"""
Template system models — ProjectTemplate and TemplateTask.

A ProjectTemplate is a reusable blueprint.
When a Project is created with template_id set, the service layer
clones all TemplateTask rows into real Task rows.
"""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, AuditMixin


class ProjectTemplate(AuditMixin, Base):
    __tablename__ = "project_templates"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Who created this template — optional (admin bulk imports may skip)
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    tasks      = relationship(
        "TemplateTask",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateTask.order_index",
        lazy="selectin",
    )


class TemplateTask(Base):
    """
    A reusable task definition belonging to a ProjectTemplate.
    Has no AuditMixin — templates are admin-managed, not audited per-row.
    """
    __tablename__ = "template_tasks"

    id              = Column(Integer, primary_key=True, index=True)
    template_id     = Column(
        Integer,
        ForeignKey("project_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title           = Column(String(255), nullable=False)
    description     = Column(Text, nullable=True)
    estimated_hours = Column(Numeric(5, 2), nullable=True)
    priority_id     = Column(Integer, ForeignKey("priorities.id", ondelete="SET NULL"), nullable=True)
    order_index     = Column(Integer, default=0, nullable=False)

    template = relationship("ProjectTemplate", back_populates="tasks")
    priority = relationship("Priority", lazy="selectin")
