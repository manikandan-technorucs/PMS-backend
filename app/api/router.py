from fastapi import APIRouter
from app.api.endpoints import users, teams, masters, projects, tasks, issues, timelogs, reports, milestones, task_lists

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(masters.router, prefix="/masters", tags=["masters"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(issues.router, prefix="/issues", tags=["issues"])
api_router.include_router(timelogs.router, prefix="/timelogs", tags=["timelogs"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(milestones.router, prefix="/milestones", tags=["milestones"])
api_router.include_router(task_lists.router, prefix="/task-lists", tags=["task-lists"])
