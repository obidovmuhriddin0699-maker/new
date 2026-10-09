"""Minimal fake of the Instagram Login + Content Publishing endpoints — E2E tests only.

Never used by the application itself. Run: uvicorn tests.fake_meta:app --port 8200
It mirrors the documented request/response shapes (data[] on code exchange,
'#_' appended to the redirect, ig_exchange_token / ig_refresh_token, /vXX/me).
"""

import itertools
import secrets
from urllib.parse import urlencode

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse

APP_ID = "e2e-app-id"
APP_SECRET = "e2e-app-secret"  # noqa: S105 - fake test credential
IG_USER_ID = "17841400000000001"

app = FastAPI(title="fake-meta")
_codes: dict[str, str] = {}
_tokens: set[str] = set()
_ids = itertools.count(5000)
_containers: dict[str, dict] = {}  # id -> {"params", "status", "media_id"}
_media: dict[str, dict] = {}


@app.get("/oauth/authorize")
def authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str,
    scope: str,
    state: str,
    deny: bool = False,
) -> RedirectResponse:
    if client_id != APP_ID or response_type != "code":
        raise HTTPException(400, "bad client")
    if deny:
        q = urlencode(
            {
                "error": "access_denied",
                "error_reason": "user_denied",
                "error_description": "The user denied your request.",
                "state": state,
            }
        )
        return RedirectResponse(f"{redirect_uri}?{q}", status_code=302)
    code = secrets.token_urlsafe(12)
    _codes[code] = redirect_uri
    return RedirectResponse(
        f"{redirect_uri}?{urlencode({'code': code, 'state': state})}#_", status_code=302
    )


@app.post("/oauth/access_token")
def access_token(
    client_id: str = Form(),
    client_secret: str = Form(),
    grant_type: str = Form(),
    redirect_uri: str = Form(),
    code: str = Form(),
) -> JSONResponse:
    if (
        client_id != APP_ID
        or client_secret != APP_SECRET
        or grant_type != "authorization_code"
        or _codes.pop(code, None) != redirect_uri
    ):
        return JSONResponse(
            {
                "error_type": "OAuthException",
                "code": 400,
                "error_message": "Invalid authorization code",
            },
            status_code=400,
        )
    token = "short-" + secrets.token_urlsafe(8)
    _tokens.add(token)
    return JSONResponse(
        {
            "data": [
                {
                    "access_token": token,
                    "user_id": IG_USER_ID,
                    "permissions": "instagram_business_basic,instagram_business_content_publish,"
                    "instagram_business_manage_insights",
                }
            ]
        }
    )


@app.get("/access_token")
def exchange(grant_type: str, client_secret: str, access_token: str) -> JSONResponse:
    if (
        grant_type != "ig_exchange_token"
        or client_secret != APP_SECRET
        or access_token not in _tokens
    ):
        return JSONResponse(
            {
                "error": {
                    "message": "Invalid OAuth access token",
                    "type": "OAuthException",
                    "code": 190,
                }
            },
            status_code=400,
        )
    token = "long-" + secrets.token_urlsafe(8)
    _tokens.add(token)
    return JSONResponse({"access_token": token, "token_type": "bearer", "expires_in": 5184000})


@app.get("/refresh_access_token")
def refresh(grant_type: str, access_token: str) -> JSONResponse:
    if grant_type != "ig_refresh_token" or access_token not in _tokens:
        return JSONResponse(
            {
                "error": {
                    "message": "Invalid OAuth access token",
                    "type": "OAuthException",
                    "code": 190,
                }
            },
            status_code=400,
        )
    token = "long-" + secrets.token_urlsafe(8)
    _tokens.add(token)
    return JSONResponse({"access_token": token, "token_type": "bearer", "expires_in": 5184000})


@app.get("/{version}/me")
def me(version: str, fields: str = Query(""), access_token: str = Query("")) -> JSONResponse:
    if access_token not in _tokens:
        return JSONResponse(
            {
                "error": {
                    "message": "Invalid OAuth access token",
                    "type": "OAuthException",
                    "code": 190,
                }
            },
            status_code=400,
        )
    return JSONResponse(
        {
            "user_id": IG_USER_ID,
            "id": "app-scoped-1",
            "username": "muxriddin.design.e2e",
            "account_type": "BUSINESS",
        }
    )


# ------------------------------------------------------------------ content publishing
def _bad_token() -> JSONResponse:
    return JSONResponse(
        {"error": {"message": "Invalid OAuth access token", "type": "OAuthException", "code": 190}},
        status_code=400,
    )


@app.post("/{version}/{ig_user_id}/media")
async def create_container(version: str, ig_user_id: str, request: Request) -> JSONResponse:
    form = dict(await request.form())
    if form.pop("access_token", None) not in _tokens or ig_user_id != IG_USER_ID:
        return _bad_token()
    cid = str(next(_ids))
    _containers[cid] = {"params": form, "status": "FINISHED", "media_id": None}
    return JSONResponse({"id": cid})


@app.post("/{version}/{ig_user_id}/media_publish")
async def media_publish(version: str, ig_user_id: str, request: Request) -> JSONResponse:
    form = dict(await request.form())
    if form.get("access_token") not in _tokens:
        return _bad_token()
    container = _containers.get(str(form.get("creation_id")))
    if container is None or container["media_id"]:
        return JSONResponse(
            {"error": {"message": "Invalid creation_id", "code": 9004, "error_subcode": 2207008}},
            status_code=400,
        )
    mid = f"1791{next(_ids)}"
    container["media_id"] = mid
    container["status"] = "PUBLISHED"
    _media[mid] = {"caption": container["params"].get("caption", "")}
    return JSONResponse({"id": mid})


@app.get("/{version}/{ig_user_id}/content_publishing_limit")
def publishing_limit(version: str, ig_user_id: str, access_token: str = "") -> JSONResponse:
    if access_token not in _tokens:
        return _bad_token()
    used = len(_media)
    return JSONResponse(
        {"data": [{"quota_usage": used, "config": {"quota_total": 100, "quota_duration": 86400}}]}
    )


@app.get("/{version}/{object_id}")
def read_object(version: str, object_id: str, access_token: str = "") -> JSONResponse:
    if access_token not in _tokens:
        return _bad_token()
    if object_id in _containers:
        return JSONResponse({"id": object_id, "status_code": _containers[object_id]["status"]})
    if object_id in _media:
        return JSONResponse(
            {"id": object_id, "permalink": f"https://www.instagram.com/p/E2E{object_id}/"}
        )
    return JSONResponse({"error": {"message": "Unknown object", "code": 100}}, status_code=400)
