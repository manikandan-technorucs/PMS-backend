from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.project import Project
from app.models.task import Task
from app.models.issue import Issue
from app.models.timelog import TimeLog

router = APIRouter()

@router.get("/summary")
def get_report_summary(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    total_tasks = db.query(Task).count()
    total_issues = db.query(Issue).count()
    total_hours_logged = db.query(func.sum(TimeLog.hours)).scalar() or 0.0
    
    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "total_issues": total_issues,
        "total_hours_logged": float(total_hours_logged)
    }
