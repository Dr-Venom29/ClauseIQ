from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces import IDashboardRepository
from app.models.document import Document, AnalysisSnapshot
from app.models.activity_log import ActivityLog

class DashboardRepository(BaseRepository, IDashboardRepository):
    def count_documents(self, user_id: str) -> int:
        return self.db.query(Document).filter(Document.user_id == user_id).count()

    def count_analyses(self, user_id: str) -> int:
        return self.db.query(AnalysisSnapshot).filter(AnalysisSnapshot.user_id == user_id).count()

    def count_chats(self, user_id: str) -> int:
        return self.db.query(ActivityLog).filter(
            ActivityLog.action == "chat",
            ActivityLog.user_id == user_id
        ).count()

    def count_comparisons(self, user_id: str) -> int:
        return self.db.query(ActivityLog).filter(
            ActivityLog.action == "comparison",
            ActivityLog.user_id == user_id
        ).count()
