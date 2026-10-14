from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.summary_service import SummaryService
from app.schemas.analysis import SummaryResponse
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.activity_service import ActivityService

router = APIRouter()

@router.get("/documents/{document_id}/summary", response_model=SummaryResponse)
async def generate_summary(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc_repo = DocumentRepository(db)
    doc = doc_repo.get_by_id(document_id, user_id=None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")

    try:
        summary_service = SummaryService(db)
        result = await summary_service.generate_summary(document_id, user_id=current_user.id)
        
        # Log the activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(user_id=current_user.id, action="summary", document_id=document_id)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
