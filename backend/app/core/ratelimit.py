"""Rate limiting (fixed window) with Redis, falling back to process memory.

* ``redis``: shared by all API workers and the Celery worker. Required in production.
* ``memory``: per-process counters, used in tests and when Redis is down in development.
  If Redis stops answering, the limiter switches to memory for 30 seconds instead of
  failing open, then tries Redis again.

Keys never contain secrets: e-mails and IPs are hashed before they reach Redis or logs.
"""

import hashlib
import logging
import threading
import time
from dataclasses import dataclass
from ipaddress import ip_address, ip_network

from fastapi import Request

from app.core.config import get_settings
from app.core.errors import TooManyRequestsError

logger = logging.getLogger(__name__)
_REDIS_RETRY_SECONDS = 30.0


@dataclass(frozen=True, slots=True)
class Limit:
    name: str
    limit: int
    window_seconds: int
    message: str = "Juda ko‘p so‘rov. Biroz kuting va qayta urinib ko‘ring."


# Central policy. Tuned for a small admin team; adjust here, not in endpoints.
LOGIN_IP = Limit("login-ip", 30, 300)
LOGIN_FAILURES = Limit(
    "login-fail", 10, 900, "Juda ko‘p noto‘g‘ri urinish. 15 daqiqadan keyin qayta urinib ko‘ring."
)
AI_GENERATE = Limit(
    "ai", 60, 3600, "AI so‘rovlari soati chegarasiga yetdi. Keyinroq urinib ko‘ring."
)
PUBLISH = Limit("publish", 30, 3600)
UPLOAD = Limit("upload", 60, 3600)
ANALYTICS_SYNC = Limit(
    "analytics-sync", 6, 3600, "Statistika soatiga 6 marta yangilanadi (Meta limitini tejash)."
)
REPORT = Limit("report", 10, 3600)
OAUTH_START = Limit("oauth-start", 10, 600)
META_CALLBACK = Limit("meta-callback", 60, 60)
TELEGRAM_CODE = Limit("telegram-code", 10, 3600)
TELEGRAM_LINK_ATTEMPT = Limit(
    "telegram-link", 5, 900, "Juda ko‘p noto‘g‘ri kod. 15 daqiqadan keyin qayta urinib ko‘ring."
)
API_IP = Limit("api-ip", 600, 60)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:24]


class RateLimiter:
    def __init__(self, backend: str | None = None) -> None:
        self.backend = backend or get_settings().rate_limit_backend
        self._lock = threading.Lock()
        self._memory: dict[str, tuple[int, float]] = {}
        self._redis_down_until = 0.0
        self._redis = None

    # ------------------------------------------------------------------ core
    def hit(self, limit: Limit, key: str, cost: int = 1) -> tuple[bool, int]:
        """Count one event. Returns (allowed, retry_after_seconds)."""
        if not get_settings().rate_limit_enabled:
            return True, 0
        bucket = f"rl:{limit.name}:{_digest(key)}"
        count, ttl = self._incr(bucket, limit.window_seconds, cost)
        return count <= limit.limit, max(ttl, 1)

    def peek(self, limit: Limit, key: str) -> tuple[bool, int]:
        """Check without counting (used to refuse before doing work)."""
        if not get_settings().rate_limit_enabled:
            return True, 0
        bucket = f"rl:{limit.name}:{_digest(key)}"
        count, ttl = self._incr(bucket, limit.window_seconds, 0)
        return count < limit.limit, max(ttl, 1)

    def check(self, limit: Limit, key: str) -> None:
        allowed, retry = self.hit(limit, key)
        if not allowed:
            raise RateLimitedError(limit.message, retry)

    def reset(self, limit: Limit, key: str) -> None:
        bucket = f"rl:{limit.name}:{_digest(key)}"
        with self._lock:
            self._memory.pop(bucket, None)
        client = self._client()
        if client is not None:
            try:
                client.delete(bucket)
            except Exception:  # noqa: BLE001
                self._mark_redis_down()

    def clear(self) -> None:
        with self._lock:
            self._memory.clear()

    # ------------------------------------------------------------------ backends
    def _incr(self, bucket: str, window: int, cost: int) -> tuple[int, int]:
        client = self._client()
        if client is not None:
            try:
                pipe = client.pipeline()
                pipe.set(bucket, 0, ex=window, nx=True)  # starts the window once
                pipe.incrby(bucket, cost)
                pipe.ttl(bucket)
                _, count, ttl = pipe.execute()
                return int(count), int(ttl if ttl and ttl > 0 else window)
            except Exception:  # noqa: BLE001 - never fail open on a Redis outage
                self._mark_redis_down()
        now = time.monotonic()
        with self._lock:
            count, reset_at = self._memory.get(bucket, (0, now + window))
            if reset_at <= now:
                count, reset_at = 0, now + window
            count += cost
            self._memory[bucket] = (count, reset_at)
            if len(self._memory) > 50_000:  # bound memory: drop expired buckets
                self._memory = {k: v for k, v in self._memory.items() if v[1] > now}
            return count, int(reset_at - now)

    def _client(self):  # type: ignore[no-untyped-def]
        if self.backend == "memory" or time.monotonic() < self._redis_down_until:
            return None
        if self._redis is None:
            from app.core.redis import get_redis

            self._redis = get_redis()
        return self._redis

    def _mark_redis_down(self) -> None:
        if time.monotonic() >= self._redis_down_until:
            logger.warning("rate_limit_redis_unavailable_using_memory")
        self._redis_down_until = time.monotonic() + _REDIS_RETRY_SECONDS


class RateLimitedError(TooManyRequestsError):
    code = "rate_limited"

    def __init__(self, message: str, retry_after: int) -> None:
        super().__init__(message, details={"retry_after_seconds": retry_after})
        self.retry_after = retry_after


_limiter: RateLimiter | None = None


def get_limiter() -> RateLimiter:
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter


def reset_limiter() -> None:
    global _limiter
    _limiter = None


# ------------------------------------------------------------------ client IP
def client_ip(request: Request) -> str:
    """Socket address, or the forwarded client address when the socket peer is a
    trusted proxy (the Next.js server / a reverse proxy in front of it)."""
    peer = request.client.host if request.client else "unknown"
    if not _trusted(peer):
        return peer
    forwarded = request.headers.get("x-forwarded-for", "")
    # Right-most address that is not one of our proxies = the real client.
    for candidate in reversed([p.strip() for p in forwarded.split(",") if p.strip()]):
        if not _trusted(candidate):
            return candidate[:64]
    return peer


def _trusted(host: str) -> bool:
    try:
        addr = ip_address(host)
    except ValueError:
        return False
    for net in get_settings().trusted_proxies:
        try:
            if addr in ip_network(net, strict=False):
                return True
        except ValueError:
            continue
    return False
