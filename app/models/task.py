from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    project_id = Column(
        String(36),
        ForeignKey("projects.id"),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    assignee_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=True,
    )

    status = Column(
        Enum(
            "TODO",
            "IN_PROGRESS",
            "DONE",
            name="task_status",
        ),
        nullable=False,
        default="TODO",
    )

    priority = Column(
        Enum(
            "LOW",
            "MEDIUM",
            "HIGH",
            name="task_priority",
        ),
        nullable=False,
        default="MEDIUM",
    )

    due_date = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    # Project chứa task
    project = relationship(
        "Project",
        back_populates="tasks",
    )

    # User được giao task
    assignee = relationship(
        "UserModel",
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id],
    )