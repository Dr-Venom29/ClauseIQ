from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.chat import ChatQuery, ChatResponse
from app.services.chat_service import ChatService
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.activity_service import ActivityService

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    query: ChatQuery, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with the RAG system.
    """
    if query.document_id:
        doc_repo = DocumentRepository(db)
        doc = doc_repo.get_by_id(query.document_id, user_id=None)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")

    try:
        chat_service = ChatService(db)
        response = await chat_service.chat(
            query=query.query, 
            user_id=current_user.id,
            document_id=query.document_id,
            conversation_id=query.conversation_id
        )
        
        # Log the activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(user_id=current_user.id, action="chat", document_id=query.document_id)
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
