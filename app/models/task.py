from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    task_list_id = Column(Integer, ForeignKey("task_lists.id", ondelete="SET NULL"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    priority_id = Column(Integer, ForeignKey("priorities.id"), nullable=True)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    progress = Column(Integer, default=0)
    estimated_hours = Column(Numeric(5, 2), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    task_list = relationship("TaskList", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])
    status = relationship("Status")
    priority = relationship("Priority")
    
    timelogs = relationship("TimeLog", back_populates="task", cascade="all, delete-orphan")
