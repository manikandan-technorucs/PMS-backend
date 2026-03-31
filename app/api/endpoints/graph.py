from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.services.graph_service import search_azure_users
from app.core.security import allow_manager_plus
from app.core.database import get_db

router = APIRouter()


@router.get(
    "/search-users",
    response_model=List[Dict[str, Any]],
    dependencies=[Depends(allow_manager_plus)],
)
def search_users(
    q: str = Query(..., min_length=2, description="Search Entra ID by displayName or mail"),
    db: Session = Depends(get_db),
):
    """
    Search Microsoft Entra ID for users.

    Returns a list of dicts with keys: id, displayName, mail.

    JIT Identity Provisioning: any user returned by Graph who is not yet
    present in the local MySQL users table is automatically upserted so
    that subsequent project/task assignment calls never hit a missing FK.

    The ConsistencyLevel: eventual header and $count=true query param are
    injected inside graph_service.search_azure_users to satisfy MS Graph's
    advanced filter prerequisites and prevent 403 errors.
    """
    try:
        return search_azure_users(q, db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
