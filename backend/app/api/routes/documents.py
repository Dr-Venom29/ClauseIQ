from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.document import Document, DocumentCreate, ClauseResponse
from app.services.document_service import DocumentService
from app.services.document_deletion_service import DocumentDeletionService
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.activity_service import ActivityService

router = APIRouter()

@router.post("/documents/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document for processing.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        document_service = DocumentService(db)
        document = await document_service.create_document(file=file, user_id=current_user.id)
        
        # Log the activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(user_id=current_user.id, action="upload", document_id=document.id)
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/version", response_model=Document)
async def upload_new_version(
    document_id: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new version of an existing document.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    document_service = DocumentService(db)
    # Check 404 vs 403
    parent_doc = document_service.document_repo.get_by_id(document_id, user_id=None)
    if not parent_doc:
        raise HTTPException(status_code=404, detail="Parent document not found")
    if parent_doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")

    try:
        document = await document_service.create_document(file=file, user_id=current_user.id, parent_document_id=document_id)
        
        # Log the activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(user_id=current_user.id, action="upload", document_id=document.id)
        
        return document
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/documents/my", response_model=List[Document])
async def get_my_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all documents owned by the current user.
    """
    document_service = DocumentService(db)
    documents = await document_service.get_all_documents(user_id=current_user.id)
    return documents

@router.get("/documents/{document_id}", response_model=Document)
async def get_document(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get document details.
    """
    document_service = DocumentService(db)
    document = document_service.document_repo.get_by_id(document_id, user_id=None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")
    return document

@router.get("/documents/", response_model=List[Document])
async def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all documents (restricted to current user).
    """
    document_service = DocumentService(db)
    documents = await document_service.get_all_documents(user_id=current_user.id)
    return documents

@router.get("/documents/{document_id}/clauses", response_model=List[ClauseResponse])
async def get_document_clauses(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all extracted clauses for a document.
    """
    document_service = DocumentService(db)
    document = document_service.document_repo.get_by_id(document_id, user_id=None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")

    clauses = await document_service.get_clauses(document_id=document_id, user_id=current_user.id)
    return clauses

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document and all related data/vectors safely.
    """
    deletion_service = DocumentDeletionService(db)
    success = await deletion_service.delete_document(document_id=document_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")
        
    # Log activity
    activity_service = ActivityService(db)
    await activity_service.log_activity(user_id=current_user.id, action="delete", document_id=document_id)
    
    return {"success": True}

@router.get("/documents/{document_id}/versions", response_model=List[Document])
async def get_document_versions(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all versions of a document family.
    """
    document_service = DocumentService(db)
    # Check document existence and ownership first
    doc = document_service.document_repo.get_by_id(document_id, user_id=None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")
        
    versions = document_service.document_repo.get_versions(document_id, user_id=current_user.id)
    return versions
