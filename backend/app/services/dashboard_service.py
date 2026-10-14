from app.repositories.dashboard_repository import DashboardRepository

class DashboardService:
    def __init__(self, db):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)

    async def get_overview(self, user_id: str) -> dict:
        return {
            "total_documents": self.dashboard_repo.count_documents(user_id),
            "total_analyses": self.dashboard_repo.count_analyses(user_id),
            "total_chats": self.dashboard_repo.count_chats(user_id),
            "total_comparisons": self.dashboard_repo.count_comparisons(user_id)
        }
