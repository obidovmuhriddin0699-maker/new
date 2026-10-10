from app.workers.celery_app import celery_app
from app.workers.tasks.system import ping


def test_celery_app_configured():
    assert celery_app.main == "muxriddin"
    assert "system.ping" in celery_app.tasks


def test_ping_task_eager():
    celery_app.conf.task_always_eager = True
    assert ping.delay().get(timeout=1) == "pong"
