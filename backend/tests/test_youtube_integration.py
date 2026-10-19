"""Tests for YouTube Data API integration and YouTube Agent."""

import pytest
import respx
import httpx

from app.integrations.youtube.client import YouTubeClient, GOOGLE_OAUTH_TOKEN_URL, YOUTUBE_API_BASE_URL
from app.integrations.youtube.schemas import (
    YouTubeCategory,
    YouTubePrivacyStatus,
    YouTubeVideoUploadRequest,
)
from app.agents.youtube import YouTubeAgent
from app.models import BrandProfile
from app.providers.ai.mock import MockAIProvider


@pytest.mark.asyncio
async def test_youtube_auth_url_generation():
    client = YouTubeClient(
        client_id="test_client_id",
        client_secret="test_secret",
    )
    url = client.get_authorization_url(redirect_uri="http://localhost:8000/callback", state="xyz")
    assert "accounts.google.com" in url
    assert "client_id=test_client_id" in url
    assert "state=xyz" in url
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_youtube_token_exchange():
    respx.post(GOOGLE_OAUTH_TOKEN_URL).respond(
        status_code=200,
        json={
            "access_token": "ya29.test_access_token",
            "refresh_token": "1//test_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        },
    )

    client = YouTubeClient(
        client_id="test_id",
        client_secret="test_secret",
    )
    tokens = await client.exchange_code("auth_code_123", redirect_uri="http://localhost:8000/callback")
    assert tokens.access_token == "ya29.test_access_token"
    assert tokens.refresh_token == "1//test_refresh_token"
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_youtube_channel_stats():
    respx.get(f"{YOUTUBE_API_BASE_URL}/channels").respond(
        status_code=200,
        json={
            "items": [
                {
                    "id": "UC1234567890",
                    "snippet": {
                        "title": "Muxriddin Dev",
                        "description": "Dasturlash va IT kanali",
                        "customUrl": "@muxriddin_dev",
                    },
                    "statistics": {
                        "subscriberCount": "15400",
                        "videoCount": "84",
                        "viewCount": "950200",
                    },
                }
            ]
        },
    )

    client = YouTubeClient(
        client_id="test_id",
        client_secret="test_secret",
        access_token="test_token",
    )
    stats = await client.get_my_channel_stats()
    assert stats.channel_id == "UC1234567890"
    assert stats.title == "Muxriddin Dev"
    assert stats.subscriber_count == 15400
    assert stats.video_count == 84
    assert stats.view_count == 950200
    await client.aclose()


@pytest.mark.asyncio
async def test_youtube_agent_mock(brand):
    mock_provider = MockAIProvider()
    agent = YouTubeAgent(mock_provider)

    meta, info = await agent.generate_metadata(
        brand,
        language="uz",
        topic="Python Dasturlash",
    )
    assert len(meta.titles) >= 1
    assert meta.description != ""
