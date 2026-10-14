from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("")
def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    metrics_repo = MetricsRepository(db)
    metrics_data = metrics_repo.get_all(user_id=current_user.id)
    
    stats = {
        "uploads": 0,
        "chat": 0,
        "gemini_call": 0,
        "cache_hit": 0,
        "cache_miss": 0
    }
    
    for m in metrics_data:
        if m.action in stats:
            stats[m.action] += m.count
            
    total_analyses = stats["cache_hit"] + stats["cache_miss"]
    savings_pct = (stats["cache_hit"] / total_analyses * 100) if total_analyses > 0 else 0
            
    return {
        "metrics": stats,
        "api_savings_percentage": round(savings_pct, 2)
    }

@router.get("/user")
def get_user_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    metrics_repo = MetricsRepository(db)
    activity_repo = ActivityLogRepository(db)
    
    # 1. Fetch system metrics from metrics repository
    metrics_data = metrics_repo.get_all(user_id=current_user.id)
    
    sys_stats = {
        "gemini_call": 0,
        "cache_hit": 0,
        "cache_miss": 0
    }
    
    for m in metrics_data:
        if m.action in sys_stats:
            sys_stats[m.action] += m.count
            
    # 2. Fetch user-facing metrics counts from activity log logs
    logs = activity_repo.get_user_logs(user_id=current_user.id)
    
    act_counts = {
        "upload": 0,
        "chat": 0,
        "comparison": 0,
        "export": 0
    }
    
    for log in logs:
        if log.action in act_counts:
            act_counts[log.action] += 1
            
    # Calculate savings percentage
    total_cache_attempts = sys_stats["cache_hit"] + sys_stats["cache_miss"]
    savings_percentage = (sys_stats["cache_hit"] / total_cache_attempts * 100) if total_cache_attempts > 0 else 0
    
    return {
        "uploads": act_counts["upload"],
        "chats": act_counts["chat"],
        "comparisons": act_counts["comparison"],
        "exports": act_counts["export"],
        "gemini_calls": sys_stats["gemini_call"],
        "cache_hits": sys_stats["cache_hit"],
        "cache_misses": sys_stats["cache_miss"],
        "savings_percentage": round(savings_percentage, 2)
    }
