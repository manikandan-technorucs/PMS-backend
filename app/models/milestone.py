from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="milestones")
    status = relationship("Status")
    owner = relationship("User")
