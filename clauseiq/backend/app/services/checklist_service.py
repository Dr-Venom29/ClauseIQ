import json
from app.models.document import Document, Chunk, AnalysisSnapshot
from app.repositories.document_repository import DocumentRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.chunk_repository import ChunkRepository
from app.core.exceptions import QuotaExceededException
from app.services.llm_router import get_llm_router, LLMRouter

class ChecklistService:
    def __init__(self, db, router: LLMRouter | None = None):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.snapshot_repo = SnapshotRepository(db)
        self.metrics_repo = MetricsRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.router = router if router is not None else get_llm_router()

    def _log_metric(self, action: str, user_id: str):
        self.metrics_repo.increment(action, user_id=user_id)

    async def generate_checklist(self, document_id: str, user_id: str) -> list:
        document = self.document_repo.get_by_id(document_id, user_id=user_id)
        if not document:
            raise ValueError("Document not found")

        # 1. Check Snapshot/Cache
        snapshot = self.snapshot_repo.get_snapshot(document_id, "checklist", user_id, document.content_hash)

        if snapshot:
            self._log_metric("cache_hit", user_id=user_id)
            return json.loads(snapshot.result_json)

        self._log_metric("cache_miss", user_id=user_id)

        chunks = self.chunk_repo.get_chunks(document_id, user_id=user_id)
        content = "\n\n".join([f"Page {chunk.page}: {chunk.content}" for chunk in chunks])

        prompt = f"""
        You are a compliance officer. Evaluate this document against standard legal/business requirements.
        Output a JSON array of objects, where each object matches:
        {{
            "title": "str",
            "status": "present|missing|unclear",
            "explanation": "str",
            "citation": "str (quote the exact text or say 'None')"
        }}
        
        Document Content:
        {content}
        """

        try:
            result = await self.router.generate_json(prompt, task="compliance", user_id=user_id)
        except QuotaExceededException:
            print("Checklist: Falling back to heuristic rules.")
            # OFFLINE FALLBACK: Heuristic Checks
            text_lower = content.lower()
            checks = [
                ("Termination Clause", ["terminate", "termination"]),
                ("Confidentiality", ["confidential", "nda", "non-disclosure"]),
                ("Indemnification", ["indemnify", "indemnification", "hold harmless"]),
                ("Governing Law", ["governing law", "jurisdiction", "courts of"]),
                ("Force Majeure", ["force majeure", "act of god", "unforeseeable"])
            ]
            
            result = []
            for title, keywords in checks:
                present = any(kw in text_lower for kw in keywords)
                result.append({
                    "title": title,
                    "status": "present" if present else "missing",
                    "explanation": "Evaluated via offline heuristics." if present else "Keyword not found.",
                    "citation": "Offline Mode Fallback"
                })

        # 3. Save Snapshot
        new_snapshot = AnalysisSnapshot(
            document_id=document_id,
            document_hash=document.content_hash,
            analysis_type="checklist",
            result_json=json.dumps(result),
            user_id=user_id
        )
        self.snapshot_repo.create_snapshot(new_snapshot, user_id=user_id)
            
        return result
