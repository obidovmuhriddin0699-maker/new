from pydantic import BaseModel


class AIStatusResponse(BaseModel):
    provider: str
    model: str
    available: bool
    model_installed: bool
    error_code: str | None = None
    message: str | None = None
