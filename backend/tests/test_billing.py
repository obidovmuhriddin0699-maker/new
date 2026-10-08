import json
import time

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.dependencies import CSRF_COOKIE_NAME
from backend.app.models import WorkspaceBilling
from backend.app.billing import TRIAL_DURATION_SECONDS


PASSWORD = "correct horse battery staple"
PLANS = [
    {
        "id": "configured",
        "name": "Configured plan",
        "price_minor": 1234,
        "currency": "USD",
        "limits": {"calls": 3},
    }
]


def register(client: TestClient, email: str) -> None:
    response = client.post("/auth/register", json={"email": email, "password": PASSWORD})
    assert response.status_code == 201


def create_workspace(client: TestClient, name: str) -> str:
    response = client.post(
        "/workspaces",
        json={"name": name},
        headers={"X-CSRF-Token": client.cookies[CSRF_COOKIE_NAME]},
    )
    assert response.status_code == 201
    return response.json()["id"]


def csrf(client: TestClient) -> dict[str, str]:
    return {"X-CSRF-Token": client.cookies[CSRF_COOKIE_NAME]}


def test_workspace_trial_is_thirty_days_and_plan_catalog_is_configured(
    client,
    monkeypatch,
) -> None:
    monkeypatch.setenv("BILLING_PLANS_JSON", json.dumps(PLANS))
    register(client, "owner@example.com")
    workspace_id = create_workspace(client, "Trial workspace")

    response = client.get(f"/workspaces/{workspace_id}/billing")

    assert response.status_code == 200
    billing = response.json()
    assert billing["status"] == "trialing"
    assert billing["trial_ends_at"] - billing["trial_started_at"] == TRIAL_DURATION_SECONDS
    assert billing["plan"] is None
    plans = client.get(f"/workspaces/{workspace_id}/billing/plans")
    assert plans.status_code == 200
    assert plans.json() == PLANS
    assert billing["usage"] == {}


def test_billing_status_reports_workspace_scoped_usage(client) -> None:
    register(client, "usage-owner@example.com")
    workspace_id = create_workspace(client, "Usage workspace")
    response = client.post(
        f"/workspaces/{workspace_id}/billing/usage/ai_requests",
        json={"amount": 2},
        headers=csrf(client),
    )
    assert response.status_code == 200

    billing = client.get(f"/workspaces/{workspace_id}/billing")
    assert billing.status_code == 200
    assert billing.json()["usage"] == {"ai_requests": 2}


def test_checkout_is_test_only_and_usage_limit_is_workspace_scoped(
    client,
    monkeypatch,
) -> None:
    monkeypatch.setenv("BILLING_PLANS_JSON", json.dumps(PLANS))
    register(client, "owner@example.com")
    first_workspace = create_workspace(client, "First")
    second_workspace = create_workspace(client, "Second")
    checkout = client.post(
        f"/workspaces/{first_workspace}/billing/checkout",
        json={"plan_id": "configured"},
        headers=csrf(client),
    )

    assert checkout.status_code == 200
    assert checkout.json()["simulated"] is True
    assert checkout.json()["payment_id"].startswith("test_")
    assert client.get(f"/workspaces/{first_workspace}/billing").json()["status"] == "active"

    first_usage = client.post(
        f"/workspaces/{first_workspace}/billing/usage/calls",
        json={"amount": 2},
        headers=csrf(client),
    )
    assert first_usage.status_code == 200
    assert first_usage.json()["units"] == 2
    exceeded = client.post(
        f"/workspaces/{first_workspace}/billing/usage/calls",
        json={"amount": 2},
        headers=csrf(client),
    )
    assert exceeded.status_code == 429

    other_workspace_usage = client.post(
        f"/workspaces/{second_workspace}/billing/usage/calls",
        json={"amount": 3},
        headers=csrf(client),
    )
    assert other_workspace_usage.status_code == 200
    assert other_workspace_usage.json()["units"] == 3


def test_billing_admin_authorization_tenant_isolation_and_payment_mode(
    client,
    monkeypatch,
) -> None:
    monkeypatch.setenv("BILLING_PLANS_JSON", json.dumps(PLANS))
    register(client, "owner@example.com")
    workspace_id = create_workspace(client, "Owner workspace")
    member = TestClient(client.app)
    other = TestClient(client.app)

    with member, other:
        register(member, "member@example.com")
        assert client.post(
            f"/workspaces/{workspace_id}/members",
            json={"email": "member@example.com", "role": "member"},
            headers=csrf(client),
        ).status_code == 201
        assert member.post(
            f"/workspaces/{workspace_id}/billing/checkout",
            json={"plan_id": "configured"},
            headers=csrf(member),
        ).status_code == 403

        register(other, "outsider@example.com")
        assert other.get(f"/workspaces/{workspace_id}/billing").status_code == 404
        assert other.post(
            f"/workspaces/{workspace_id}/billing/checkout",
            json={"plan_id": "configured"},
            headers=csrf(other),
        ).status_code == 404

    monkeypatch.setenv("PAYMENT_MODE", "live")
    unavailable = client.post(
        f"/workspaces/{workspace_id}/billing/checkout",
        json={"plan_id": "configured"},
        headers=csrf(client),
    )
    assert unavailable.status_code == 503


def test_expired_trial_rejects_metered_usage(client, test_engine) -> None:
    register(client, "owner@example.com")
    workspace_id = create_workspace(client, "Expired")
    with Session(test_engine) as db:
        billing = db.scalar(
            select(WorkspaceBilling).where(WorkspaceBilling.workspace_id == workspace_id)
        )
        assert billing is not None
        billing.trial_ends_at = int(time.time()) - 1
        db.commit()

    response = client.post(
        f"/workspaces/{workspace_id}/billing/usage/calls",
        json={"amount": 1},
        headers=csrf(client),
    )
    assert response.status_code == 402


def test_unknown_plan_and_untrusted_prices_are_rejected(client, monkeypatch) -> None:
    register(client, "owner@example.com")
    workspace_id = create_workspace(client, "No plans")
    assert client.get(f"/workspaces/{workspace_id}/billing/plans").json() == []

    unknown = client.post(
        f"/workspaces/{workspace_id}/billing/checkout",
        json={"plan_id": "made-up"},
        headers=csrf(client),
    )
    assert unknown.status_code == 404

    monkeypatch.setenv("BILLING_PLANS_JSON", json.dumps([{"id": "malformed", "price": 0}]))
    invalid_catalog = client.get(f"/workspaces/{workspace_id}/billing/plans")
    assert invalid_catalog.status_code == 503


def test_missing_active_plan_does_not_disable_limits(client, monkeypatch) -> None:
    monkeypatch.setenv("BILLING_PLANS_JSON", json.dumps(PLANS))
    register(client, "owner@example.com")
    workspace_id = create_workspace(client, "Plan catalog changes")
    assert client.post(
        f"/workspaces/{workspace_id}/billing/checkout",
        json={"plan_id": "configured"},
        headers=csrf(client),
    ).status_code == 200

    monkeypatch.setenv("BILLING_PLANS_JSON", "[]")
    usage = client.post(
        f"/workspaces/{workspace_id}/billing/usage/calls",
        json={"amount": 1},
        headers=csrf(client),
    )
    assert usage.status_code == 503
