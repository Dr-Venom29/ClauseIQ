from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.checklist_service import ChecklistService
from app.schemas.analysis import ChecklistItem
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.activity_service import ActivityService

router = APIRouter()

@router.get("/documents/{document_id}/checklist", response_model=List[ChecklistItem])
async def generate_checklist(
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
        checklist_service = ChecklistService(db)
        result = await checklist_service.generate_checklist(document_id, user_id=current_user.id)
        
        # Log the activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(user_id=current_user.id, action="checklist", document_id=document_id)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
