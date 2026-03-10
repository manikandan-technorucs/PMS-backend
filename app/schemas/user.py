from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from .masters import RoleResponse, MasterResponse, SkillResponse

class UserBase(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    role: Optional[RoleResponse] = None
    is_external: Optional[bool] = False
    is_synced: Optional[bool] = False
    display_name: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    language: Optional[str] = "English"
    timezone: Optional[str] = "Asia/Kolkata"

class UserCreate(UserBase):
    employee_id: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    join_date: Optional[date] = None
    role_id: Optional[int] = None
    dept_id: Optional[int] = None
    status_id: Optional[int] = None
    location_id: Optional[int] = None
    manager_id: Optional[int] = None
    skill_ids: Optional[List[int]] = []
    o365_id: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    join_date: Optional[date] = None
    role_id: Optional[int] = None
    dept_id: Optional[int] = None
    status_id: Optional[int] = None
    location_id: Optional[int] = None
    manager_id: Optional[int] = None
    skill_ids: Optional[List[int]] = None
    o365_id: Optional[str] = None
    is_external: Optional[bool] = None
    is_synced: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    public_id: str
    employee_id: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    join_date: Optional[date] = None
    role_id: Optional[int] = None
    dept_id: Optional[int] = None
    status_id: Optional[int] = None
    location_id: Optional[int] = None
    manager_id: Optional[int] = None
    o365_id: Optional[str] = None
    display_name: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

    role: Optional[RoleResponse] = None
    department: Optional[MasterResponse] = None
    status: Optional[MasterResponse] = None
    location: Optional[MasterResponse] = None
    manager: Optional[UserBase] = None
    skills: List[SkillResponse] = []

    model_config = {"from_attributes": True}

class RoleWithUsersResponse(RoleResponse):
    users: List[UserResponse] = []
