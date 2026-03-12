from sqlalchemy import Column, Integer, String, ForeignKey, Table, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

user_team_link = Table(
    "user_team_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("team_id", Integer, ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True),
)

user_skill_link = Table(
    "user_skill_link",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(50), unique=True, index=True, nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    job_title = Column(String(100), nullable=True)
    join_date = Column(Date, default=func.current_date(), nullable=True)
    
    # Profile Details
    display_name = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    language = Column(String(50), default="English", nullable=True)
    timezone = Column(String(100), default="Asia/Kolkata", nullable=True)
    
    # O365 Sync & External flags
    o365_id = Column(String(255), unique=True, index=True, nullable=True)
    is_synced = Column(Boolean, default=False)
    is_external = Column(Boolean, default=False) # True for Customers
    
    # Foreign Keys
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    dept_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    status_id = Column(Integer, ForeignKey("user_statuses.id", ondelete="SET NULL"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    role = relationship("Role", lazy="joined")
    department = relationship("Department", lazy="joined")
    status = relationship("UserStatus", lazy="joined")
    location = relationship("Location", lazy="joined")
    manager = relationship("User", remote_side=[id])
    
    # Many-to-Many
    teams = relationship("Team", secondary=user_team_link, back_populates="members")
    skills = relationship("Skill", secondary=user_skill_link, backref="users")
    projects = relationship("Project", secondary="project_users", back_populates="users")
    
    # Reverse relationship for teams where this user is admin/lead
    managed_teams = relationship("Team", back_populates="lead", foreign_keys="Team.lead_id")

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
