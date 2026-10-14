from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces import IActivityLogRepository
from app.models.activity_log import ActivityLog
from app.models.document import Document
from typing import List, Optional

class ActivityLogRepository(BaseRepository, IActivityLogRepository):
    def log_activity(self, user_id: str, action: str, document_id: Optional[str] = None) -> ActivityLog:
        log_entry = ActivityLog(
            user_id=user_id,
            action=action,
            document_id=document_id
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def get_user_logs(self, user_id: str) -> List[ActivityLog]:
        return self.db.query(ActivityLog).filter(ActivityLog.user_id == user_id).order_by(ActivityLog.timestamp.desc()).all()

    def delete_document_logs(self, document_id: str, user_id: str) -> None:
        self.db.query(ActivityLog).filter(
            ActivityLog.document_id == document_id,
            ActivityLog.user_id == user_id
        ).delete(synchronize_session=False)
        self.db.commit()

    def get_recent_activities(self, user_id: str, limit: int = 20) -> List[dict]:
        results = self.db.query(
            ActivityLog.action,
            Document.filename.label("document_name"),
            ActivityLog.timestamp
        ).outerjoin(
            Document, ActivityLog.document_id == Document.id
        ).filter(
            ActivityLog.user_id == user_id
        ).order_by(
            ActivityLog.timestamp.desc()
        ).limit(limit).all()
        
        return [
            {
                "action": r.action,
                "document_name": r.document_name or "",
                "timestamp": r.timestamp.isoformat() if r.timestamp else None
            }
            for r in results
        ]
