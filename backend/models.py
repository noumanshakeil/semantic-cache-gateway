from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class CacheEntry(Base):
    __tablename__ = "cache_entries"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    prompt_norm: Mapped[str] = mapped_column(Text)
    prompt_raw: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    hits: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class CacheQueryLog(Base):
    __tablename__ = "cache_query_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prompt: Mapped[str] = mapped_column(Text)
    hit: Mapped[int] = mapped_column(Integer)
    similarity: Mapped[float] = mapped_column(Float, default=0.0)
    entry_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
