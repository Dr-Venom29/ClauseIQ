from pydantic import BaseModel, ConfigDict
from typing import Optional, List

from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    content_hash: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str
    version_number: int
    parent_document_id: Optional[str] = None
    upload_timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Chunk(BaseModel):
    id: str
    document_id: str
    page: int
    section: Optional[str]
    content: str
    
    model_config = ConfigDict(from_attributes=True)

class ClauseResponse(BaseModel):
    id: str
    document_id: str
    clause_identifier: str
    title: str
    content: str
    page_number: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)
