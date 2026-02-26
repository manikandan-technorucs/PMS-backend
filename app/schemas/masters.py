from pydantic import BaseModel
from typing import Dict, Any, Optional

class MasterBase(BaseModel):
    name: str

class MasterCreate(MasterBase):
    pass

class MasterResponse(MasterBase):
    id: int

    model_config = {"from_attributes": True}

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Dict[str, Any] = {}

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int

    model_config = {"from_attributes": True}

class SkillBase(BaseModel):
    name: str

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int

    model_config = {"from_attributes": True}
