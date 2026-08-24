from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ==================================================
# Project
# ==================================================

class ProjectBase(BaseModel):
    name: str
    description: str | None = None




class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectResponse(ProjectBase):
    id: str
    owner_id: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==================================================
# ProjectMember
# ==================================================

class ProjectMemberBase(BaseModel):
    role: str = "MEMBER"


class ProjectMemberCreate(ProjectMemberBase):
    project_id: str
    user_id: str


class ProjectMemberUpdate(BaseModel):
    role: str | None = None


class ProjectMemberResponse(ProjectMemberBase):
    project_id: str
    user_id: str
    joined_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class AddMemberRequest(BaseModel):
    user_id: str
    role: str = "MEMBER"

class ProjectMemberDetailResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)