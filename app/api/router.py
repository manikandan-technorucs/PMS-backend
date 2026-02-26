from fastapi import APIRouter
from app.api.endpoints import users, teams, masters

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(masters.router, prefix="/masters", tags=["masters"])
