from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.core.database import AuditMixin, Base

class Issue(AuditMixin, Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Email-as-Key Foreign Keys
    reporter_email = Column(String(255), ForeignKey("users.email"), nullable=True)
    assignee_email = Column(String(255), ForeignKey("users.email"), nullable=True)
    
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)
    priority_id = Column(Integer, ForeignKey("priorities.id"), nullable=True)

    # Shadow State for Automation (Backend Only)
    previous_status = Column(String(100), nullable=True)

    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    estimated_hours = Column(Numeric(5, 2), nullable=True)
    is_processed = Column(Boolean, default=False)

    # Relationships
    project = relationship("Project", back_populates="issues")
    reporter = relationship("User", foreign_keys=[reporter_email])
    assignee = relationship("User", foreign_keys=[assignee_email])
    status = relationship("Status")
    priority = relationship("Priority")
    
    # Multi-Media Issue & Document Engine Link
    documents = relationship("Document", secondary="issue_document_link", back_populates="issues")
