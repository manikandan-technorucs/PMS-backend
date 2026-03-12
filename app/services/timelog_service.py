from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.models.timelog import TimeLog
from app.models.task import Task
from app.schemas.timelog import TimeLogCreate, TimeLogUpdate

def get_timelog(db: Session, timelog_id: int):
    return db.query(TimeLog).options(
        joinedload(TimeLog.user),
        joinedload(TimeLog.project),
        joinedload(TimeLog.task).joinedload(Task.project),
        joinedload(TimeLog.issue)
    ).filter(TimeLog.id == timelog_id).first()

def get_timelogs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    project_id: int = None,
    user_ids: List[int] = None
):
    query = db.query(TimeLog).options(
        joinedload(TimeLog.user),
        joinedload(TimeLog.project),
        joinedload(TimeLog.task).joinedload(Task.project),
        joinedload(TimeLog.issue)
    )
    if project_id is not None:
        query = query.outerjoin(Task, TimeLog.task_id == Task.id).filter(
            or_(
                TimeLog.project_id == project_id,
                Task.project_id == project_id
            )
        )
    if user_ids:
        query = query.filter(TimeLog.user_id.in_(user_ids))
        
    return query.offset(skip).limit(limit).all()

def create_timelog(db: Session, timelog: TimeLogCreate):
    db_timelog = TimeLog(
        user_id=timelog.user_id,
        project_id=timelog.project_id,
        task_id=timelog.task_id,
        issue_id=timelog.issue_id,
        timesheet_id=timelog.timesheet_id,
        date=timelog.date,
        hours=timelog.hours,
        description=timelog.description,
        log_title=timelog.log_title,
        billing_type=timelog.billing_type,
        approval_status=timelog.approval_status
    )
    db.add(db_timelog)
    db.commit()
    db.refresh(db_timelog)
    return get_timelog(db, db_timelog.id)

def update_timelog(db: Session, timelog_id: int, timelog_update: TimeLogUpdate):
    db_timelog = db.query(TimeLog).filter(TimeLog.id == timelog_id).first()
    if not db_timelog:
        return None
    
    update_data = timelog_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_timelog, key, value)
        
    db.commit()
    db.refresh(db_timelog)
    return get_timelog(db, db_timelog.id)

def delete_timelog(db: Session, timelog_id: int):
    db_timelog = db.query(TimeLog).filter(TimeLog.id == timelog_id).first()
    if db_timelog:
        db.delete(db_timelog)
        db.commit()
        return True
    return False
