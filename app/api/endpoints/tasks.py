from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_sync_db
from app.core.security import (
    allow_authenticated,
    allow_task_create,
    allow_task_view,
    allow_task_delete,
    check_task_owner_or_lead,
    is_employee_only,
    is_full_access,
)
from sqlalchemy import select, or_, exists

from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services import task_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_task_create),
):
    return task_service.create_task(
        db=db,
        task=task,
        actor_id=current_user.o365_id or str(current_user.id),
        created_by_id=current_user.id,
    )


@router.post("/bulk", response_model=List[TaskResponse])
def bulk_create_tasks(
    tasks: List[TaskCreate],
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_task_create),
):
    results = []
    for t in tasks:
        results.append(
            task_service.create_task(
                db=db,
                task=t,
                actor_id=current_user.o365_id or str(current_user.id),
                created_by_id=current_user.id,
            )
        )
    return results


@router.get("/search", response_model=List[TaskResponse])
def search_tasks(
    q: str = Query(..., min_length=1),
    project_id: Optional[int] = Query(None),
    limit: int = 20,
    db: Session = Depends(get_sync_db),
):
    return task_service.search_tasks(db, query=q, project_id=project_id, limit=limit)


@router.get("/", response_model=TaskListResponse)
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    assignee_email: Optional[List[str]] = Query(None),
    status_id: Optional[List[int]] = Query(None),
    priority_id: Optional[List[int]] = Query(None),
    milestone_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_sync_db),

    current_user=Depends(allow_task_view),
):

    from app.core.security import get_user_view_level
    view_level = get_user_view_level(current_user, 'task-view')

    if view_level == 'O':
        # Own: only tasks created by the user or where user is the owner
        assignee_email = [current_user.email]
    elif view_level == 'A':
        # Assigned: tasks assigned to user OR tasks in projects where user is a member
        if project_id:
            from app.models.project import ProjectMember
            is_member = db.execute(
                select(ProjectMember).where(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == current_user.id
                )
            ).first() is not None
            
            if not is_member:
                assignee_email = [current_user.email]
            else:
                assignee_email = None
        else:
            assignee_email = [current_user.email]
    # 'All' => no filtering, use whatever was passed

    return task_service.get_tasks(
        db,
        skip=skip,
        limit=limit,
        project_id=project_id,
        status_ids=status_id,
        priority_ids=priority_id,
        milestone_id=milestone_id,
        assignee_emails=assignee_email,
        search=search,
    )



@router.get("/{task_id}", response_model=TaskResponse)
def read_task(
    task_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_authenticated),
):
    db_task = task_service.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    from app.core.security import get_user_view_level
    view_level = get_user_view_level(current_user, 'task-view')

    if view_level != 'All':
        from app.models.task import task_assignees
        
        # Check if user has access: assignee or co-assignee
        is_co_assignee = db.execute(
            select(exists().where(
                task_assignees.c.task_id == task_id,
                task_assignees.c.user_id == current_user.id
            ))
        ).scalar()

        has_access = (
            db_task.assignee_id == current_user.id or 
            is_co_assignee or
            db_task.created_by_id == current_user.id
        )
        
        if not has_access and view_level == 'A':
            # Also check if they are a project member
            from app.models.project import ProjectMember
            is_member = db.execute(
                select(ProjectMember).where(
                    ProjectMember.project_id == db_task.project_id,
                    ProjectMember.user_id == current_user.id
                )
            ).first() is not None
            
            if is_member:
                has_access = True
                
        if not has_access:
            raise HTTPException(
                status_code=403,
                detail="Access denied: you are not assigned to this task and not a project member.",
            )
    return db_task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_task_owner_or_lead),
):
    updated = task_service.update_task(
        db,
        task_id=task_id,
        task_update=task,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_task_delete),
):
    success = task_service.delete_task(
        db,
        task_id=task_id,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
