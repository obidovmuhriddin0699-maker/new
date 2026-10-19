"""YouTube Data API and AI Agent endpoints."""

import os
import shutil
import tempfile
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from app.agents.youtube import YouTubeAgent, YouTubeMetadataOutput, YouTubeShortsScriptOutput
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.integrations.youtube.client import YouTubeClient
from app.integrations.youtube.errors import YouTubeApiError
from app.integrations.youtube.schemas import (
    YouTubeCategory,
    YouTubeChannelStats,
    YouTubePrivacyStatus,
    YouTubeVideoResponse,
    YouTubeVideoStats,
    YouTubeVideoUploadRequest,
)
from app.models import BrandProfile, User
from app.providers.ai.factory import create_ai_provider

router = APIRouter(prefix="/youtube", tags=["youtube"])


class OAuthCallbackRequest(BaseModel):
    code: str
    redirect_uri: str | None = None


class MetadataGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, description="Video mavzusi")
    video_summary: str | None = Field(default=None, description="Video haqida qisqacha ma'lumot")
    target_audience: str | None = Field(default=None, description="Maqsadli auditoriya")
    language: str = Field(default="uz", description="Til: uz, ru, en")


class ShortsScriptGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, description="Shorts mavzusi")
    target_seconds: int = Field(default=45, ge=15, le=60, description="Davomiyligi (soniya)")
    language: str = Field(default="uz", description="Til: uz, ru, en")


def _get_youtube_client(
    access_token: str | None = None,
    refresh_token: str | None = None,
) -> YouTubeClient:
    settings = get_settings()
    return YouTubeClient(
        client_id=settings.youtube_client_id,
        client_secret=settings.youtube_client_secret.get_secret_value(),
        access_token=access_token,
        refresh_token=refresh_token,
        api_key=settings.youtube_api_key or None,
    )


# -----------------------------------------------------------------------------
# OAuth Endpoints
# -----------------------------------------------------------------------------

