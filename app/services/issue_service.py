from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueUpdate
from app.utils.ids import generate_public_id
from app.services.automation_engine import execute_automation_event
from app.models.user import User

def get_issue(db: Session, issue_id: int):
    return db.query(Issue).options(
        joinedload(Issue.project),
        joinedload(Issue.reporter),
        joinedload(Issue.assignee),
        joinedload(Issue.status),
        joinedload(Issue.priority)
    ).filter(Issue.id == issue_id).first()

def get_issues(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    project_id: int = None,
    status_ids: List[int] = None,
    priority_ids: List[int] = None,
    assignee_ids: List[int] = None
):
    query = db.query(Issue).options(
        joinedload(Issue.project),
        joinedload(Issue.reporter),
        joinedload(Issue.assignee),
        joinedload(Issue.status),
        joinedload(Issue.priority)
    )
    if project_id is not None:
        query = query.filter(Issue.project_id == project_id)
    if status_ids:
        query = query.filter(Issue.status_id.in_(status_ids))
    if priority_ids:
        query = query.filter(Issue.priority_id.in_(priority_ids))
    if assignee_ids:
        query = query.filter(Issue.assignee_id.in_(assignee_ids))
        
    return query.offset(skip).limit(limit).all()

def create_issue(db: Session, issue: IssueCreate):
    public_id = generate_public_id("ISS-")
    db_issue = Issue(
        public_id=public_id,
        title=issue.title,
        description=issue.description,
        project_id=issue.project_id,
        reporter_id=issue.reporter_id,
        assignee_id=issue.assignee_id,
        status_id=issue.status_id,
        priority_id=issue.priority_id,
        start_date=issue.start_date,
        end_date=issue.end_date,
        estimated_hours=issue.estimated_hours
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)

    # Trigger Automations: ISSUE_CREATED
    if db_issue.assignee_id:
        assignee = db.query(User).filter(User.id == db_issue.assignee_id).first()
        if assignee and assignee.email:
            payload = {
                "issue_id": db_issue.public_id,
                "issue_title": db_issue.title,
                "project_name": db_issue.project.name if db_issue.project else "Unassigned",
                "assignee_name": f"{assignee.first_name} {assignee.last_name}"
            }
            execute_automation_event(
                db=db,
                event_name="ISSUE_CREATED",
                payload=payload,
                email_recipient=assignee.email,
                entity_id=str(db_issue.id)
            )

    return get_issue(db, db_issue.id)

def update_issue(db: Session, issue_id: int, issue_update: IssueUpdate):
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        return None
    
    update_data = issue_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_issue, key, value)
        
    db.commit()
    db.refresh(db_issue)
    return get_issue(db, db_issue.id)

def delete_issue(db: Session, issue_id: int):
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if db_issue:
        db.delete(db_issue)
        db.commit()
        return True
    return False

def search_issues(db: Session, query: str, project_id: int = None, limit: int = 20):
    if not query:
        return []
    q = f"%{query}%"
    from sqlalchemy import or_
    query_obj = db.query(Issue).options(
        joinedload(Issue.project),
        joinedload(Issue.reporter),
        joinedload(Issue.assignee),
        joinedload(Issue.status)
    )
    if project_id:
        query_obj = query_obj.filter(Issue.project_id == project_id)
    
    return query_obj.filter(
        or_(
            Issue.title.ilike(q),
            Issue.public_id.ilike(q)
        )
    ).limit(limit).all()
