from pydantic import BaseModel
from typing import Optional, List

class ChatQuery(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    document_id: Optional[str] = None

class Citation(BaseModel):
    document_name: str
    page_number: int
    section: Optional[str]

class ChatResponse(BaseModel):
    response: str
    citations: List[Citation]
