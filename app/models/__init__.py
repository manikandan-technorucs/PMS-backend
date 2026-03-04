# Import all models here so Alembic and SQLAlchemy can discover them automatically
from app.models.masters import Department, Location, UserStatus, Skill, Status, Priority
from app.models.roles import Role
from app.models.user import User, user_team_link
from app.models.team import Team
from app.models.project import Project, project_users
from app.models.task import Task
from app.models.issue import Issue
from app.models.timelog import TimeLog
from app.models.milestone import Milestone
from app.models.task_list import TaskList
from app.models.timesheet import Timesheet
from app.models.document import Document

# The order of these imports doesn't heavily matter for sqlalchemy base 
# as long as they are imported before Base.metadata.create_all is called.
