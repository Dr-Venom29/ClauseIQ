from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.activity_service import ActivityService
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/activity/recent")
async def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's recent activity logs.
    """
    activity_service = ActivityService(db)
    activities = await activity_service.get_recent_activity(current_user.id)
    return activities
