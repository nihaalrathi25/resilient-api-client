from typing import Any
from pydantic import BaseModel, Field, HttpUrl


class APIRequest(BaseModel):
    url: HttpUrl
    payload: dict[str, Any] = Field(default_factory=dict)
    timeout: float = Field(default=5.0, gt=0, le=60)
    retry_count: int = Field(default=3, ge=0, le=10)
    fallback_data: dict[str, Any] | None = None


class APIResponse(BaseModel):
    status: str
    response: Any | None = None
    attempts: int
    retry_attempts: int
    fallback_used: bool
    error: str | None = None