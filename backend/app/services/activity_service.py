from app.repositories.activity_log_repository import ActivityLogRepository
from typing import Optional, List

class ActivityService:
    def __init__(self, db):
        self.db = db
        self.activity_log_repo = ActivityLogRepository(db)

    async def log_activity(self, user_id: str, action: str, document_id: Optional[str] = None):
        return self.activity_log_repo.log_activity(user_id=user_id, action=action, document_id=document_id)

    async def get_recent_activity(self, user_id: str, limit: int = 20) -> List[dict]:
        return self.activity_log_repo.get_recent_activities(user_id=user_id, limit=limit)
