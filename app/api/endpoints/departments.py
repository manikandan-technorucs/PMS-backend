from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import allow_authenticated
from app.schemas.masters import MasterResponse
from app.services import master_service

router = APIRouter(dependencies=[Depends(allow_authenticated)])

@router.get("", response_model=List[MasterResponse])
def read_departments(db: Session = Depends(get_db)):
    return master_service.get_departments(db)

@router.get("/search", response_model=List[MasterResponse])
def search_departments(
    q: str = Query(..., min_length=1),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return master_service.search_departments(db, q, limit)
