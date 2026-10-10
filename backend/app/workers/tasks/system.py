from app.workers.celery_app import celery_app


@celery_app.task(name="system.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="ops.check")
def ops_check() -> list[dict]:
    """Operational problems -> OPS_ALERT (Telegram) when they change; see app/services/ops.py."""
    from dataclasses import asdict

    from app.core.database import get_sessionmaker
    from app.services.ops import OpsMonitor

    with get_sessionmaker()() as session:
        return [asdict(p) for p in OpsMonitor(session).run()]
