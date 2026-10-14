from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.document import Document, Chunk, Clause, AnalysisSnapshot, Metrics
from app.models.user import User
from app.models.activity_log import ActivityLog

class IDocumentRepository(ABC):
    @abstractmethod
    def get_by_id(self, document_id: str, user_id: Optional[str] = None) -> Optional[Document]:
        pass

    @abstractmethod
    def get_by_hash(self, content_hash: str, user_id: str) -> Optional[Document]:
        pass

    @abstractmethod
    def create(self, db_document: Document, user_id: str) -> Document:
        pass

    @abstractmethod
    def update(self, db_document: Document, user_id: str) -> Document:
        pass

    @abstractmethod
    def delete(self, document_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    def get_all(self, user_id: str) -> List[Document]:
        pass

    @abstractmethod
    def get_versions(self, document_id: str, user_id: str) -> List[Document]:
        pass

class IChunkRepository(ABC):
    @abstractmethod
    def add_chunk(self, chunk: Chunk, user_id: str) -> Chunk:
        pass

    @abstractmethod
    def get_chunks(self, document_id: str, user_id: str) -> List[Chunk]:
        pass

    @abstractmethod
    def delete_document_chunks(self, document_id: str, user_id: str) -> None:
        pass

class IClauseRepository(ABC):
    @abstractmethod
    def create_clause(self, clause: Clause, user_id: str) -> Clause:
        pass

    @abstractmethod
    def get_document_clauses(self, document_id: str, user_id: str) -> List[Clause]:
        pass

    @abstractmethod
    def delete_document_clauses(self, document_id: str, user_id: str) -> None:
        pass

class ISnapshotRepository(ABC):
    @abstractmethod
    def get_snapshot(self, document_id: str, analysis_type: str, user_id: str, document_hash: str = None) -> Optional[AnalysisSnapshot]:
        pass

    @abstractmethod
    def create_snapshot(self, snapshot: AnalysisSnapshot, user_id: str) -> AnalysisSnapshot:
        pass

    @abstractmethod
    def update_snapshot(self, snapshot: AnalysisSnapshot, user_id: str) -> AnalysisSnapshot:
        pass

    @abstractmethod
    def delete_snapshot(self, snapshot_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    def delete_document_snapshots(self, document_id: str, user_id: str) -> None:
        pass

class IMetricsRepository(ABC):
    @abstractmethod
    def increment(self, action: str, user_id: str) -> Metrics:
        pass

    @abstractmethod
    def get_metric(self, action: str, user_id: str) -> Optional[Metrics]:
        pass

    @abstractmethod
    def get_all(self, user_id: str) -> List[Metrics]:
        pass

class IActivityLogRepository(ABC):
    @abstractmethod
    def log_activity(self, user_id: str, action: str, document_id: Optional[str] = None) -> ActivityLog:
        pass

    @abstractmethod
    def get_user_logs(self, user_id: str) -> List[ActivityLog]:
        pass

    @abstractmethod
    def delete_document_logs(self, document_id: str, user_id: str) -> None:
        pass

    @abstractmethod
    def get_recent_activities(self, user_id: str, limit: int = 20) -> List[dict]:
        pass

class IDashboardRepository(ABC):
    @abstractmethod
    def count_documents(self, user_id: str) -> int:
        pass

    @abstractmethod
    def count_analyses(self, user_id: str) -> int:
        pass

    @abstractmethod
    def count_chats(self, user_id: str) -> int:
        pass

    @abstractmethod
    def count_comparisons(self, user_id: str) -> int:
        pass

class IUserRepository(ABC):
    @abstractmethod
    def create_user(self, email: str, password_hash: str) -> User:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def user_exists(self, email: str) -> bool:
        pass
