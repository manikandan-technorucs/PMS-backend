from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.task_list import TaskList
from app.schemas.task_list import TaskListCreate, TaskListUpdate
from app.utils.audit_utils import write_audit, capture_audit_details

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

def create_task_list(db: Session, task_list: TaskListCreate, actor_id: Optional[str] = None):
    db_task_list = TaskList(
        name=task_list.name,
        description=task_list.description,
        project_id=task_list.project_id
    )
    db.add(db_task_list)
    db.flush()

    write_audit(db, actor_id, "CREATE", "task_lists",
                resource_id=task_list.project_id or db_task_list.id,
                record_id=db_task_list.id,
                details=[{"field_name": "name", "old_value": None, "new_value": task_list.name}])

    db.commit()
    db.refresh(db_task_list)
    return get_task_list(db, db_task_list.id)

def update_task_list(db: Session, task_list_id: int, task_list_update: TaskListUpdate, actor_id: Optional[str] = None):
    db_task_list = db.query(TaskList).filter(TaskList.id == task_list_id).first()
    if not db_task_list:
        return None

    update_data = task_list_update.model_dump(exclude_unset=True)
    changes = capture_audit_details(db_task_list, update_data)

    for key, value in update_data.items():
        setattr(db_task_list, key, value)

    write_audit(db, actor_id, "UPDATE", "task_lists",
                resource_id=db_task_list.project_id or task_list_id,
                record_id=task_list_id,
                details=changes)

    db.commit()
    db.refresh(db_task_list)
    return get_task_list(db, db_task_list.id)

def delete_task_list(db: Session, task_list_id: int, actor_id: Optional[str] = None):
    db_task_list = db.query(TaskList).filter(TaskList.id == task_list_id).first()
    if db_task_list:
        write_audit(db, actor_id, "DELETE", "task_lists",
                    resource_id=db_task_list.project_id or task_list_id,
                    record_id=task_list_id,
                    details=[{"field_name": "name", "old_value": db_task_list.name, "new_value": None}])
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
