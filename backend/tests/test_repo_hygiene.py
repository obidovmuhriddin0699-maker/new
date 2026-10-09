"""Guards against committing secrets."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Needs the git checkout (not available inside the Docker test image).
pytestmark = pytest.mark.skipif(not (ROOT / ".git").exists(), reason="not a git checkout")


def _ignored(path: str) -> bool:
    return (
        subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT, check=False).returncode == 0
    )


def test_env_files_are_gitignored():
    assert _ignored(".env")
    assert _ignored("backend/.env")
    assert _ignored("frontend/.env.local")
    assert not _ignored(".env.example")
    assert not _ignored(".env.production.example")
    assert _ignored(".env.production")


def test_env_example_has_no_real_secrets():
    text = (ROOT / ".env.example").read_text()
    for line in text.splitlines():
        if line.startswith(("JWT_SECRET_KEY=", "TOKEN_ENCRYPTION_KEYS=")):
            assert line.split("=", 1)[1].strip() in ("", "change-me")


def test_source_folders_are_never_ignored():
    # A bare "media/" pattern once hid frontend/src/app/(panel)/media from git.
    for path in (
        "frontend/src/app/(panel)/media/page.tsx",
        "frontend/src/app/media/[name]/route.ts",
        "backend/app/services/media_storage.py",
    ):
        assert not _ignored(path), path
    assert _ignored("backend/data/media/upload.jpg")


SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "Meta/Facebook token": re.compile(r"\bEAA[A-Za-z0-9]{60,}"),
    "Instagram token": re.compile(r"\bIGAA[A-Za-z0-9_-]{60,}"),
    "Telegram bot token": re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_-]{33}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "OpenAI/Anthropic-style key": re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{32,}"),
    "Fernet key assignment": re.compile(r"TOKEN_ENCRYPTION_KEYS\s*=\s*['\"]?[A-Za-z0-9_-]{43}="),
}


def test_no_secrets_in_tracked_files():
    files = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    hits = []
    for name in files:
        if name.endswith(("package-lock.json", ".png", ".jpg", ".ico", ".woff2")):
            continue
        try:
            text = (ROOT / name).read_text(errors="ignore")
        except (IsADirectoryError, FileNotFoundError):
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                hits.append(f"{name}: {label}")
    assert hits == []
