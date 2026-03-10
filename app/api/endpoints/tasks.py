from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services import task_service

router = APIRouter()

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return task_service.create_task(db=db, task=task)

@router.post("/bulk", response_model=List[TaskResponse])
def bulk_create_tasks(tasks: List[TaskCreate], db: Session = Depends(get_db)):
    return [task_service.create_task(db=db, task=t) for t in tasks]

@router.get("/", response_model=List[TaskResponse])
def read_tasks(
    skip: int = 0, 
    limit: int = 100, 
    project_id: int = None, 
    status_id: List[int] = Query(None),
    priority_id: List[int] = Query(None),
    assignee_id: List[int] = Query(None),
    db: Session = Depends(get_db)
):
    return task_service.get_tasks(
        db, 
        skip=skip, 
        limit=limit, 
        project_id=project_id,
        status_ids=status_id,
        priority_ids=priority_id,
        assignee_ids=assignee_id
    )

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = task_service.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = task_service.update_task(db, task_id=task_id, task_update=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = task_service.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
