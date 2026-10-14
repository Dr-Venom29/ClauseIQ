import json
from app.models.document import Document, Chunk, AnalysisSnapshot
from app.repositories.document_repository import DocumentRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.chunk_repository import ChunkRepository
from app.core.exceptions import QuotaExceededException
from app.services.llm_router import get_llm_router, LLMRouter

class RiskService:
    def __init__(self, db, router: LLMRouter | None = None):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.snapshot_repo = SnapshotRepository(db)
        self.metrics_repo = MetricsRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.router = router if router is not None else get_llm_router()

    def _log_metric(self, action: str, user_id: str):
        self.metrics_repo.increment(action, user_id=user_id)

    async def analyze_risks(self, document_id: str, user_id: str) -> dict:
        document = self.document_repo.get_by_id(document_id, user_id=user_id)
        if not document:
            raise ValueError("Document not found")

        # 1. Check Snapshot/Cache
        snapshot = self.snapshot_repo.get_snapshot(document_id, "risks", user_id, document.content_hash)

        if snapshot:
            self._log_metric("cache_hit", user_id=user_id)
            return json.loads(snapshot.result_json)

        self._log_metric("cache_miss", user_id=user_id)

        chunks = self.chunk_repo.get_chunks(document_id, user_id=user_id)
        content = "\n\n".join([f"Page {chunk.page}: {chunk.content}" for chunk in chunks])

        prompt = f"""
        You are a risk management AI. Analyze the document and identify high, medium, and low risks.
        Output a JSON object matching this schema:
        {{
            "high_risks": [{{"risk": "str", "severity": "high", "reason": "str", "citation": "str"}}],
            "medium_risks": [{{"risk": "str", "severity": "medium", "reason": "str", "citation": "str"}}],
            "low_risks": [{{"risk": "str", "severity": "low", "reason": "str", "citation": "str"}}],
            "assumptions": ["str"]
        }}
        
        Document Content:
        {content}
        """

        try:
            result = await self.router.generate_json(prompt, task="risk_analysis", user_id=user_id)
        except QuotaExceededException:
            print("Risk Analysis: Falling back to heuristic rules.")
            # OFFLINE FALLBACK: Heuristic Checks
            text_lower = content.lower()
            medium_risks = []
            
            if "liability" in text_lower:
                medium_risks.append({"risk": "Liability Clause Present", "severity": "medium", "reason": "Detected via heuristic offline mode.", "citation": "Various"})
            if "punitive damages" in text_lower:
                medium_risks.append({"risk": "Punitive Damages Mentioned", "severity": "medium", "reason": "Detected via heuristic offline mode.", "citation": "Various"})
                
            result = {
                "high_risks": [],
                "medium_risks": medium_risks,
                "low_risks": [],
                "assumptions": ["AI quota exhausted. Used offline risk heuristics."]
            }

        # 3. Save Snapshot
        new_snapshot = AnalysisSnapshot(
            document_id=document_id,
            document_hash=document.content_hash,
            analysis_type="risks",
            result_json=json.dumps(result),
            user_id=user_id
        )
        self.snapshot_repo.create_snapshot(new_snapshot, user_id=user_id)
            
        return result
