from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class EmailTemplate(Base):
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=True) # Future-proofing
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    variables_schema = Column(JSON, nullable=True) # E.g., ["task_name", "assigned_user"]
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    automation_rules = relationship("AutomationRule", back_populates="template")

class AutomationRule(Base):
    __tablename__ = "automation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), index=True, nullable=True)
    
    # E.g., "TASK_ASSIGNED", "ISSUE_CREATED"
    trigger_event = Column(String(100), index=True, nullable=False)
    
    # E.g., {"priority": "High", "status": "Open"}
    conditions_json = Column(JSON, nullable=True)
    
    template_id = Column(Integer, ForeignKey("email_templates.id", ondelete="RESTRICT"), index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    template = relationship("EmailTemplate", back_populates="automation_rules")
    logs = relationship("AutomationLog", back_populates="rule")

class AutomationLog(Base):
    __tablename__ = "automation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # E.g., "SUCCESS", "FAILED", "RETrying"
    execution_status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Used for idempotency (e.g., hash combination of trigger_event + entity_id)
    idempotency_key = Column(String(255), unique=True, index=True, nullable=False)
    
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    rule = relationship("AutomationRule", back_populates="logs")
