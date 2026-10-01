from sqlalchemy import text

from backend.app.database import create_database_engine


def test_sqlite_engine_connects_and_executes_query() -> None:
    engine = create_database_engine("sqlite:///:memory:")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar_one()
    finally:
        engine.dispose()

    assert result == 1
