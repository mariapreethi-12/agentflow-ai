from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


StageId = Literal["intake", "prd", "architecture", "backend", "qa", "review"]


class Approval(BaseModel):
    approved: bool = False
    approved_at: datetime | None = None
    note: str = "Waiting for human approval."


class Artifact(BaseModel):
    schema_name: str
    title: str
    score: int = Field(ge=0, le=100)
    generated_at: datetime
    data: dict[str, Any]


class ProjectCreate(BaseModel):
    name: str = "Dental clinic booking workflow"
    idea: str
    answers: dict[int, str] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    name: str | None = None
    idea: str | None = None
    answers: dict[int, str] | None = None
    active_stage: StageId | None = None


class ApprovalRequest(BaseModel):
    stage: StageId
    note: str | None = None


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    idea: str
    answers: dict[int, str] = Field(default_factory=dict)
    active_stage: StageId = "intake"
    approvals: dict[StageId, Approval] = Field(default_factory=dict)
    artifacts: dict[str, Artifact] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectListItem(BaseModel):
    id: str
    name: str
    active_stage: StageId
    updated_at: datetime
