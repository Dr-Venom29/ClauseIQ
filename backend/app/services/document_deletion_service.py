import os
from fastapi import HTTPException, status
from app.repositories.document_repository import DocumentRepository
from app.repositories.clause_repository import ClauseRepository
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.activity_log_repository import ActivityLogRepository
from app.storage.local import LocalStorageProvider
from app.vector_store.faiss import FAISSVectorStore

class DocumentDeletionService:
    def __init__(self, db, storage_provider=None):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.clause_repo = ClauseRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.snapshot_repo = SnapshotRepository(db)
        self.activity_log_repo = ActivityLogRepository(db)
        self.storage_provider = storage_provider or LocalStorageProvider()
        self.vector_store = FAISSVectorStore()

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        # Check document ownership
        # Pass user_id=None to first see if document exists at all (helps distinguish 404 from 403)
        doc = self.document_repo.get_by_id(document_id, user_id=None)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if doc.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not own this document")

        # 1. Delete file from physical storage
        if doc.storage_path:
            self.storage_provider.delete_file(doc.storage_path)

        # 2. Rebuild FAISS index removing this document's vectors
        try:
            self.vector_store.delete_document_vectors(document_id)
        except Exception as e:
            print(f"Error deleting vectors from FAISS: {e}")

        # 3. Delete from DB (Chunks, Clauses, Snapshots, Activity Logs, then the Document itself)
        self.chunk_repo.delete_document_chunks(document_id, user_id)
        self.clause_repo.delete_document_clauses(document_id, user_id)
        self.snapshot_repo.delete_document_snapshots(document_id, user_id)
        self.activity_log_repo.delete_document_logs(document_id, user_id)
        
        # Finally delete document
        success = self.document_repo.delete(document_id, user_id)
        return success
