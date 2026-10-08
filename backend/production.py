import os
import subprocess
import sys

from backend.app.config import validate_production_configuration
from backend.app.database import engine


def main() -> None:
    validate_production_configuration(os.environ, engine.url.drivername)
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
    )
    port = os.getenv("PORT", "8000")
    os.execvpe(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            port,
        ],
        os.environ.copy(),
    )


if __name__ == "__main__":
    main()
