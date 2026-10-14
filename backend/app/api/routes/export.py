from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from app.db.session import get_db
from app.services.export_service import ExportService
from app.schemas.analysis import ExportResponse

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.activity_service import ActivityService

router = APIRouter()

@router.post("/documents/{document_id}/export", response_model=ExportResponse)
async def generate_export(
    document_id: str, 
    format: str = "pdf", 
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
        export_service = ExportService(db)
        result = await export_service.export_report(document_id, user_id=current_user.id, export_format=format)
        
        # Log the activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(user_id=current_user.id, action="export", document_id=document_id)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/download/{filename}")
async def download_export(filename: str):
    file_path = os.path.join("exports", filename)
    if os.path.exists(file_path):
        if filename.endswith(".json"):
            media_type = "application/json"
        elif filename.endswith(".docx"):
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            media_type = "application/pdf"
        return FileResponse(path=file_path, filename=filename, media_type=media_type)
    raise HTTPException(status_code=404, detail="File not found")
