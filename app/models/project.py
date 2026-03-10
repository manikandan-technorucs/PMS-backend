from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Float, Table, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

project_users = Table(
    "project_users",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    client = Column(String(255), nullable=True)
    
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    priority_id = Column(Integer, ForeignKey("priorities.id"), nullable=True)
    dept_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    estimated_hours = Column(Float, default=0.0)
    
    # Zoho Features
    is_template = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    group_id = Column(Integer, ForeignKey("project_groups.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    manager = relationship("User", foreign_keys=[manager_id])
    status = relationship("Status")
    priority = relationship("Priority")
    department = relationship("Department")
    team = relationship("Team")
    group = relationship("ProjectGroup", back_populates="projects")
    
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    task_lists = relationship("TaskList", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    users = relationship("User", secondary=project_users, back_populates="projects")
