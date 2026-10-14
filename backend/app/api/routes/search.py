from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.search import SearchQuery, SearchResult
from app.services.search_service import SearchService
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.document_repository import DocumentRepository

router = APIRouter()
search_service = SearchService()

@router.post("/search", response_model=SearchResult)
async def search(
    query: SearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Perform a semantic search.
    """
    if query.document_id:
        doc_repo = DocumentRepository(db)
        doc = doc_repo.get_by_id(query.document_id, user_id=None)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")

    results = await search_service.search(
        query=query.query, 
        user_id=current_user.id,
        document_id=query.document_id, 
        top_k=query.top_k
    )
    if not results:
        return {"results": []}
    return {"results": results}
