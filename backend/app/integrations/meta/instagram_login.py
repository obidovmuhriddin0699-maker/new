"""HTTP client for the Instagram API with Instagram Login (Business Login for Instagram).

Verified against Meta's documentation (October 2026):
* authorize:   {META_OAUTH_AUTHORIZE_URL}?client_id&redirect_uri&response_type=code&scope&state
* code -> short-lived token: POST {META_OAUTH_TOKEN_URL} (form: client_id, client_secret,
  grant_type=authorization_code, redirect_uri, code). Response: {"data": [{"access_token",
  "user_id", "permissions"}]} — a flat object is also accepted defensively.
* short -> long-lived (60 days): GET {graph}/access_token?grant_type=ig_exchange_token
* refresh (token >= 24 h old, not expired; +60 days): GET {graph}/refresh_access_token
  ?grant_type=ig_refresh_token
* profile: GET {graph}/{version}/me?fields=user_id,username,account_type,...
  ``user_id`` is the Instagram professional account id; ``id`` is app-scoped.

Never logs tokens: httpx loggers are capped at WARNING and token parameters are redacted
(app.core.logging.install_secret_filters).
"""

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import Settings, get_settings
from app.integrations.meta.errors import MetaApiError, MetaErrorKind, from_response

PROFILE_FIELDS = "user_id,username,account_type,name,profile_picture_url"


@dataclass(slots=True)
class ShortLivedToken:
    access_token: str
    user_id: str | None
    permissions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class LongLivedToken:
    access_token: str
    expires_in: int
    token_type: str | None = None


@dataclass(slots=True)
class MetaProfile:
    ig_user_id: str
    app_scoped_id: str | None
    username: str | None
    account_type: str | None
    name: str | None = None
    profile_picture_url: str | None = None


def strip_code(code: str) -> str:
    """Meta appends '#_' to the redirect; it is not part of the code."""
    code = code.strip()
    return code[:-2] if code.endswith("#_") else code


class InstagramLoginClient:
    def __init__(
        self, settings: Settings | None = None, client: httpx.AsyncClient | None = None
    ) -> None:
        self.settings = settings or get_settings()
        self._client = client or httpx.AsyncClient(timeout=self.settings.meta_http_timeout_seconds)

    async def aclose(self) -> None:
        await self._client.aclose()

    # ------------------------------------------------------------------ OAuth
    def authorize_url(self, state: str) -> str:
        s = self.settings
        if not s.meta_configured:
            raise MetaApiError(MetaErrorKind.NOT_CONFIGURED)
        query = urlencode(
            {
                "client_id": s.meta_app_id,
                "redirect_uri": s.meta_redirect_uri,
                "response_type": "code",
                "scope": ",".join(s.meta_scopes),
                "state": state,
            }
        )
        return f"{s.meta_oauth_authorize_url}?{query}"

    async def exchange_code(self, code: str) -> ShortLivedToken:
        s = self.settings
        data = await self._request(
            "POST",
            s.meta_oauth_token_url,
            data={
                "client_id": s.meta_app_id,
                "client_secret": s.meta_app_secret.get_secret_value(),
                "grant_type": "authorization_code",
                "redirect_uri": s.meta_redirect_uri,
                "code": strip_code(code),
            },
        )
        entry = data["data"][0] if isinstance(data.get("data"), list) and data["data"] else data
        token = entry.get("access_token")
        if not isinstance(token, str) or not token:
            raise MetaApiError(MetaErrorKind.OAUTH, meta_message="no access_token in response")
        perms = entry.get("permissions") or []
        if isinstance(perms, str):
            perms = [p.strip() for p in perms.split(",") if p.strip()]
        user_id = entry.get("user_id")
        return ShortLivedToken(
            token, str(user_id) if user_id is not None else None, [str(p) for p in perms]
        )

    async def exchange_long_lived(self, short_token: str) -> LongLivedToken:
        s = self.settings
        data = await self._request(
            "GET",
            f"{s.meta_graph_base_url}/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": s.meta_app_secret.get_secret_value(),
                "access_token": short_token,
            },
        )
        return self._long_lived(data)

    async def refresh(self, long_token: str) -> LongLivedToken:
        s = self.settings
        data = await self._request(
            "GET",
            f"{s.meta_graph_base_url}/refresh_access_token",
            params={"grant_type": "ig_refresh_token", "access_token": long_token},
        )
        return self._long_lived(data)

    async def get_me(self, token: str) -> MetaProfile:
        s = self.settings
        data = await self._request(
            "GET",
            f"{s.meta_graph_base_url}/{s.meta_graph_api_version}/me",
            params={"fields": PROFILE_FIELDS, "access_token": token},
        )
        ig_user_id = data.get("user_id") or data.get("id")
        if not ig_user_id:
            raise MetaApiError(MetaErrorKind.UNKNOWN, meta_message="profile without user_id")
        return MetaProfile(
            ig_user_id=str(ig_user_id),
            app_scoped_id=str(data["id"]) if data.get("id") is not None else None,
            username=data.get("username"),
            account_type=data.get("account_type"),
            name=data.get("name"),
            profile_picture_url=data.get("profile_picture_url"),
        )

    # ------------------------------------------------------------------ internals
    @staticmethod
    def _long_lived(data: dict[str, Any]) -> LongLivedToken:
        token = data.get("access_token")
        if not isinstance(token, str) or not token:
            raise MetaApiError(MetaErrorKind.OAUTH, meta_message="no access_token in response")
        try:
            expires_in = int(data.get("expires_in") or 0)
        except (TypeError, ValueError):
            expires_in = 0
        return LongLivedToken(token, expires_in, data.get("token_type"))

    async def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        try:
            resp = await self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as exc:
            raise MetaApiError(MetaErrorKind.NETWORK, meta_message="timeout") from exc
        except httpx.HTTPError as exc:
            raise MetaApiError(MetaErrorKind.NETWORK, meta_message=type(exc).__name__) from exc
        try:
            body = resp.json()
        except ValueError:
            body = None
        if (
            resp.status_code >= 400
            or not isinstance(body, dict)
            or "error" in body
            or "error_type" in body
        ):
            raise from_response(resp.status_code, body)
        return body
