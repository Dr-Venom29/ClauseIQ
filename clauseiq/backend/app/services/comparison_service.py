from rapidfuzz import fuzz
from app.models.document import Document, Clause
from app.repositories.document_repository import DocumentRepository
from app.repositories.clause_repository import ClauseRepository
from app.services.change_analysis_service import ChangeAnalysisService

class ComparisonService:
    def __init__(self, db, change_service: ChangeAnalysisService | None = None):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.clause_repo = ClauseRepository(db)
        self.change_service = change_service if change_service is not None else ChangeAnalysisService()

    async def compare_documents(self, doc_a_id: str, doc_b_id: str, user_id: str) -> dict:
        doc_a = self.document_repo.get_by_id(doc_a_id, user_id=user_id)
        doc_b = self.document_repo.get_by_id(doc_b_id, user_id=user_id)
        
        if not doc_a or not doc_b:
            raise ValueError("One or both documents not found")

        clauses_a = self.clause_repo.get_document_clauses(doc_a_id, user_id=user_id)
        clauses_b = self.clause_repo.get_document_clauses(doc_b_id, user_id=user_id)

        added = []
        removed = []
        modified = []
        unchanged = []

        # Find best matches based on fuzzy ratio
        b_matched = set()

        for a in clauses_a:
            best_match = None
            best_score = 0
            
            for b in clauses_b:
                if b.id in b_matched:
                    continue
                # Simple exact ID match bypass
                if a.clause_identifier and a.clause_identifier != 'Unknown' and a.clause_identifier == b.clause_identifier:
                    best_match = b
                    best_score = fuzz.ratio(a.content, b.content)
                    break
                
                score = fuzz.ratio(a.content, b.content)
                if score > best_score:
                    best_score = score
                    best_match = b
            
            if best_match and best_score >= 80:
                b_matched.add(best_match.id)
                if best_score >= 98:
                    unchanged.append({
                        "clause_id": a.clause_identifier,
                        "title": a.title,
                        "content": a.content
                    })
                else:
                    analysis = await self.change_service.analyze_change(a.content, best_match.content, user_id=user_id)
                    modified.append({
                        "old_clause": {"clause_id": a.clause_identifier, "title": a.title, "content": a.content},
                        "new_clause": {"clause_id": best_match.clause_identifier, "title": best_match.title, "content": best_match.content},
                        "analysis": analysis
                    })
            else:
                removed.append({
                    "clause_id": a.clause_identifier,
                    "title": a.title,
                    "content": a.content
                })

        for b in clauses_b:
            if b.id not in b_matched:
                added.append({
                    "clause_id": b.clause_identifier,
                    "title": b.title,
                    "content": b.content
                })

        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged
        }
