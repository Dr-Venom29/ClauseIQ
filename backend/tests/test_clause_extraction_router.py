import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.core.exceptions import QuotaExceededException
from app.models.document import Document, Chunk, Clause
from app.services.clause_extraction_service import ClauseExtractionService
from app.services.llm_router import LLMRouter, get_llm_router


def test_clause_extraction_routes_to_router_with_task():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        extracted_data = [
            {"clause_id": "1.1", "title": "Governing Law", "content": "This agreement is governed by California law."},
            {"clause_id": "2.1", "title": "Confidentiality", "content": "Information shall remain confidential for 3 years."},
        ]
        mock_router.generate_json = AsyncMock(return_value=extracted_data)

        service = ClauseExtractionService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc100", user_id="user_abc", content_hash="hash_abc", filename="agreement.pdf"
        ))
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="chk1", document_id="doc100", page=1, content="Section 1.1: Governing Law. This agreement is governed by California law."),
            Chunk(id="chk2", document_id="doc100", page=2, content="Section 2.1: Confidentiality. Information shall remain confidential for 3 years."),
        ])
        saved_clauses = []
        service.clause_repo.create_clause = MagicMock(side_effect=lambda c, user_id: saved_clauses.append(c))

        await service.extract_clauses(document_id="doc100", user_id="user_abc")

        mock_router.generate_json.assert_awaited_once()
        call_args, call_kwargs = mock_router.generate_json.call_args
        assert call_kwargs.get("task") == "clause_extraction"
        assert call_kwargs.get("user_id") == "user_abc"
        assert "Governing Law" in call_args[0]
        assert "Confidentiality" in call_args[0]

        assert len(saved_clauses) == 2
        assert saved_clauses[0].clause_identifier == "1.1"
        assert saved_clauses[0].title == "Governing Law"
        assert saved_clauses[0].document_id == "doc100"
        assert saved_clauses[0].user_id == "user_abc"
        assert saved_clauses[1].clause_identifier == "2.1"
        assert saved_clauses[1].title == "Confidentiality"

    asyncio.run(_run())


def test_clause_extraction_regex_fallback_on_quota():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_json = AsyncMock(side_effect=QuotaExceededException("Quota exceeded"))

        service = ClauseExtractionService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=Document(
            id="doc200", user_id="user_xyz", content_hash="hash_xyz", filename="contract.pdf"
        ))
        chunk_content = (
            "Article 1: Scope of Work\nThe vendor shall provide software engineering services.\n"
            "Section 2: Payment\nInvoices are payable within 30 days of receipt."
        )
        service.chunk_repo.get_chunks = MagicMock(return_value=[
            Chunk(id="chk10", document_id="doc200", page=1, content=chunk_content),
        ])
        saved_clauses = []
        service.clause_repo.create_clause = MagicMock(side_effect=lambda c, user_id: saved_clauses.append(c))

        await service.extract_clauses(document_id="doc200", user_id="user_xyz")

        mock_router.generate_json.assert_awaited_once()
        assert len(saved_clauses) >= 1
        assert saved_clauses[0].document_id == "doc200"
        assert saved_clauses[0].user_id == "user_xyz"
        assert saved_clauses[0].clause_identifier.startswith("R-")

    asyncio.run(_run())


def test_clause_extraction_document_not_found():
    async def _run():
        db = MagicMock()
        mock_router = MagicMock(spec=LLMRouter)
        service = ClauseExtractionService(db, router=mock_router)
        service.document_repo.get_by_id = MagicMock(return_value=None)

        with pytest.raises(ValueError, match="Document not found"):
            await service.extract_clauses(document_id="missing_doc", user_id="u1")

        mock_router.generate_json.assert_not_awaited()

    asyncio.run(_run())


def test_clause_extraction_defaults_to_global_router():
    db = MagicMock()
    service = ClauseExtractionService(db)
    assert service.router is get_llm_router()
