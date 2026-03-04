from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.timelog import TimeLogCreate, TimeLogUpdate, TimeLogResponse
from app.services import timelog_service

router = APIRouter()

@router.post("/", response_model=TimeLogResponse)
def create_timelog(timelog: TimeLogCreate, db: Session = Depends(get_db)):
    return timelog_service.create_timelog(db=db, timelog=timelog)

@router.get("/", response_model=List[TimeLogResponse])
def read_timelogs(skip: int = 0, limit: int = 100, project_id: int = None, db: Session = Depends(get_db)):
    return timelog_service.get_timelogs(db, skip=skip, limit=limit, project_id=project_id)

@router.get("/{timelog_id}", response_model=TimeLogResponse)
def read_timelog(timelog_id: int, db: Session = Depends(get_db)):
    db_timelog = timelog_service.get_timelog(db, timelog_id=timelog_id)
    if db_timelog is None:
        raise HTTPException(status_code=404, detail="TimeLog not found")
    return db_timelog

@router.put("/{timelog_id}", response_model=TimeLogResponse)
def update_timelog(timelog_id: int, timelog: TimeLogUpdate, db: Session = Depends(get_db)):
    db_timelog = timelog_service.update_timelog(db, timelog_id=timelog_id, timelog_update=timelog)
    if db_timelog is None:
        raise HTTPException(status_code=404, detail="TimeLog not found")
    return db_timelog

@router.delete("/{timelog_id}")
def delete_timelog(timelog_id: int, db: Session = Depends(get_db)):
    success = timelog_service.delete_timelog(db, timelog_id=timelog_id)
    if not success:
        raise HTTPException(status_code=404, detail="TimeLog not found")
    return {"message": "TimeLog deleted successfully"}
