import logging
import os

from dotenv import load_dotenv

from backend.app.config import is_production, validate_production_configuration
from backend.app.database import Base, SessionLocal, engine
from backend.app import models  # noqa: F401
from backend.app.ollama import OllamaAdapter
from backend.app.telegram import TelegramBotAPI, run_polling


def main() -> None:
    load_dotenv(dotenv_path=".env", override=False)
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit(
            "Set TELEGRAM_BOT_TOKEN in the local environment or repository-root .env before starting polling."
        )

    if is_production(os.environ):
        validate_production_configuration(os.environ, engine.url.drivername)
    else:
        Base.metadata.create_all(bind=engine)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger(__name__).info("Telegram polling started; bot token is not logged.")
    run_polling(SessionLocal, OllamaAdapter(), TelegramBotAPI(token))


if __name__ == "__main__":
    main()
