from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.timesheet import TimesheetCreate, TimesheetUpdate, TimesheetResponse
from app.services import timesheet_service

router = APIRouter()

@router.post("/", response_model=TimesheetResponse)
def create_timesheet(timesheet: TimesheetCreate, db: Session = Depends(get_db)):
    return timesheet_service.create_timesheet(db=db, timesheet=timesheet)

@router.get("/", response_model=List[TimesheetResponse])
def read_timesheets(skip: int = 0, limit: int = 100, project_id: int = None, user_id: int = None, db: Session = Depends(get_db)):
    return timesheet_service.get_timesheets(db, skip=skip, limit=limit, project_id=project_id, user_id=user_id)

@router.get("/{timesheet_id}", response_model=TimesheetResponse)
def read_timesheet(timesheet_id: int, db: Session = Depends(get_db)):
    db_timesheet = timesheet_service.get_timesheet(db, timesheet_id=timesheet_id)
    if db_timesheet is None:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    return db_timesheet

@router.put("/{timesheet_id}", response_model=TimesheetResponse)
def update_timesheet(timesheet_id: int, timesheet: TimesheetUpdate, db: Session = Depends(get_db)):
    db_timesheet = timesheet_service.update_timesheet(db, timesheet_id=timesheet_id, timesheet_update=timesheet)
    if db_timesheet is None:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    return db_timesheet

@router.delete("/{timesheet_id}")
def delete_timesheet(timesheet_id: int, db: Session = Depends(get_db)):
    success = timesheet_service.delete_timesheet(db, timesheet_id=timesheet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    return {"message": "Timesheet deleted successfully"}
