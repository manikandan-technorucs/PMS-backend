from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class TimeLog(Base):
    __tablename__ = "timelogs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)
    
    date = Column(Date, nullable=False)
    hours = Column(Numeric(5, 2), nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    user = relationship("User")
    project = relationship("Project")
    task = relationship("Task", back_populates="timelogs")
    issue = relationship("Issue")
