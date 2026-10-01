from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


Role = Literal["owner", "admin", "member"]
AssignableRole = Literal["admin", "member"]


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Workspace name cannot be blank")
        return value


class MemberCreate(BaseModel):
    email: EmailStr
    role: AssignableRole = "member"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class MemberRoleUpdate(BaseModel):
    role: AssignableRole


class UserResponse(BaseModel):
    id: str
    email: str


class MembershipResponse(BaseModel):
    user_id: str
    email: str
    role: Role


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    role: Role


class CurrentUserResponse(UserResponse):
    active_workspace_id: str | None
    workspaces: list[WorkspaceResponse]


class BillingPlanResponse(BaseModel):
    id: str
    name: str
    price_minor: int
    currency: str
    limits: dict[str, int]


class BillingStatusResponse(BaseModel):
    workspace_id: str
    status: Literal["trialing", "active", "expired"]
    trial_started_at: int
    trial_ends_at: int
    plan: BillingPlanResponse | None


class CheckoutRequest(BaseModel):
    plan_id: str = Field(min_length=1, max_length=64)


class CheckoutResponse(BaseModel):
    status: Literal["active"]
    plan_id: str
    payment_id: str
    simulated: Literal[True] = True


class UsageRequest(BaseModel):
    amount: int = Field(gt=0, le=100_000)


class UsageResponse(BaseModel):
    workspace_id: str
    metric: str
    period_start: int
    units: int
    limit: int | None


class AIChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=16_000)
    system: str | None = Field(default=None, max_length=4_000)


class AIChatResponse(BaseModel):
    model: str
    response: str
