import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.billing import (
    PlanConfig,
    effective_status,
    ensure_billing_account,
    enforce_and_record_usage,
    get_plan_catalog,
    get_test_payment_adapter,
)
from backend.app.database import get_db
from backend.app.dependencies import CurrentUser, CsrfSession, require_membership, require_workspace_admin
from backend.app.models import Workspace, WorkspaceBilling, WorkspaceUsage
from backend.app.schemas import (
    BillingPlanResponse,
    BillingStatusResponse,
    CheckoutRequest,
    CheckoutResponse,
    UsageRequest,
    UsageResponse,
)


router = APIRouter(prefix="/workspaces/{workspace_id}/billing", tags=["billing"])


def plan_response(plan: PlanConfig) -> BillingPlanResponse:
    return BillingPlanResponse(
        id=plan.id,
        name=plan.name,
        price_minor=plan.price_minor,
        currency=plan.currency,
        limits=plan.limits,
    )


@router.get("/plans", response_model=list[BillingPlanResponse])
def list_plans(
    workspace_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[BillingPlanResponse]:
    require_membership(workspace_id, user, db)
    return [plan_response(plan) for plan in get_plan_catalog().values()]


@router.get("", response_model=BillingStatusResponse)
def get_billing_status(
    workspace_id: str,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> BillingStatusResponse:
    require_membership(workspace_id, user, db)
    if db.get(Workspace, workspace_id) is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    billing = ensure_billing_account(db, workspace_id)
    db.commit()
    catalog = get_plan_catalog()
    selected_plan = catalog.get(billing.plan_id) if billing.plan_id else None
    if billing.status == "active" and selected_plan is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active workspace plan is missing from the configured catalog",
        )
    now = int(time.time())
    period_start = now - now % (30 * 24 * 60 * 60)
    usage_rows = db.scalars(
        select(WorkspaceUsage).where(
            WorkspaceUsage.workspace_id == workspace_id,
            WorkspaceUsage.period_start == period_start,
        )
    )
    return BillingStatusResponse(
        workspace_id=workspace_id,
        status=effective_status(billing),
        trial_started_at=billing.trial_started_at,
        trial_ends_at=billing.trial_ends_at,
        plan=plan_response(selected_plan) if selected_plan else None,
        usage={row.metric: row.units for row in usage_rows},
    )


@router.post("/checkout", response_model=CheckoutResponse)
def start_test_checkout(
    workspace_id: str,
    payload: CheckoutRequest,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    require_workspace_admin(workspace_id, user, db)
    plan = get_plan_catalog().get(payload.plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Billing plan not found")
    billing = ensure_billing_account(db, workspace_id)
    payment = get_test_payment_adapter().create_checkout(workspace_id, plan.id)
    billing.plan_id = plan.id
    billing.status = "active"
    billing.simulated_payment_id = payment.payment_id
    db.commit()
    return CheckoutResponse(status="active", plan_id=plan.id, payment_id=payment.payment_id)


@router.post("/usage/{metric}", response_model=UsageResponse)
def record_usage(
    workspace_id: str,
    metric: str,
    payload: UsageRequest,
    auth_session: CsrfSession,
    user: CurrentUser,
    db: Session = Depends(get_db),
) -> UsageResponse:
    require_membership(workspace_id, user, db)
    if not metric or len(metric) > 64:
        raise HTTPException(status_code=422, detail="Metric name must contain 1 to 64 characters")
    billing = ensure_billing_account(db, workspace_id)
    period_start = int(time.time())
    usage = enforce_and_record_usage(
        db,
        billing,
        workspace_id,
        metric,
        payload.amount,
        period_start,
    )
    db.commit()
    plan = get_plan_catalog().get(billing.plan_id) if billing.plan_id else None
    return UsageResponse(
        workspace_id=workspace_id,
        metric=metric,
        period_start=usage.period_start,
        units=usage.units,
        limit=plan.limits.get(metric) if plan else None,
    )
