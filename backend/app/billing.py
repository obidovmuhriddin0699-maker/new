import json
import os
import time
import uuid
from dataclasses import dataclass

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import WorkspaceBilling, WorkspaceUsage


TRIAL_DURATION_SECONDS = 30 * 24 * 60 * 60
PLAN_CATALOG_ENV = "BILLING_PLANS_JSON"


class PlanConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(min_length=1, max_length=100)
    price_minor: int = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    limits: dict[str, int] = Field(default_factory=dict)


def get_plan_catalog() -> dict[str, PlanConfig]:
    raw_catalog = os.getenv(PLAN_CATALOG_ENV, "[]")
    try:
        configs = TypeAdapter(list[PlanConfig]).validate_python(json.loads(raw_catalog))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing plan catalog is not configured correctly",
        ) from exc

    catalog = {plan.id: plan for plan in configs}
    if len(catalog) != len(configs):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing plan catalog contains duplicate ids",
        )
    for plan in configs:
        if any(not metric or value < 0 for metric, value in plan.limits.items()):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Billing plan limits must be non-negative",
            )
    return catalog


def ensure_billing_account(db: Session, workspace_id: str) -> WorkspaceBilling:
    billing = db.get(WorkspaceBilling, workspace_id)
    if billing is None:
        now = int(time.time())
        billing = WorkspaceBilling(
            workspace_id=workspace_id,
            trial_started_at=now,
            trial_ends_at=now + TRIAL_DURATION_SECONDS,
            status="trialing",
        )
        db.add(billing)
        db.flush()
    return billing


def effective_status(billing: WorkspaceBilling, now: int | None = None) -> str:
    if billing.status == "active":
        return "active"
    if billing.status == "trialing" and billing.trial_ends_at <= (now or int(time.time())):
        return "expired"
    return billing.status


def enforce_and_record_usage(
    db: Session,
    billing: WorkspaceBilling,
    workspace_id: str,
    metric: str,
    amount: int,
    now: int | None = None,
) -> WorkspaceUsage:
    billing = db.scalar(
        select(WorkspaceBilling)
        .where(WorkspaceBilling.workspace_id == workspace_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ) or billing
    status_now = effective_status(billing, now)
    if status_now == "expired":
        raise HTTPException(status_code=402, detail="Workspace trial has expired")
    if status_now != "active" and status_now != "trialing":
        raise HTTPException(status_code=402, detail="Workspace billing is not active")

    plan = get_plan_catalog().get(billing.plan_id) if billing.plan_id else None
    if billing.status == "active" and plan is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active workspace plan is missing from the configured catalog",
        )
    limit = plan.limits.get(metric) if plan else None
    current_period = now or int(time.time())
    period_start = current_period - current_period % (30 * 24 * 60 * 60)
    usage = db.scalar(
        select(WorkspaceUsage)
        .where(
            WorkspaceUsage.workspace_id == workspace_id,
            WorkspaceUsage.metric == metric,
            WorkspaceUsage.period_start == period_start,
        )
        .with_for_update()
    )
    current_units = usage.units if usage else 0
    if limit is not None and current_units + amount > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"message": "Workspace plan limit exceeded", "metric": metric, "limit": limit},
        )

    if usage is None:
        usage = WorkspaceUsage(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            metric=metric,
            period_start=period_start,
            units=amount,
        )
        db.add(usage)
    else:
        usage.units += amount
    db.flush()
    return usage


@dataclass(frozen=True)
class TestPaymentResult:
    payment_id: str


class TestPaymentAdapter:
    def create_checkout(self, workspace_id: str, plan_id: str) -> TestPaymentResult:
        return TestPaymentResult(payment_id=f"test_{uuid.uuid4().hex}")


def get_test_payment_adapter() -> TestPaymentAdapter:
    if os.getenv("PAYMENT_MODE", "test").lower() != "test":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Only the test payment adapter is available",
        )
    return TestPaymentAdapter()
