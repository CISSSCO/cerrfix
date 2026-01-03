from pydantic import BaseModel, Field
from typing import List, Literal
from typing import Optional, Dict

class ErrorSignature(BaseModel):
    type: Literal["regex", "string"]
    pattern: str

class RootCause(BaseModel):
    summary: str
    details: str

class Resolution(BaseModel):
    strategy: Literal["manual", "automatic"]
    risk_level: Literal["low", "medium", "high"]
    steps: List[str]

class Verification(BaseModel):
    success_criteria: List[str]

class Fix(BaseModel):
    schema_version: float = Field(..., ge=1.0)

    issue_id: str = Field(
        ...,
        pattern=r"^[A-Z0-9_]+$",
        description="Unique issue identifier"
    )

    title: str

    category: str
    subcategory: str

    severity: Literal["info", "warning", "error", "critical"]
    confidence: Literal["low", "medium", "high"]
    scope: Optional[Dict[str, str]] = None
    error_signature: ErrorSignature

    description: str
    root_cause: RootCause
    resolution: Resolution
    verification: Verification

