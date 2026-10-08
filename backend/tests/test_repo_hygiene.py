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
