from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.masters import MasterResponse, RoleResponse, SkillResponse, RoleCreate
from app.services import master_service

router = APIRouter()

@router.get("/departments", response_model=List[MasterResponse])
def read_departments(db: Session = Depends(get_db)):
    return master_service.get_departments(db)

@router.get("/locations", response_model=List[MasterResponse])
def read_locations(db: Session = Depends(get_db)):
    return master_service.get_locations(db)

@router.get("/statuses", response_model=List[MasterResponse])
def read_statuses(db: Session = Depends(get_db)):
    return master_service.get_statuses(db)

@router.get("/roles", response_model=List[RoleResponse])
def read_roles(db: Session = Depends(get_db)):
    return master_service.get_roles(db)

@router.post("/roles", response_model=RoleResponse)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    return master_service.create_role(db, role.model_dump())

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role: RoleCreate, db: Session = Depends(get_db)):
    return master_service.update_role(db, role_id, role.model_dump(exclude_unset=True))

@router.get("/skills", response_model=List[SkillResponse])
def read_skills(db: Session = Depends(get_db)):
    return master_service.get_skills(db)
