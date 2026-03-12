from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services import project_service

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db=db, project=project)

@router.get("/search", response_model=List[ProjectResponse])
def search_projects(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return project_service.search_projects(db, query=q, limit=limit)

@router.get("/", response_model=List[ProjectResponse])
def read_projects(
    skip: int = 0, 
    limit: int = 100, 
    status_id: List[int] = Query(None),
    priority_id: List[int] = Query(None),
    manager_id: List[int] = Query(None),
    group_id: List[int] = Query(None),
    db: Session = Depends(get_db)
):
    return project_service.get_projects(
        db, 
        skip=skip, 
        limit=limit, 
        status_ids=status_id, 
        priority_ids=priority_id, 
        manager_ids=manager_id, 
        group_ids=group_id
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = project_service.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = project_service.update_project(db, project_id=project_id, project_update=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    success = project_service.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/users/{user_id}")
def assign_user_to_project(project_id: int, user_id: int, db: Session = Depends(get_db)):
    success = project_service.add_user_to_project(db, project_id=project_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project or User not found")
    return {"message": "User assigned to project successfully"}

@router.delete("/{project_id}/users/{user_id}")
def unassign_user_from_project(project_id: int, user_id: int, db: Session = Depends(get_db)):
    success = project_service.remove_user_from_project(db, project_id=project_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project or User not found")
    return {"message": "User removed from project successfully"}
