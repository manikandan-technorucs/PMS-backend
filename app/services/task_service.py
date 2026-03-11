from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.ids import generate_public_id
from app.services.automation_engine import execute_automation_event
from app.models.user import User

def get_task(db: Session, task_id: int):
    return db.query(Task).options(
        joinedload(Task.project),
        joinedload(Task.assignee),
        joinedload(Task.status),
        joinedload(Task.priority)
    ).filter(Task.id == task_id).first()

def get_tasks(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    project_id: int = None,
    status_ids: List[int] = None,
    priority_ids: List[int] = None,
    assignee_ids: List[int] = None
):
    query = db.query(Task).options(
        joinedload(Task.project),
        joinedload(Task.assignee),
        joinedload(Task.status),
        joinedload(Task.priority)
    )
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    if status_ids:
        query = query.filter(Task.status_id.in_(status_ids))
    if priority_ids:
        query = query.filter(Task.priority_id.in_(priority_ids))
    if assignee_ids:
        query = query.filter(Task.assignee_id.in_(assignee_ids))
        
    return query.offset(skip).limit(limit).all()

def create_task(db: Session, task: TaskCreate):
    public_id = generate_public_id("TSK-")
    db_task = Task(
        public_id=public_id,
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        assignee_id=task.assignee_id,
        task_list_id=task.task_list_id,
        status_id=task.status_id,
        priority_id=task.priority_id,
        due_date=task.due_date,
        start_date=task.start_date,
        end_date=task.end_date,
        progress=task.progress,
        estimated_hours=task.estimated_hours
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Trigger Automations: TASK_ASSIGNED
    if db_task.assignee_id:
        assignee = db.query(User).filter(User.id == db_task.assignee_id).first()
        if assignee and assignee.email:
            payload = {
                "task_id": db_task.public_id,
                "task_title": db_task.title,
                "project_name": db_task.project.name if db_task.project else "Unassigned",
                "assignee_name": f"{assignee.first_name} {assignee.last_name}"
            }
            execute_automation_event(
                db=db,
                event_name="TASK_ASSIGNED",
                payload=payload,
                email_recipient=assignee.email,
                entity_id=str(db_task.id)
            )

    return get_task(db, db_task.id)

def update_task(db: Session, task_id: int, task_update: TaskUpdate):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    db.commit()
    db.refresh(db_task)
    return get_task(db, db_task.id)

def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False
