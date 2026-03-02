from pydantic import BaseModel
from typing import Optional
from datetime import date
from .user import UserBase
from .task import TaskBase
from .project import ProjectBase
from .issue import IssueBase

class TimeLogBase(BaseModel):
    date: date
    hours: float
    description: Optional[str] = None

class TimeLogCreate(TimeLogBase):
    user_id: int
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    issue_id: Optional[int] = None

class TimeLogUpdate(BaseModel):
    date: Optional[date] = None
    hours: Optional[float] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    issue_id: Optional[int] = None

class TimeLogResponse(TimeLogBase):
    id: int
    user_id: int
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    issue_id: Optional[int] = None

    user: Optional[UserBase] = None
    project: Optional[ProjectBase] = None
    task: Optional[TaskBase] = None
    issue: Optional[IssueBase] = None

    model_config = {"from_attributes": True}
