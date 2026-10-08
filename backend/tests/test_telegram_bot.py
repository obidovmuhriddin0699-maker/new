from unittest.mock import patch
import logging

import pytest

from backend import telegram_bot


def test_main_loads_token_from_repository_env_file_without_logging_it(
    monkeypatch,
    tmp_path,
    caplog,
) -> None:
    secret = "local-test-token-never-log"
    (tmp_path / ".env").write_text(f"TELEGRAM_BOT_TOKEN={secret}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr(logging.getLogger("httpx"), "level", logging.NOTSET)

    with (
        patch.object(telegram_bot.Base.metadata, "create_all"),
        patch.object(telegram_bot, "run_polling") as run_polling,
    ):
        telegram_bot.main()

    assert run_polling.call_args.args[2]._token == secret
    assert secret not in caplog.text
    assert logging.getLogger("httpx").getEffectiveLevel() >= logging.WARNING


def test_process_environment_token_takes_precedence_over_env_file(
    monkeypatch,
    tmp_path,
) -> None:
    (tmp_path / ".env").write_text(
        "TELEGRAM_BOT_TOKEN=file-test-token\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "process-test-token")

    with (
        patch.object(telegram_bot.Base.metadata, "create_all"),
        patch.object(telegram_bot, "run_polling") as run_polling,
    ):
        telegram_bot.main()

    assert run_polling.call_args.args[2]._token == "process-test-token"


def test_main_refuses_to_start_without_a_token(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(SystemExit, match="repository-root .env"):
        telegram_bot.main()
