from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.masters import MasterResponse, RoleResponse, SkillResponse, RoleCreate, RoleUpdate
from app.schemas.user import RoleWithUsersResponse
from app.services import master_service

router = APIRouter()

@router.get("/departments", response_model=List[MasterResponse])
def read_departments(db: Session = Depends(get_db)):
    return master_service.get_departments(db)

@router.get("/locations", response_model=List[MasterResponse])
def read_locations(db: Session = Depends(get_db)):
    return master_service.get_locations(db)

@router.get("/user-statuses", response_model=List[MasterResponse])
def read_user_statuses(db: Session = Depends(get_db)):
    return master_service.get_user_statuses(db)

@router.get("/statuses", response_model=List[MasterResponse])
def read_statuses(db: Session = Depends(get_db)):
    return master_service.get_statuses(db)

@router.get("/priorities", response_model=List[MasterResponse])
def read_priorities(db: Session = Depends(get_db)):
    return master_service.get_priorities(db)

@router.get("/roles", response_model=List[RoleResponse])
def read_roles(db: Session = Depends(get_db)):
    return master_service.get_roles(db)

@router.get("/roles/{role_id}", response_model=RoleWithUsersResponse)
def read_role(role_id: int, db: Session = Depends(get_db)):
    db_role = master_service.get_role(db, role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.post("/roles", response_model=RoleResponse)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    return master_service.create_role(db, role.model_dump())

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db)):
    return master_service.update_role(db, role_id, role.model_dump(exclude_unset=True))

@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    success = master_service.delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}

@router.get("/skills", response_model=List[SkillResponse])
def read_skills(db: Session = Depends(get_db)):
    return master_service.get_skills(db)
