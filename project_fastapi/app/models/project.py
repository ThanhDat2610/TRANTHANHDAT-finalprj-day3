from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    owner_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    # User sở hữu project
    owner = relationship(
        "UserModel",
        back_populates="owned_projects",
        foreign_keys=[owner_id],
    )

    # Thành viên
    members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Tasks
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectMember(Base):
    __tablename__ = "project_members"

    # Composite Primary Key
    project_id = Column(
        String(36),
        ForeignKey("projects.id"),
        primary_key=True,
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        primary_key=True,
    )

    role = Column(
        Enum(
            "OWNER",
            "MEMBER",
            name="project_member_role",
        ),
        nullable=False,
        default="MEMBER",
    )

    joined_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    # Project
    project = relationship(
        "Project",
        back_populates="members",
    )

    # User
    user = relationship(
        "UserModel",
        back_populates="project_memberships",
    )