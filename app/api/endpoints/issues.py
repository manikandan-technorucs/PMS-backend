from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_sync_db
from sqlalchemy import select, or_, exists
from app.core.security import allow_authenticated, is_employee_only, is_full_access, allow_issue_create, allow_issue_view, allow_issue_delete, check_issue_owner_or_lead

from app.models.user import User

from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse, IssueListResponse
from app.services import issue_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])


@router.post("/", response_model=IssueResponse, dependencies=[Depends(allow_issue_create)])
def create_issue(
    issue: IssueCreate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_issue_create),
):

    if not issue.reporter_id:
        issue.reporter_id = current_user.id
    return issue_service.create_issue(
        db=db,
        issue=issue,
        actor_id=current_user.o365_id or str(current_user.id),
        created_by_id=current_user.id,
    )


@router.post("/bulk", response_model=List[IssueResponse], dependencies=[Depends(allow_issue_create)])
def bulk_create_issues(
    issues: List[IssueCreate],
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_issue_create),
):
    results = []
    for i in issues:
        if not i.reporter_id:
            i.reporter_id = current_user.id
        results.append(
            issue_service.create_issue(
                db=db, issue=i,
                actor_id=current_user.o365_id or str(current_user.id),
                created_by_id=current_user.id,
            )
        )
    return results


@router.get("/search", response_model=List[IssueResponse])
def search_issues(
    q: str = Query(..., min_length=1),
    project_id: Optional[int] = Query(None),
    limit: int = 20,
    db: Session = Depends(get_sync_db),
):
    return issue_service.search_issues(db, query=q, project_id=project_id, limit=limit)


@router.get("/", response_model=IssueListResponse)
def read_issues(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    status_id: Optional[List[int]] = Query(None),
    priority_id: Optional[List[int]] = Query(None),
    severity_id: Optional[List[int]] = Query(None),
    assignee_email: Optional[List[str]] = Query(None),
    search: Optional[str] = None,
    milestone_id: Optional[int] = Query(None),
    db: Session = Depends(get_sync_db),

    current_user=Depends(allow_issue_view),
):

    if not is_full_access(current_user):
        if project_id:
            from app.models.project import ProjectMember
            from app.models.issue import Issue

            
            # Member can see all project issues
            is_member = db.execute(
                select(ProjectMember).where(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == current_user.id
                )
            ).first() is not None
            
            if not is_member:
                # Not a member, but maybe assigned to some issues in this project?
                # We'll filter by assignee_email in the service
                assignee_email = [current_user.email]
            else:
                assignee_email = None
        else:
            # No project_id, show only assigned issues globally
            assignee_email = [current_user.email]


    return issue_service.get_issues(
        db,
        skip=skip,
        limit=limit,
        project_id=project_id,
        status_ids=status_id,
        priority_ids=priority_id,
        severity_ids=severity_id,
        assignee_emails=assignee_email,
        search=search,
        milestone_id=milestone_id,
    )



@router.get("/{issue_id}", response_model=IssueResponse)
def read_issue(
    issue_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_issue_view),
):
    db_issue = issue_service.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    if not is_full_access(current_user):
        from app.models.issue import issue_assignees
        
        # Check if user has access: reporter, assignee, or co-assignee

        is_co_assignee = db.execute(
            select(exists().where(
                issue_assignees.c.issue_id == issue_id,
                issue_assignees.c.user_id == current_user.id
            ))
        ).scalar()
        
        has_access = (
            db_issue.reporter_id == current_user.id or 
            db_issue.assignee_id == current_user.id or 
            is_co_assignee
        )
        
        if not has_access:
            # Also check if they are a project member
            from app.models.project import ProjectMember
            is_member = db.execute(
                select(ProjectMember).where(
                    ProjectMember.project_id == db_issue.project_id,
                    ProjectMember.user_id == current_user.id
                )
            ).first() is not None
            
            if not is_member:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: you are not assigned to this issue and not a project member.",
                )
    return db_issue

    return db_issue


@router.put("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue: IssueUpdate,
    db: Session = Depends(get_sync_db),
    current_user=Depends(check_issue_owner_or_lead),
):
    db_issue = issue_service.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    updated = issue_service.update_issue(
        db,
        issue_id=issue_id,
        issue_update=issue,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return updated


@router.delete("/{issue_id}", status_code=204, dependencies=[Depends(allow_issue_delete)])
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_sync_db),
    current_user=Depends(allow_issue_delete),
):
    success = issue_service.delete_issue(
        db,
        issue_id=issue_id,
        actor_id=current_user.o365_id or str(current_user.id),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Issue not found")
