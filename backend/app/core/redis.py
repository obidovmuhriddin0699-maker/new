"""Redis client factory. Redis is optional in development; health reports its state."""

import redis

from app.core.config import get_settings


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(
        get_settings().redis_url, socket_connect_timeout=1, socket_timeout=1
    )


def check_redis() -> tuple[bool, str | None]:
    try:
        client = get_redis()
        client.ping()
        client.close()
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, type(exc).__name__
