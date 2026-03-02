from sqlalchemy.orm import Session, joinedload
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.ids import generate_public_id

def get_task(db: Session, task_id: int):
    return db.query(Task).options(
        joinedload(Task.project),
        joinedload(Task.assignee),
        joinedload(Task.status),
        joinedload(Task.priority)
    ).filter(Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).options(
        joinedload(Task.project),
        joinedload(Task.assignee),
        joinedload(Task.status),
        joinedload(Task.priority)
    ).offset(skip).limit(limit).all()

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
