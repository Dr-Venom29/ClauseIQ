import json
import re
from app.models.document import Document, Chunk, Clause
from app.repositories.document_repository import DocumentRepository
from app.repositories.clause_repository import ClauseRepository
from app.repositories.chunk_repository import ChunkRepository
from app.core.exceptions import QuotaExceededException
from app.services.llm_router import get_llm_router, LLMRouter

class ClauseExtractionService:
    def __init__(self, db, router: LLMRouter | None = None):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.clause_repo = ClauseRepository(db)
        self.chunk_repo = ChunkRepository(db)
        self.router = router if router is not None else get_llm_router()

    async def extract_clauses(self, document_id: str, user_id: str):
        document = self.document_repo.get_by_id(document_id, user_id=user_id)
        if not document:
            raise ValueError("Document not found")

        chunks = self.chunk_repo.get_chunks(document_id, user_id=user_id)
        content = "\n\n".join([f"Page {chunk.page}: {chunk.content}" for chunk in chunks])

        prompt = f"""
        You are a legal document parsing AI.
        Extract all major clauses from the following document.
        Output a valid JSON array of objects matching this schema:
        [{{
            "clause_id": "str (e.g. 1.1 or 3A)",
            "title": "str",
            "content": "str"
        }}]
        
        If clause numbering is unavailable, invent logical sequential IDs (e.g. C1, C2).
        Extract the full content of the clause, summarizing only if the clause is extremely long.
        
        Document Content:
        {content}
        """
        
        clauses_data = []
        try:
            clauses_data = await self.router.generate_json(prompt, task="clause_extraction", user_id=user_id)
        except QuotaExceededException:
            print("Clause Extraction: Quota exceeded, falling back to Regex heuristic.")
            # HYBRID FALLBACK: Regex grouping
            sections = re.split(r'\n(?=\d+\.\d*|\bArticle\b|\bSection\b)', content, flags=re.IGNORECASE)
            for i, sec in enumerate(sections):
                if not sec.strip(): continue
                lines = sec.strip().split('\n')
                title = lines[0][:100]
                clauses_data.append({
                    "clause_id": f"R-{i+1}",
                    "title": title,
                    "content": sec.strip()
                })

        for c_data in clauses_data:
            clause = Clause(
                document_id=document_id,
                clause_identifier=c_data.get('clause_id', 'Unknown'),
                title=c_data.get('title', 'Untitled'),
                content=c_data.get('content', ''),
                user_id=user_id
            )
            self.clause_repo.create_clause(clause, user_id=user_id)