@router.get("/oauth/url")
def get_oauth_url(
    redirect_uri: str | None = None,
    state: str | None = None,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Generate Google OAuth 2.0 URL to connect YouTube channel."""
    settings = get_settings()
    eff_redirect_uri = redirect_uri or settings.youtube_redirect_uri
    if not settings.youtube_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="YOUTUBE_CLIENT_ID .env faylida sozlanmagan.",
        )
    client = _get_youtube_client()
    url = client.get_authorization_url(redirect_uri=eff_redirect_uri, state=state)
    return {"authorization_url": url, "redirect_uri": eff_redirect_uri}


@router.post("/oauth/callback")
async def exchange_oauth_code(
    payload: OAuthCallbackRequest,
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    """Exchange OAuth code for tokens."""
    settings = get_settings()
    eff_redirect_uri = payload.redirect_uri or settings.youtube_redirect_uri
    client = _get_youtube_client()
    try:
        tokens = await client.exchange_code(payload.code, redirect_uri=eff_redirect_uri)
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in,
            "token_type": tokens.token_type,
        }
    except YouTubeApiError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    finally:
        await client.aclose()


# -----------------------------------------------------------------------------
# Channel & Video Analytics
# -----------------------------------------------------------------------------

@router.get("/channel", response_model=YouTubeChannelStats)
async def get_my_channel(
    access_token: str = Query(..., description="OAuth access token"),
    refresh_token: str | None = Query(None, description="OAuth refresh token"),
    current_user: User = Depends(get_current_user),
) -> YouTubeChannelStats:
    """Get authenticated user's YouTube channel stats."""
    client = _get_youtube_client(access_token=access_token, refresh_token=refresh_token)
    try:
        return await client.get_my_channel_stats()
    except YouTubeApiError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc
    finally:
        await client.aclose()


@router.get("/videos", response_model=list[YouTubeVideoStats])
async def list_channel_videos(
    access_token: str = Query(...),
    refresh_token: str | None = Query(None),
    max_results: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
) -> list[YouTubeVideoStats]:
    """List recent videos with views, likes, and comment counts."""
    client = _get_youtube_client(access_token=access_token, refresh_token=refresh_token)
    try:
        return await client.list_channel_videos(max_results=max_results)
    except YouTubeApiError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc
    finally:
        await client.aclose()


@router.get("/videos/{video_id}", response_model=YouTubeVideoStats)
async def get_video(
    video_id: str,
    access_token: str = Query(...),
    refresh_token: str | None = Query(None),
    current_user: User = Depends(get_current_user),
) -> YouTubeVideoStats:
    """Get metrics and stats for a specific YouTube video."""
    client = _get_youtube_client(access_token=access_token, refresh_token=refresh_token)
    try:
        return await client.get_video_stats(video_id)
    except YouTubeApiError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc
    finally:
        await client.aclose()


# -----------------------------------------------------------------------------
# Video Upload & Scheduling
# -----------------------------------------------------------------------------

@router.post("/upload", response_model=YouTubeVideoResponse)
async def upload_video(
    file: UploadFile = File(..., description="Video fayl"),
    title: str = Form(..., max_length=100),
    description: str = Form(""),
    tags: str = Form("", description="Vergul bilan ajratilgan teglar"),
    category_id: str = Form(YouTubeCategory.PEOPLE_BLOGS),
    privacy_status: YouTubePrivacyStatus = Form(YouTubePrivacyStatus.PRIVATE),
    publish_at: datetime | None = Form(None, description="Rejalashtirilgan nashr vaqti"),
    access_token: str = Form(...),
    refresh_token: str | None = Form(None),
    current_user: User = Depends(get_current_user),
) -> YouTubeVideoResponse:
    """Upload video to YouTube and optionally schedule it for future publishing."""
    client = _get_youtube_client(access_token=access_token, refresh_token=refresh_token)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    req = YouTubeVideoUploadRequest(
        title=title,
        description=description,
        tags=tag_list,
        category_id=category_id,
        privacy_status=privacy_status,
        publish_at=publish_at,
    )

    suffix = ".mp4"
    if file.filename and "." in file.filename:
        suffix = "." + file.filename.rsplit(".", 1)[-1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name
        shutil.copyfileobj(file.file, tmp)

    try:
        return await client.upload_video(tmp_path, req)
    except YouTubeApiError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        await client.aclose()


# -----------------------------------------------------------------------------
# AI Agent Endpoints (Title, Description, Tags, Shorts Script)
# -----------------------------------------------------------------------------

@router.post("/ai/metadata", response_model=YouTubeMetadataOutput)
async def generate_youtube_metadata(
    payload: MetadataGenerationRequest,
    current_user: User = Depends(get_current_user),
) -> YouTubeMetadataOutput:
    """Generate high CTR titles, SEO description, tags and thumbnail idea using AI."""
    ai_provider = create_ai_provider()
    agent = YouTubeAgent(ai_provider)

    mock_brand = BrandProfile(
        name="YouTube Channel",
        niche="Content Creation",
        voice=["Samimiy", "Ekspert", "Qiziqarli"],
        topics=["Texnologiya", "Foydali"],
        languages=[payload.language],
        target_audience=payload.target_audience or "O'zbek tilida sifatli kontent izlovchilar",
        preferred_ctas=["Kanalga obuna bo'ling!"],
    )

    output, _ = await agent.generate_metadata(
        mock_brand,
        language=payload.language,
        topic=payload.topic,
        video_summary=payload.video_summary,
        target_audience=payload.target_audience,
    )
    return output


@router.post("/ai/shorts-script", response_model=YouTubeShortsScriptOutput)
async def generate_shorts_script(
    payload: ShortsScriptGenerationRequest,
    current_user: User = Depends(get_current_user),
) -> YouTubeShortsScriptOutput:
    """Generate viral YouTube Shorts script with 3-second hook and visual cues."""
    ai_provider = create_ai_provider()
    agent = YouTubeAgent(ai_provider)

    mock_brand = BrandProfile(
        name="YouTube Shorts",
        niche="Short Content",
        voice=["Dinamik", "Qiziqarli", "Tezkor"],
        topics=["Shorts"],
        languages=[payload.language],
        target_audience="Shorts tomoshabinlari",
    )

    output, _ = await agent.generate_shorts_script(
        mock_brand,
        language=payload.language,
        topic=payload.topic,
        target_seconds=payload.target_seconds,
    )
    return output
