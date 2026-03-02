from sqlalchemy.orm import Session, joinedload
from app.models.timelog import TimeLog
from app.schemas.timelog import TimeLogCreate, TimeLogUpdate

def get_timelog(db: Session, timelog_id: int):
    return db.query(TimeLog).options(
        joinedload(TimeLog.user),
        joinedload(TimeLog.project),
        joinedload(TimeLog.task),
        joinedload(TimeLog.issue)
    ).filter(TimeLog.id == timelog_id).first()

def get_timelogs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(TimeLog).options(
        joinedload(TimeLog.user),
        joinedload(TimeLog.project),
        joinedload(TimeLog.task),
        joinedload(TimeLog.issue)
    ).offset(skip).limit(limit).all()

def create_timelog(db: Session, timelog: TimeLogCreate):
    db_timelog = TimeLog(
        user_id=timelog.user_id,
        project_id=timelog.project_id,
        task_id=timelog.task_id,
        issue_id=timelog.issue_id,
        date=timelog.date,
        hours=timelog.hours,
        description=timelog.description
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
