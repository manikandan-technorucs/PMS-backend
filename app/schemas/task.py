from pydantic import BaseModel
from typing import Optional
from datetime import date
from .masters import MasterResponse
from .user import UserBase
from .project import ProjectBase

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    progress: int = 0
    estimated_hours: Optional[float] = 0.0
    project: Optional[ProjectBase] = None

class TaskCreate(TaskBase):
    project_id: Optional[int] = None
    task_list_id: Optional[int] = None
    assignee_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    progress: Optional[int] = None
    estimated_hours: Optional[float] = None
    project_id: Optional[int] = None
    task_list_id: Optional[int] = None
    assignee_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    public_id: str
    project_id: Optional[int] = None
    task_list_id: Optional[int] = None
    assignee_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None

    project: Optional[ProjectBase] = None
    assignee: Optional[UserBase] = None
    status: Optional[MasterResponse] = None
    priority: Optional[MasterResponse] = None

    model_config = {"from_attributes": True}
