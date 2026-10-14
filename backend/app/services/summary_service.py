import json
from app.models.document import Document, Chunk, AnalysisSnapshot
from app.repositories.document_repository import DocumentRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.chunk_repository import ChunkRepository
from app.core.exceptions import QuotaExceededException
from app.services.llm_router import get_llm_router, LLMRouter

class SummaryService:
    def __init__(self, db, router: LLMRouter | None = None):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.snapshot_repo = SnapshotRepository(db)
        self.metrics_repo = MetricsRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.router = router if router is not None else get_llm_router()

    def _log_metric(self, action: str, user_id: str):
        self.metrics_repo.increment(action, user_id=user_id)

    async def generate_summary(self, document_id: str, user_id: str) -> dict:
        document = self.document_repo.get_by_id(document_id, user_id=user_id)
        if not document:
            raise ValueError("Document not found")

        # 1. Check Snapshot/Cache
        snapshot = self.snapshot_repo.get_snapshot(document_id, "summary", user_id, document.content_hash)

        if snapshot:
            self._log_metric("cache_hit", user_id=user_id)
            return json.loads(snapshot.result_json)

        self._log_metric("cache_miss", user_id=user_id)

        chunks = self.chunk_repo.get_chunks(document_id, user_id=user_id)
        content = "\n\n".join([f"Page {chunk.page}: {chunk.content}" for chunk in chunks])

        prompt = f"""
        You are a legal research assistant. Analyze the following document and provide a comprehensive structured summary.
        Output valid JSON matching this schema:
        {{
            "executive_summary": "str",
            "purpose": "str",
            "key_obligations": ["str"],
            "important_clauses": ["str"],
            "penalties": ["str"],
            "exceptions": ["str"],
            "takeaways": ["str"]
        }}
        
        Document Content:
        {content}
        """

        try:
            result = await self.router.generate_json(prompt, task="summary", user_id=user_id)
        except QuotaExceededException:
            # OFFLINE FALLBACK: Extractive Summary
            print("Summary: Falling back to extractive heuristic.")
            # Simplistic extraction: Just grab the first few chunks
            extractive_text = " ".join([c.content for c in chunks[:2]])
            result = {
                "executive_summary": extractive_text[:500] + "...",
                "purpose": "Extracted automatically (Offline Mode)",
                "key_obligations": ["Offline extraction unavailable"],
                "important_clauses": ["Offline extraction unavailable"],
                "penalties": ["Offline extraction unavailable"],
                "exceptions": ["Offline extraction unavailable"],
                "takeaways": ["AI quota exhausted. Displaying partial fallback data."]
            }

        # 3. Save Snapshot
        new_snapshot = AnalysisSnapshot(
            document_id=document_id,
            document_hash=document.content_hash,
            analysis_type="summary",
            result_json=json.dumps(result),
            user_id=user_id
        )
        self.snapshot_repo.create_snapshot(new_snapshot, user_id=user_id)

        return result
