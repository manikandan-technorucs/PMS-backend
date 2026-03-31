from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from .masters import MasterResponse
from .user import UserBase
from .project import ProjectBase
from .document import DocumentResponse

class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = 0.0

class IssueCreate(IssueBase):
    project_id: Optional[int] = None
    reporter_email: Optional[str] = None
    assignee_email: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    document_ids: Optional[List[int]] = []

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    reporter_email: Optional[str] = None
    assignee_email: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    document_ids: Optional[List[int]] = []

class IssueResponse(IssueBase):
    id: int
    public_id: str
    project_id: Optional[int] = None
    reporter_email: Optional[str] = None
    assignee_email: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None

    project: Optional[ProjectBase] = None
    reporter: Optional[UserBase] = None
    assignee: Optional[UserBase] = None
    status: Optional[MasterResponse] = None
    priority: Optional[MasterResponse] = None
    documents: Optional[List[DocumentResponse]] = []

    model_config = {"from_attributes": True}
