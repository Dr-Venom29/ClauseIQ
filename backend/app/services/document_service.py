import hashlib
import uuid
import os
from fastapi import UploadFile
from typing import List

from app.models.document import Document, Chunk, Clause
from app.repositories.document_repository import DocumentRepository
from app.repositories.clause_repository import ClauseRepository
from app.repositories.chunk_repository import ChunkRepository
from app.storage.local import LocalStorageProvider
from app.services.parser_service import ParserService

class DocumentService:
    def __init__(self, db, storage_provider=None):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.clause_repo = ClauseRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.storage_provider = storage_provider or LocalStorageProvider()
        self.parser_service = ParserService(db, self.storage_provider)

    async def create_document(self, file: UploadFile, user_id: str, parent_document_id: str = None) -> Document:
        content = await file.read()
        content_hash = hashlib.md5(content).hexdigest()

        # Check for duplicate document
        db_document = self.document_repo.get_by_hash(content_hash, user_id=user_id)
        if db_document and not parent_document_id:
            return db_document

        # Generate a temporary ID for file storage naming before the model generates its final primary key
        temp_id = str(uuid.uuid4())
        
        # Save file via storage provider
        storage_path = self.storage_provider.save_file(content, file.filename, custom_id=temp_id)

        version_number = 1
        if parent_document_id:
            parent_doc = self.document_repo.get_by_id(parent_document_id, user_id=user_id)
            if parent_doc:
                version_number = parent_doc.version_number + 1
            else:
                raise ValueError("Parent document not found")

        db_document = Document(
            filename=file.filename,
            content_hash=content_hash,
            storage_path=storage_path,
            version_number=version_number,
            parent_document_id=parent_document_id,
            user_id=user_id
        )
        self.document_repo.create(db_document, user_id=user_id)

        # Parse and chunk the document
        await self.parser_service.parse_document(db_document, user_id=user_id)

        return db_document

    async def get_document(self, document_id: str, user_id: str) -> Document:
        return self.document_repo.get_by_id(document_id, user_id=user_id)

    async def get_all_documents(self, user_id: str) -> List[Document]:
        return self.document_repo.get_all(user_id=user_id)

    async def get_clauses(self, document_id: str, user_id: str) -> List[Clause]:
        clauses = self.clause_repo.get_document_clauses(document_id, user_id=user_id)
        chunks = self.chunk_repo.get_chunks(document_id, user_id=user_id)
        
        for clause in clauses:
            clause.page_number = 1
            best_overlap = 0
            c_content = clause.content.lower().strip()
            if not c_content:
                continue
            for chunk in chunks:
                chk_content = chunk.content.lower().strip()
                if chk_content in c_content:
                    overlap = len(chk_content)
                elif c_content in chk_content:
                    overlap = len(c_content)
                else:
                    words_c = set(c_content.split())
                    words_chk = set(chk_content.split())
                    overlap = len(words_c & words_chk)
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    clause.page_number = chunk.page
        return clauses
