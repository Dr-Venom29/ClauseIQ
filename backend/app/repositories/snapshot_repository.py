from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces import ISnapshotRepository
from app.models.document import AnalysisSnapshot
from typing import Optional

class SnapshotRepository(BaseRepository, ISnapshotRepository):
    def get_snapshot(self, document_id: str, analysis_type: str, user_id: str, document_hash: str = None) -> Optional[AnalysisSnapshot]:
        query = self.db.query(AnalysisSnapshot).filter(
            AnalysisSnapshot.document_id == document_id,
            AnalysisSnapshot.analysis_type == analysis_type,
            AnalysisSnapshot.user_id == user_id
        )
        if document_hash:
            query = query.filter(AnalysisSnapshot.document_hash == document_hash)
        return query.first()

    def create_snapshot(self, snapshot: AnalysisSnapshot, user_id: str) -> AnalysisSnapshot:
        snapshot.user_id = user_id
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def update_snapshot(self, snapshot: AnalysisSnapshot, user_id: str) -> AnalysisSnapshot:
        if snapshot.user_id != user_id:
            raise ValueError("Access Denied")
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def delete_snapshot(self, snapshot_id: str, user_id: str) -> bool:
        snapshot = self.db.query(AnalysisSnapshot).filter(
            AnalysisSnapshot.id == snapshot_id,
            AnalysisSnapshot.user_id == user_id
        ).first()
        if snapshot:
            self.db.delete(snapshot)
            self.db.commit()
            return True
        return False

    def delete_document_snapshots(self, document_id: str, user_id: str) -> None:
        self.db.query(AnalysisSnapshot).filter(
            AnalysisSnapshot.document_id == document_id,
            AnalysisSnapshot.user_id == user_id
        ).delete(synchronize_session=False)
        self.db.commit()
