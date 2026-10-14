from pydantic import BaseModel
from typing import List, Optional

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[str] = None

class SearchResultItem(BaseModel):
    document_name: str
    page_number: int
    section: Optional[str]
    content: str
    score: float

class SearchResult(BaseModel):
    results: List[SearchResultItem]
