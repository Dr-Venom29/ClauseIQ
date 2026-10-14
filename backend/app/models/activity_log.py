import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.models.document import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True) # upload, summary, checklist, risk_analysis, comparison, chat, export
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
