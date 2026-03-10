from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.search_service import search_service

router = APIRouter()

@router.get("/", response_model=List[Any])
def global_search(
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1),
    limit: int = Query(15, gt=0, le=50)
) -> Any:
    """
    Search across projects, tasks, and issues.
    """
    return search_service.global_search(db, query=q, limit=limit)
