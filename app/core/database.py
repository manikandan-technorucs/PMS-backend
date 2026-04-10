"""
Async database engine and session factory.

Migrated from sync SQLAlchemy to fully async using:
  - create_async_engine  (aiomysql driver)
  - async_sessionmaker   (yields AsyncSession)
  - Async-safe get_db dependency

All services and endpoints depend on AsyncSession via get_db().
"""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy import Column, Boolean, DateTime
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import logging

from app.core.config import settings

logger = logging.getLogger("app.database")

# ── SSL for Azure MySQL ───────────────────────────────────────────────────────
connect_args: dict = {}
if "azure" in settings.MYSQL_SERVER:
    connect_args = {"ssl": {"ssl_mode": "REQUIRED"}}

# ── Async Engine ──────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=30,
    pool_recycle=280,   # Stay under Azure MySQL's 300 s idle timeout
    pool_timeout=20,
    echo=False,
)

# ── Session Factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ── ORM Base ──────────────────────────────────────────────────────────────────
Base = declarative_base()


# ── Audit Mixin (mixed into every domain model) ───────────────────────────────
class AuditMixin:
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=None,
        onupdate=func.now(),
        nullable=True,
    )
    is_active  = Column(Boolean, default=True,  nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


# ── FastAPI Dependency ────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async session dependency. Services manage their own commits."""
    async with AsyncSessionLocal() as session:
        yield session
