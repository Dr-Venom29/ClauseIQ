from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces import IDocumentRepository
from app.models.document import Document
from typing import List, Optional

class DocumentRepository(BaseRepository, IDocumentRepository):
    def get_by_id(self, document_id: str, user_id: Optional[str] = None) -> Optional[Document]:
        query = self.db.query(Document).filter(Document.id == document_id)
        if user_id is not None:
            query = query.filter(Document.user_id == user_id)
        return query.first()

    def get_by_hash(self, content_hash: str, user_id: str) -> Optional[Document]:
        return self.db.query(Document).filter(Document.content_hash == content_hash, Document.user_id == user_id).first()

    def create(self, db_document: Document, user_id: str) -> Document:
        db_document.user_id = user_id
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def update(self, db_document: Document, user_id: str) -> Document:
        if db_document.user_id != user_id:
            raise ValueError("Access Denied")
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def delete(self, document_id: str, user_id: str) -> bool:
        doc = self.get_by_id(document_id, user_id=user_id)
        if doc:
            self.db.delete(doc)
            self.db.commit()
            return True
        return False

    def get_all(self, user_id: str) -> List[Document]:
        return self.db.query(Document).filter(Document.user_id == user_id).all()

    def get_versions(self, document_id: str, user_id: str) -> List[Document]:
        return self.db.query(Document).filter(
            ((Document.id == document_id) | (Document.parent_document_id == document_id)),
            Document.user_id == user_id
        ).all()
