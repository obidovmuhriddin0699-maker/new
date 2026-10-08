"""Development seed data (idempotent).

Creates: an owner user, the "Muxriddin Design" brand profile, one example
draft carousel with asset *metadata* (no real files) and default system
settings. It never creates Instagram accounts or OAuth tokens.

The admin password comes from ``SEED_ADMIN_PASSWORD`` if set; otherwise a
random one is generated and printed once. Nothing is hard-coded.
"""

import os
import secrets
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.actors import HumanActor, SystemActor
from app.core.config import get_settings
from app.core.security import hash_password, normalize_login_email
from app.core.transaction import atomic
from app.models import BrandProfile, Content, User
from app.models.enums import AssetKind, AuditAction, ContentLanguage, ContentType, UserRole
from app.repositories import (
    BrandProfileRepository,
    ContentRepository,
    SystemSettingRepository,
    UserRepository,
)
from app.services.audit import AuditLogService
from app.services.content import AssetInput, ContentService

DEFAULT_ADMIN_EMAIL = "admin@example.com"
SEED_TOPIC = "[seed] Minimalist yotoqxona: 5 ta asosiy qoida"

BRAND = {
    "name": "Muxriddin Design",
    "niche": "Interior design",
    "voice": ["Premium", "Minimal", "Professional", "Modern", "Expert", "Trustworthy"],
    "topics": [
        "Minimalism",
        "Neo Classic",
        "Modern Interior",
        "Luxury Interior",
        "3D Visualization",
        "Corona Renderer",
        "3ds Max",
        "Lighting",
        "Materials",
        "Marble",
        "Wood",
        "Furniture",
        "Interior Planning",
        "Design Mistakes",
        "Before/After",
        "Client Education",
    ],
    "forbidden_rules": [
        "Clickbait ishlatma",
        "Uydirma statistika yozma",
        "Soxta mijoz fikrlari yaratma",
        "Soxta portfolio yaratma",
        "'100% kafolat' kabi asossiz va'dalar berma",
    ],
    "languages": ["uz", "ru", "en"],
    "visual_style": (
        "Premium minimalist interiors, natural light, warm beige palette, natural marble "
        "and wood, hidden LED lighting, photorealistic architectural visualization"
    ),
}

DEFAULT_SETTINGS = {
    "content.default_language": ("uz", "Default content language"),
    "content.weekly_plan": (
        {
            "MONDAY": "CAROUSEL",
            "TUESDAY": "STORY",
            "WEDNESDAY": "REELS",
            "THURSDAY": "POST",
            "FRIDAY": "REELS",
            "SATURDAY": "STORY",
            "SUNDAY": "POST",
        },
        "Default weekly content mix (adjusted later by analytics)",
    ),
    "media.aspect_ratios": (
        {
            "POST": ["4:5", "1:1", "16:9"],
            "CAROUSEL": ["4:5", "1:1"],
            "REELS": ["9:16"],
            "STORY": ["9:16"],
        },
        "Allowed aspect ratios per content type",
    ),
}


@dataclass(slots=True)
class SeedResult:
    admin_email: str
    admin_created: bool
    generated_password: str | None
    brand_profile_id: int
    content_id: int
    content_created: bool


def run_seed(session: Session, *, admin_email: str | None = None) -> SeedResult:
    if get_settings().app_env == "production":
        raise RuntimeError("Development seed must not run in production")

    email = normalize_login_email(
        admin_email or os.getenv("SEED_ADMIN_EMAIL") or DEFAULT_ADMIN_EMAIL
    )
    generated: str | None = None
    system = SystemActor("seed")
    audit = AuditLogService(session)

    with atomic(session):
        users = UserRepository(session)
        admin = users.get_by_email(email)
        admin_created = admin is None
        if admin is None:
            password = os.getenv("SEED_ADMIN_PASSWORD")
            if not password:
                password = generated = secrets.token_urlsafe(18)
            if len(password) < 12:
                raise ValueError("SEED_ADMIN_PASSWORD must be at least 12 characters")
            admin = users.add(
                User(
                    email=email,
                    password_hash=hash_password(password),
                    full_name="Development Admin",
                    role=UserRole.OWNER,
                )
            )

        brands = BrandProfileRepository(session)
        brand = brands.get_by_name(BRAND["name"])
        if brand is None:
            brand = brands.add(BrandProfile(**BRAND, is_default=True))

        settings_repo = SystemSettingRepository(session)
        for key, (value, description) in DEFAULT_SETTINGS.items():
            if settings_repo.get(key) is None:
                settings_repo.set_value(key, value, description)

        content = _find_seed_content(session)
        content_created = content is None
        if content is None:
            actor = HumanActor(user_id=admin.id)
            service = ContentService(session, audit)
            content = service.create(
                actor,
                content_type=ContentType.CAROUSEL,
                language=ContentLanguage.UZ,
                brand_profile_id=brand.id,
                topic=SEED_TOPIC,
                hook="Kichik xonani katta ko‘rsatishning 5 ta oddiy qoidasi.",
                caption=(
                    "Minimalizm — bu bo‘shliq emas, balki to‘g‘ri tanlov.\n\n"
                    "1. Ochiq ranglar palitrasi\n2. Yashirin saqlash joylari\n"
                    "3. Tabiiy yorug‘lik\n4. Kam, lekin sifatli mebel\n5. Bir xil materiallar"
                ),
                hashtags=["#interiordesign", "#minimalism", "#muxriddindesign"],
                cta="Foydali bo‘lsa, saqlab qo‘ying.",
                visual_prompt=BRAND["visual_style"],
                aspect_ratio="4:5",
                change_note="seed",
            )
            for position in range(3):
                service.add_asset(
                    content.id,
                    actor,
                    expected_version=content.version,
                    asset=AssetInput(
                        kind=AssetKind.IMAGE,
                        position=position,
                        storage_path=f"seed/minimal-bedroom-{position + 1}.jpg",
                        mime_type="image/jpeg",
                        width=1080,
                        height=1350,
                        provider="seed-placeholder",
                    ),
                )

        audit.record(
            AuditAction.SEED_APPLIED,
            system,
            details={"admin_created": admin_created, "content_created": content_created},
        )

    return SeedResult(
        admin_email=email,
        admin_created=admin_created,
        generated_password=generated,
        brand_profile_id=brand.id,
        content_id=content.id,
        content_created=content_created,
    )


def _find_seed_content(session: Session) -> Content | None:
    repo = ContentRepository(session)
    return session.scalar(repo._select().where(Content.topic == SEED_TOPIC))
