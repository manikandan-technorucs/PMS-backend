from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import allow_authenticated
from app.schemas.milestone import MilestoneCreate, MilestoneResponse, MilestoneUpdate
from app.services import milestone_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])

@router.post("/", response_model=MilestoneResponse)
def create_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user = Depends(allow_authenticated)
):
    return milestone_service.create_milestone(db=db, milestone=milestone, actor_id=current_user.o365_id or str(current_user.id))

@router.get("/", response_model=List[MilestoneResponse])
def read_milestones(
    project_id: int = None,
    skip: int = 0,
    limit: int = 100,
    status_id: List[int] = Query(None),
    db: Session = Depends(get_db)
):
    return milestone_service.get_milestones(
        db, 
        skip=skip, 
        limit=limit, 
        project_id=project_id,
        status_ids=status_id
    )

@router.get("/{milestone_id}", response_model=MilestoneResponse)
def read_milestone(
    milestone_id: int,
    db: Session = Depends(get_db)
):
    db_milestone = milestone_service.get_milestone(db, milestone_id=milestone_id)
    if db_milestone is None:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return db_milestone

@router.put("/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: int,
    milestone_in: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(allow_authenticated)
):
    custom = milestone_service.update_milestone(db, milestone_id, milestone_in, actor_id=current_user.o365_id or str(current_user.id))
    if not custom:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return custom

@router.delete("/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(allow_authenticated)
):
    success = milestone_service.delete_milestone(db, milestone_id=milestone_id, actor_id=current_user.o365_id or str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return {"message": "Milestone deleted successfully"}
