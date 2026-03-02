from pydantic import BaseModel
from typing import Optional
from datetime import date
from .masters import MasterResponse
from .user import UserBase
from .team import TeamBase

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    client: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = 0.0

class ProjectCreate(ProjectBase):
    manager_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    dept_id: Optional[int] = None
    team_id: Optional[int] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    manager_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    dept_id: Optional[int] = None
    team_id: Optional[int] = None

class ProjectResponse(ProjectBase):
    id: int
    public_id: str
    manager_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    dept_id: Optional[int] = None
    team_id: Optional[int] = None

    manager: Optional[UserBase] = None
    status: Optional[MasterResponse] = None
    priority: Optional[MasterResponse] = None
    department: Optional[MasterResponse] = None
    team: Optional[TeamBase] = None

    model_config = {"from_attributes": True}
