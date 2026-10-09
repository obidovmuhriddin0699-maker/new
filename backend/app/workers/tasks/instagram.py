"""Periodic maintenance for Instagram tokens."""

from app.core.database import get_sessionmaker
from app.services.instagram_oauth import InstagramOAuthService
from app.workers.celery_app import celery_app


@celery_app.task(name="instagram.refresh_tokens")
def refresh_instagram_tokens() -> dict[str, int]:
    """Refresh long-lived tokens that are close to expiry (Meta: >= 24 h old, not expired)."""
    with get_sessionmaker()() as session:
        return InstagramOAuthService(session).refresh_due()
