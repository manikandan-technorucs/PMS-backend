from pydantic import BaseModel
from typing import Optional
from datetime import date
from .masters import MasterResponse
from .project import ProjectBase

class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class MilestoneCreate(MilestoneBase):
    project_id: int
    status_id: Optional[int] = None

class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_id: Optional[int] = None
    status_id: Optional[int] = None

class MilestoneResponse(MilestoneBase):
    id: int
    public_id: str
    project_id: Optional[int] = None
    status_id: Optional[int] = None

    project: Optional[ProjectBase] = None
    status: Optional[MasterResponse] = None

    model_config = {"from_attributes": True}
