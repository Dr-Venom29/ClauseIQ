from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces import IClauseRepository
from app.models.document import Clause
from typing import List

class ClauseRepository(BaseRepository, IClauseRepository):
    def create_clause(self, clause: Clause, user_id: str) -> Clause:
        clause.user_id = user_id
        self.db.add(clause)
        self.db.commit()
        self.db.refresh(clause)
        return clause

    def get_document_clauses(self, document_id: str, user_id: str) -> List[Clause]:
        return self.db.query(Clause).filter(
            Clause.document_id == document_id,
            Clause.user_id == user_id
        ).all()

    def delete_document_clauses(self, document_id: str, user_id: str) -> None:
        self.db.query(Clause).filter(
            Clause.document_id == document_id,
            Clause.user_id == user_id
        ).delete()
        self.db.commit()
