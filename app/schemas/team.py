from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .masters import MasterResponse
from .user import UserResponse

class TeamBase(BaseModel):
    name: str
    team_email: EmailStr
    budget_allocation: float = 0.0
    description: Optional[str] = None
    team_type: Optional[str] = None
    max_team_size: Optional[int] = None
    primary_communication_channel: Optional[str] = None
    channel_id: Optional[str] = None

class TeamCreate(TeamBase):
    lead_id: Optional[int] = None
    dept_id: Optional[int] = None
    location_id: Optional[int] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    team_email: Optional[EmailStr] = None
    budget_allocation: Optional[float] = None
    description: Optional[str] = None
    team_type: Optional[str] = None
    max_team_size: Optional[int] = None
    primary_communication_channel: Optional[str] = None
    channel_id: Optional[str] = None
    lead_id: Optional[int] = None
    dept_id: Optional[int] = None
    location_id: Optional[int] = None

class TeamResponse(TeamBase):
    id: int
    public_id: str
    lead_id: Optional[int] = None
    dept_id: Optional[int] = None
    location_id: Optional[int] = None
    
    department: Optional[MasterResponse] = None
    location: Optional[MasterResponse] = None
    # Cannot include lead to avoid deep nesting recursive import directly, but we can do it if desired.
    
    model_config = {"from_attributes": True}

class TeamWithMembersResponse(TeamResponse):
    members: List[UserResponse] = []
