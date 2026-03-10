from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.project_group import ProjectGroupCreate, ProjectGroupResponse, ProjectGroupUpdate
from app.services import project_group_service

router = APIRouter()

@router.get("/", response_model=List[ProjectGroupResponse])
def read_project_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return project_group_service.get_project_groups(db, skip=skip, limit=limit)

@router.post("/", response_model=ProjectGroupResponse)
def create_project_group(group: ProjectGroupCreate, db: Session = Depends(get_db)):
    return project_group_service.create_project_group(db, group)

@router.get("/{group_id}", response_model=ProjectGroupResponse)
def read_project_group(group_id: int, db: Session = Depends(get_db)):
    db_group = project_group_service.get_project_group(db, group_id)
    if not db_group:
        raise HTTPException(status_code=404, detail="Project group not found")
    return db_group

@router.put("/{group_id}", response_model=ProjectGroupResponse)
def update_project_group(group_id: int, group: ProjectGroupUpdate, db: Session = Depends(get_db)):
    db_group = project_group_service.update_project_group(db, group_id, group)
    if not db_group:
        raise HTTPException(status_code=404, detail="Project group not found")
    return db_group

@router.delete("/{group_id}")
def delete_project_group(group_id: int, db: Session = Depends(get_db)):
    success = project_group_service.delete_project_group(db, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project group not found")
    return {"message": "Project group deleted successfully"}
