import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, UTC

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    filename = Column(String, index=True)
    content_hash = Column(String, unique=False, index=True) # allow same content for different versions just in case
    storage_path = Column(String)
    version_number = Column(Integer, default=1)
    parent_document_id = Column(String, nullable=True, index=True)
    upload_timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String, index=True)
    page = Column(Integer)
    section = Column(String, nullable=True)
    content = Column(Text)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

class Clause(Base):
    __tablename__ = "clauses"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String, index=True)
    clause_identifier = Column(String)
    title = Column(String)
    content = Column(Text)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

class AnalysisSnapshot(Base):
    __tablename__ = "analysis_snapshots"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String, index=True)
    document_hash = Column(String, index=True)
    analysis_type = Column(String, index=True) # summary, checklist, risks, comparison
    result_json = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

class Metrics(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action = Column(String, index=True) # e.g. upload, chat, gemini_call, cache_hit, cache_miss
    count = Column(Integer, default=1)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
