# Import all models here so Alembic and SQLAlchemy can discover them automatically
from app.models.masters import Department, Location, UserStatus
from app.models.roles import Role
from app.models.user import User, user_team_link
from app.models.team import Team

# The order of these imports doesn't heavily matter for sqlalchemy base 
# as long as they are imported before Base.metadata.create_all is called.
