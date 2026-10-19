"""YouTube Data API v3 asynchronous client using httpx.

Handles:
- OAuth2 authorization & token exchange / refresh
- Resumable video upload (supports large videos)
- Scheduled publishing (via status.publishAt)
- Video & channel statistics querying
"""

import logging
import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx

from app.integrations.youtube.errors import YouTubeApiError, YouTubeErrorKind
from app.integrations.youtube.schemas import (
    YouTubeAuthTokens,
    YouTubeChannelStats,
    YouTubePrivacyStatus,
    YouTubeVideoResponse,
    YouTubeVideoStats,
    YouTubeVideoUploadRequest,
)

logger = logging.getLogger("app.integrations.youtube")

GOOGLE_OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"  # noqa: S105
YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]


class YouTubeClient:
    """Async client for YouTube Data API v3."""

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.api_key = api_key
        self._http = httpx.AsyncClient(timeout=60.0)

    async def aclose(self) -> None:
        await self._http.aclose()

    # -------------------------------------------------------------------------
    # OAuth 2.0 Flow
    # -------------------------------------------------------------------------

    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str | None = None,
        scopes: list[str] | None = None,
    ) -> str:
        """Generate Google OAuth 2.0 authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes or YOUTUBE_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }
        if state:
            params["state"] = state
        return f"{GOOGLE_OAUTH_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> YouTubeAuthTokens:
        """Exchange authorization code for access and refresh tokens."""
        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        try:
            resp = await self._http.post(GOOGLE_OAUTH_TOKEN_URL, data=payload)
            data = resp.json()
            if resp.status_code != 200:
                raise YouTubeApiError(
                    YouTubeErrorKind.AUTH,
                    data.get("error_description", "Token exchange failed"),
                    status_code=resp.status_code,
                    details=data,
                )
            self.access_token = data.get("access_token")
            if "refresh_token" in data:
                self.refresh_token = data.get("refresh_token")
            return YouTubeAuthTokens(
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token"),
                expires_in=data.get("expires_in", 3600),
                token_type=data.get("token_type", "Bearer"),
                scope=data.get("scope"),
            )
        except httpx.HTTPError as exc:
            raise YouTubeApiError(YouTubeErrorKind.NETWORK, str(exc)) from exc

    async def refresh_token_if_needed(self) -> str:
        """Refresh access token using refresh_token."""
        if not self.refresh_token:
            if self.access_token:
                return self.access_token
            raise YouTubeApiError(
                YouTubeErrorKind.AUTH,
                "Refresh token mavjud emas. Avval Google OAuth orqali ulanish zarur.",
            )

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        try:
            resp = await self._http.post(GOOGLE_OAUTH_TOKEN_URL, data=payload)
            data = resp.json()
            if resp.status_code != 200:
                raise YouTubeApiError(
                    YouTubeErrorKind.AUTH,
                    data.get("error_description", "Token yangilashda xatolik yuz berdi"),
                    status_code=resp.status_code,
                    details=data,
                )
            self.access_token = data["access_token"]
            return self.access_token
        except httpx.HTTPError as exc:
            raise YouTubeApiError(YouTubeErrorKind.NETWORK, str(exc)) from exc

    def _auth_headers(self) -> dict[str, str]:
        if not self.access_token:
            raise YouTubeApiError(
                YouTubeErrorKind.AUTH,
                "Access token yo'q. Avval avtorizatsiyadan o'ting.",
            )
        return {"Authorization": f"Bearer {self.access_token}"}

    def _handle_api_error(self, resp: httpx.Response) -> None:
        try:
            body = resp.json()
            err = body.get("error", {})
            msg = err.get("message", resp.text)
            status_code = resp.status_code
            reasons = [e.get("reason", "") for e in err.get("errors", [])]
        except Exception:
            msg = resp.text
            status_code = resp.status_code
            reasons = []

        if status_code in (401, 403):
            if "quotaExceeded" in reasons or "rateLimitExceeded" in reasons:
                raise YouTubeApiError(YouTubeErrorKind.QUOTA_EXCEEDED, msg, status_code=status_code)
            raise YouTubeApiError(YouTubeErrorKind.AUTH, msg, status_code=status_code)
        if status_code == 404:
            raise YouTubeApiError(YouTubeErrorKind.NOT_FOUND, msg, status_code=status_code)

        raise YouTubeApiError(YouTubeErrorKind.UNKNOWN, msg, status_code=status_code)

    # -------------------------------------------------------------------------
    # Video Upload (Resumable Upload)
    # -------------------------------------------------------------------------

    async def upload_video(
        self,
        file_path: str | Path,
        metadata: YouTubeVideoUploadRequest,
    ) -> YouTubeVideoResponse:
        """Upload video file to YouTube with metadata and scheduling options.

        Uses YouTube's 2-step Resumable Upload protocol.
        """
        path = Path(file_path)
        if not path.is_file():
            raise YouTubeApiError(
                YouTubeErrorKind.INVALID_REQUEST,
                f"Video fayl topilmadi: {path}",
            )

        file_size = path.stat().st_size
        mime_type, _ = mimetypes.guess_type(path.name)
        if not mime_type or not mime_type.startswith("video/"):
            mime_type = "video/mp4"

        # Auto refresh token if needed
        if self.refresh_token:
            await self.refresh_token_if_needed()

        # Build video metadata resource
        snippet: dict[str, Any] = {
            "title": metadata.title,
            "description": metadata.description,
            "tags": metadata.tags,
            "categoryId": metadata.category_id,
        }

        status: dict[str, Any] = {
            "privacyStatus": metadata.privacy_status.value,
            "selfDeclaredMadeForKids": metadata.made_for_kids,
        }

        # Scheduled publishing logic
        if metadata.publish_at:
            # YouTube requires privacyStatus to be "private" when publishAt is set
            status["privacyStatus"] = YouTubePrivacyStatus.PRIVATE.value
            dt = metadata.publish_at
            iso_time = dt.isoformat() + ("Z" if dt.tzinfo is None else "")
            status["publishAt"] = iso_time

        request_body = {
            "snippet": snippet,
            "status": status,
        }

        # Step 1: Initiate Resumable Upload Session
        init_headers = {
            **self._auth_headers(),
            "X-Upload-Content-Type": mime_type,
            "X-Upload-Content-Length": str(file_size),
            "Content-Type": "application/json; charset=UTF-8",
        }

        init_params = {
            "part": "snippet,status",
            "uploadType": "resumable",
            "notifySubscribers": str(metadata.notify_subscribers).lower(),
        }

        logger.info(
            "YouTube resumable upload boshlandi: %s (%d bytes)",
            path.name,
            file_size,
        )

        resp = await self._http.post(
            YOUTUBE_UPLOAD_URL,
            params=init_params,
            headers=init_headers,
            json=request_body,
        )

        if resp.status_code not in (200, 201):
            self._handle_api_error(resp)

        upload_url = resp.headers.get("Location")
        if not upload_url:
            raise YouTubeApiError(
                YouTubeErrorKind.UPLOAD_FAILED,
                "YouTube yuklash sessiyasini yarata olmadi (Location header yo'q).",
                status_code=resp.status_code,
            )

        # Step 2: Upload file bytes
        upload_timeout = max(300.0, file_size / (50 * 1024))
        with open(path, "rb") as f:
            file_data = f.read()

        upload_headers = {
            "Content-Type": mime_type,
            "Content-Length": str(file_size),
        }

        upload_resp = await self._http.put(
            upload_url,
            headers=upload_headers,
            content=file_data,
            timeout=upload_timeout,
        )

        if upload_resp.status_code not in (200, 201):
            self._handle_api_error(upload_resp)

        result = upload_resp.json()
        video_id = result.get("id", "")
        ret_snippet = result.get("snippet", {})
        ret_status = result.get("status", {})

        logger.info("Video muvaffaqiyatli yuklandi: video_id=%s", video_id)

        return YouTubeVideoResponse(
            video_id=video_id,
            title=ret_snippet.get("title", metadata.title),
            description=ret_snippet.get("description", metadata.description),
            privacy_status=ret_status.get("privacyStatus", metadata.privacy_status.value),
            publish_at=metadata.publish_at,
            url=f"https://www.youtube.com/watch?v={video_id}",
        )

    # -------------------------------------------------------------------------
    # Channel and Video Analytics & Stats
    # -------------------------------------------------------------------------

    async def get_my_channel_stats(self) -> YouTubeChannelStats:
        """Fetch statistics for the authenticated user's YouTube channel."""
        if self.refresh_token:
            await self.refresh_token_if_needed()

        params = {
            "part": "snippet,statistics",
            "mine": "true",
        }
        resp = await self._http.get(
            f"{YOUTUBE_API_BASE_URL}/channels",
            params=params,
            headers=self._auth_headers(),
        )

        if resp.status_code != 200:
            self._handle_api_error(resp)

        data = resp.json()
        items = data.get("items", [])
        if not items:
            raise YouTubeApiError(
                YouTubeErrorKind.NOT_FOUND,
                "Foydalanuvchiga tegishli YouTube kanal topilmadi.",
            )

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        return YouTubeChannelStats(
            channel_id=item.get("id", ""),
            title=snippet.get("title", ""),
            description=snippet.get("description", ""),
            custom_url=snippet.get("customUrl"),
            subscriber_count=int(stats.get("subscriberCount", 0)),
            video_count=int(stats.get("videoCount", 0)),
            view_count=int(stats.get("viewCount", 0)),
        )

    async def get_video_stats(self, video_id: str) -> YouTubeVideoStats:
        """Fetch statistics and details for a specific video."""
        if self.refresh_token:
            await self.refresh_token_if_needed()

        params = {
            "part": "snippet,statistics,status",
            "id": video_id,
        }
        resp = await self._http.get(
            f"{YOUTUBE_API_BASE_URL}/videos",
            params=params,
            headers=self._auth_headers(),
        )

        if resp.status_code != 200:
            self._handle_api_error(resp)

        data = resp.json()
        items = data.get("items", [])
        if not items:
            raise YouTubeApiError(
                YouTubeErrorKind.NOT_FOUND,
                f"Video topilmadi: {video_id}",
            )

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        status = item.get("status", {})

        return YouTubeVideoStats(
            video_id=video_id,
            title=snippet.get("title", ""),
            view_count=int(stats.get("viewCount", 0)),
            like_count=int(stats.get("likeCount", 0)),
            comment_count=int(stats.get("commentCount", 0)),
            published_at=snippet.get("publishedAt"),
            privacy_status=status.get("privacyStatus", "public"),
        )

    async def list_channel_videos(self, max_results: int = 10) -> list[YouTubeVideoStats]:
        """Fetch latest videos of the channel."""
        if self.refresh_token:
            await self.refresh_token_if_needed()

        channel_resp = await self._http.get(
            f"{YOUTUBE_API_BASE_URL}/channels",
            params={"part": "contentDetails", "mine": "true"},
            headers=self._auth_headers(),
        )
        if channel_resp.status_code != 200:
            self._handle_api_error(channel_resp)

        ch_data = channel_resp.json()
        items = ch_data.get("items", [])
        if not items:
            return []

        uploads_id = (
            items[0]
            .get("contentDetails", {})
            .get("relatedPlaylists", {})
            .get("uploads")
        )
        if not uploads_id:
            return []

        pl_resp = await self._http.get(
            f"{YOUTUBE_API_BASE_URL}/playlistItems",
            params={
                "part": "snippet,contentDetails",
                "playlistId": uploads_id,
                "maxResults": min(max_results, 50),
            },
            headers=self._auth_headers(),
        )
        if pl_resp.status_code != 200:
            self._handle_api_error(pl_resp)

        pl_items = pl_resp.json().get("items", [])
        video_ids = [
            it.get("contentDetails", {}).get("videoId")
            for it in pl_items
            if it.get("contentDetails", {}).get("videoId")
        ]

        if not video_ids:
            return []

        v_resp = await self._http.get(
            f"{YOUTUBE_API_BASE_URL}/videos",
            params={"part": "snippet,statistics,status", "id": ",".join(video_ids)},
            headers=self._auth_headers(),
        )
        if v_resp.status_code != 200:
            self._handle_api_error(v_resp)

        out: list[YouTubeVideoStats] = []
        for v in v_resp.json().get("items", []):
            snippet = v.get("snippet", {})
            stats = v.get("statistics", {})
            status = v.get("status", {})
            out.append(
                YouTubeVideoStats(
                    video_id=v.get("id", ""),
                    title=snippet.get("title", ""),
                    view_count=int(stats.get("viewCount", 0)),
                    like_count=int(stats.get("likeCount", 0)),
                    comment_count=int(stats.get("commentCount", 0)),
                    published_at=snippet.get("publishedAt"),
                    privacy_status=status.get("privacyStatus", "public"),
                )
            )
        return out
