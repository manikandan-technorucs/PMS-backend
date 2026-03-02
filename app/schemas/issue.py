from pydantic import BaseModel
from typing import Optional
from datetime import date
from .masters import MasterResponse
from .user import UserBase
from .project import ProjectBase

class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = 0.0

class IssueCreate(IssueBase):
    project_id: Optional[int] = None
    reporter_id: Optional[int] = None
    assignee_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    reporter_id: Optional[int] = None
    assignee_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = None

class IssueResponse(IssueBase):
    id: int
    public_id: str
    project_id: Optional[int] = None
    reporter_id: Optional[int] = None
    assignee_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None

    project: Optional[ProjectBase] = None
    reporter: Optional[UserBase] = None
    assignee: Optional[UserBase] = None
    status: Optional[MasterResponse] = None
    priority: Optional[MasterResponse] = None

    model_config = {"from_attributes": True}
