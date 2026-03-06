from sqlalchemy.orm import Session
from app.models.timesheet import Timesheet
from app.schemas.timesheet import TimesheetCreate, TimesheetUpdate
from app.services.automation_engine import execute_automation_event

def get_timesheets(db: Session, skip: int = 0, limit: int = 100, project_id: int = None, user_id: int = None):
    query = db.query(Timesheet)
    if project_id:
        query = query.filter(Timesheet.project_id == project_id)
    if user_id:
        query = query.filter(Timesheet.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def get_timesheet(db: Session, timesheet_id: int):
    return db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()

def create_timesheet(db: Session, timesheet: TimesheetCreate):
    db_timesheet = Timesheet(
        name=timesheet.name,
        start_date=timesheet.start_date,
        end_date=timesheet.end_date,
        project_id=timesheet.project_id,
        user_id=timesheet.user_id,
        billing_type=timesheet.billing_type,
        total_hours=timesheet.total_hours,
        approval_status=timesheet.approval_status
    )
    db.add(db_timesheet)
    db.commit()
    db.refresh(db_timesheet)
    return db_timesheet

def update_timesheet(db: Session, timesheet_id: int, timesheet_update: TimesheetUpdate):
    db_timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()
    if not db_timesheet:
        return None
    
    old_status = db_timesheet.approval_status
    update_data = timesheet_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_timesheet, key, value)
        
    db.commit()
    db.refresh(db_timesheet)

    # Trigger Automations: TIMESHEET_STATUS_UPDATED
    if "approval_status" in update_data and update_data["approval_status"] != old_status:
        if db_timesheet.user and db_timesheet.user.email:
            payload = {
                "timesheet_name": db_timesheet.name,
                "old_status": old_status,
                "new_status": db_timesheet.approval_status,
                "user_name": f"{db_timesheet.user.first_name} {db_timesheet.user.last_name}"
            }
            execute_automation_event(
                db=db,
                event_name="TIMESHEET_STATUS_UPDATED",
                payload=payload,
                email_recipient=db_timesheet.user.email,
                entity_id=str(db_timesheet.id)
            )

    return db_timesheet

def delete_timesheet(db: Session, timesheet_id: int):
    db_timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()
    if not db_timesheet:
        return False
    
    db.delete(db_timesheet)
    db.commit()
    return True
