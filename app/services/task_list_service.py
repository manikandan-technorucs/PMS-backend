from sqlalchemy.orm import Session, joinedload
from app.models.task_list import TaskList
from app.schemas.task_list import TaskListCreate, TaskListUpdate

def get_task_list(db: Session, task_list_id: int):
    return db.query(TaskList).options(
        joinedload(TaskList.project)
    ).filter(TaskList.id == task_list_id).first()

def get_task_lists(db: Session, project_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(TaskList).options(
        joinedload(TaskList.project)
    )
    if project_id:
        query = query.filter(TaskList.project_id == project_id)
    return query.offset(skip).limit(limit).all()

def create_task_list(db: Session, task_list: TaskListCreate):
    db_task_list = TaskList(
        name=task_list.name,
        description=task_list.description,
        project_id=task_list.project_id
    )
    db.add(db_task_list)
    db.commit()
    db.refresh(db_task_list)
    return get_task_list(db, db_task_list.id)

def update_task_list(db: Session, task_list_id: int, task_list_update: TaskListUpdate):
    db_task_list = db.query(TaskList).filter(TaskList.id == task_list_id).first()
    if not db_task_list:
        return None
    
    update_data = task_list_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task_list, key, value)
        
    db.commit()
    db.refresh(db_task_list)
    return get_task_list(db, db_task_list.id)

def delete_task_list(db: Session, task_list_id: int):
    db_task_list = db.query(TaskList).filter(TaskList.id == task_list_id).first()
    if db_task_list:
        db.delete(db_task_list)
        db.commit()
        return True
    return False

def search_task_lists(db: Session, query: str, project_id: int = None, limit: int = 20):
    if not query:
        return []
    q = f"%{query}%"
    from sqlalchemy import or_
    query_obj = db.query(TaskList).options(joinedload(TaskList.project))
    if project_id:
        query_obj = query_obj.filter(TaskList.project_id == project_id)
    return query_obj.filter(TaskList.name.ilike(q)).limit(limit).all()
