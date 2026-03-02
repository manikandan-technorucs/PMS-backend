from pydantic import BaseModel
from typing import Optional
from .project import ProjectBase

class TaskListBase(BaseModel):
    name: str
    description: Optional[str] = None

class TaskListCreate(TaskListBase):
    project_id: int

class TaskListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None

class TaskListResponse(TaskListBase):
    id: int
    project_id: int
    project: Optional[ProjectBase] = None

    model_config = {"from_attributes": True}
