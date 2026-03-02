from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse
from app.services import issue_service

router = APIRouter()

@router.post("/", response_model=IssueResponse)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    return issue_service.create_issue(db=db, issue=issue)

@router.get("/", response_model=List[IssueResponse])
def read_issues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return issue_service.get_issues(db, skip=skip, limit=limit)

@router.get("/{issue_id}", response_model=IssueResponse)
def read_issue(issue_id: int, db: Session = Depends(get_db)):
    db_issue = issue_service.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return db_issue

@router.put("/{issue_id}", response_model=IssueResponse)
def update_issue(issue_id: int, issue: IssueUpdate, db: Session = Depends(get_db)):
    db_issue = issue_service.update_issue(db, issue_id=issue_id, issue_update=issue)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return db_issue

@router.delete("/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    success = issue_service.delete_issue(db, issue_id=issue_id)
    if not success:
        raise HTTPException(status_code=404, detail="Issue not found")
    return {"message": "Issue deleted successfully"}
