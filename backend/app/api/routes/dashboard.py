from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.dashboard_service import DashboardService
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user-scoped workspace stats.
    """
    dashboard_service = DashboardService(db)
    stats = await dashboard_service.get_overview(current_user.id)
    return stats
