"""Guards against committing secrets."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _ignored(path: str) -> bool:
    return (
        subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT, check=False).returncode == 0
    )


def test_env_files_are_gitignored():
    assert _ignored(".env")
    assert _ignored("backend/.env")
    assert _ignored("frontend/.env.local")
    assert not _ignored(".env.example")


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
