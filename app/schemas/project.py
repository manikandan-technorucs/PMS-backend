from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date
from .masters import MasterResponse
from .user import UserBase
from .team import TeamBase
from .project_group import ProjectGroupResponse

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    client: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = None

class ProjectCreate(ProjectBase):
    manager_email: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    manager_email: Optional[str] = None
    status_id: Optional[int] = None
    previous_status: Optional[int] = None
    priority_id: Optional[int] = None

class ProjectResponse(ProjectBase):
    id: int
    public_id: str
    manager_email: Optional[str] = None
    created_by_email: Optional[str] = None
    status_id: Optional[int] = None
    previous_status: Optional[int] = None
    priority_id: Optional[int] = None

    manager: Optional[UserBase] = None
    creator: Optional[UserBase] = None
    status: Optional[MasterResponse] = None
    previous_status_obj: Optional[MasterResponse] = None
    priority: Optional[MasterResponse] = None
    users: List[UserBase] = []

    model_config = {"from_attributes": True}

class ProjectListResponse(BaseModel):
    total: int
    data: List[ProjectResponse]


class ProjectUserCreate(BaseModel):
    """
    Validated payload for assigning a user to a project.
    Ensures user_id (Microsoft OID), user_email, and project_id are never null or empty.
    """
    user_id: str
    user_email: str
    display_name: Optional[str] = None  # Needed for JIT provisioning
    project_id: int
    role_id: Optional[int] = None

    @field_validator("project_id")
    @classmethod
    def id_must_be_positive(cls, v: int, info) -> int:
        if v is None or v <= 0:
            raise ValueError(f"{info.field_name} must be a positive integer")
        return v

    @field_validator("user_id", "user_email")
    @classmethod
    def value_must_not_be_empty(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} must not be null or empty")
        return v.strip()


