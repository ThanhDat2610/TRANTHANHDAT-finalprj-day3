from datetime import datetime

from pydantic import BaseModel, ConfigDict


# =========================
# Base
# =========================

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: datetime | None = None


# =========================
# Create
# =========================

class TaskCreate(TaskBase):
    project_id: str
    assignee_id: str | None = None


# =========================
# Update
# =========================

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None


# =========================
# Response
# =========================

class TaskResponse(TaskBase):
    id: str
    project_id: str
    assignee_id: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )