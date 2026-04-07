from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base, AuditMixin

class Role(AuditMixin, Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)
    permissions = Column(JSON, default=dict)

    users = relationship("User", back_populates="role")

    @property
    def users_count(self) -> int:
        return len(self.users)
