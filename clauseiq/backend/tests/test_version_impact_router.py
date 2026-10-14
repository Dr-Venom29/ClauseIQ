import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock
from app.core.exceptions import QuotaExceededException
from app.models.document import Document, Clause
from app.services.change_analysis_service import ChangeAnalysisService
from app.services.comparison_service import ComparisonService
from app.services.llm_router import LLMRouter


def test_change_analysis_routes_to_router_with_task():
    async def _run():
        mock_router = MagicMock(spec=LLMRouter)
        expected_analysis = {
            "what_changed": "Notice period reduced from 30 to 14 days.",
            "compliance_impact": "High - shorter notice may violate local laws.",
            "risk_impact": "Risk Increased"
        }
        mock_router.generate_json = AsyncMock(return_value=expected_analysis)

        service = ChangeAnalysisService(router=mock_router)
        result = await service.analyze_change(
            old_text="Termination requires 30 days notice.",
            new_text="Termination requires 14 days notice.",
            user_id="user_123"
        )

        assert result == expected_analysis
        mock_router.generate_json.assert_awaited_once()
        call_args, call_kwargs = mock_router.generate_json.call_args
        assert call_kwargs.get("task") == "version_impact"
        assert call_kwargs.get("user_id") == "user_123"
        assert "Termination requires 30 days notice." in call_args[0]
        assert "Termination requires 14 days notice." in call_args[0]

    asyncio.run(_run())


def test_comparison_service_only_analyzes_modified_clauses():
    async def _run():
        db = MagicMock()
        mock_change_service = MagicMock(spec=ChangeAnalysisService)
        mock_change_service.analyze_change = AsyncMock(return_value={
            "what_changed": "Payment terms changed from 30 to 45 days.",
            "compliance_impact": "Low",
            "risk_impact": "Risk Increased"
        })

        service = ComparisonService(db, change_service=mock_change_service)

        doc_a = Document(id="doc_a", user_id="u1", content_hash="h_a", filename="v1.pdf")
        doc_b = Document(id="doc_b", user_id="u1", content_hash="h_b", filename="v2.pdf")
        service.document_repo.get_by_id = MagicMock(side_effect=lambda doc_id, user_id: doc_a if doc_id == "doc_a" else doc_b)

        # Clauses for Doc A:
        # C1: Identical to Doc B
        # C2: Modified in Doc B
        # C3: Removed in Doc B
        clauses_a = [
            Clause(id="ca1", document_id="doc_a", clause_identifier="1.0", title="Governing Law", content="This agreement is governed by the laws of California.", user_id="u1"),
            Clause(id="ca2", document_id="doc_a", clause_identifier="2.0", title="Payment Terms", content="Payment shall be made within 30 days of receiving the invoice.", user_id="u1"),
            Clause(id="ca3", document_id="doc_a", clause_identifier="3.0", title="Confidentiality", content="All shared technical information shall remain confidential for five years.", user_id="u1"),
        ]

        # Clauses for Doc B:
        # C1: Identical to Doc A
        # C2: Modified version of C2 (~85% similarity)
        # C4: Added in Doc B
        clauses_b = [
            Clause(id="cb1", document_id="doc_b", clause_identifier="1.0", title="Governing Law", content="This agreement is governed by the laws of California.", user_id="u1"),
            Clause(id="cb2", document_id="doc_b", clause_identifier="2.0", title="Payment Terms", content="Payment shall be made within 45 days of receiving the final invoice.", user_id="u1"),
            Clause(id="cb4", document_id="doc_b", clause_identifier="4.0", title="Arbitration", content="Any dispute shall be submitted to binding arbitration in San Francisco.", user_id="u1"),
        ]

        service.clause_repo.get_document_clauses = MagicMock(side_effect=lambda doc_id, user_id: clauses_a if doc_id == "doc_a" else clauses_b)

        comparison = await service.compare_documents("doc_a", "doc_b", user_id="u1")

        # Verify classifications
        assert len(comparison["unchanged"]) == 1
        assert comparison["unchanged"][0]["clause_id"] == "1.0"

        assert len(comparison["modified"]) == 1
        assert comparison["modified"][0]["old_clause"]["clause_id"] == "2.0"
        assert comparison["modified"][0]["new_clause"]["clause_id"] == "2.0"
        assert comparison["modified"][0]["analysis"]["what_changed"] == "Payment terms changed from 30 to 45 days."

        assert len(comparison["removed"]) == 1
        assert comparison["removed"][0]["clause_id"] == "3.0"

        assert len(comparison["added"]) == 1
        assert comparison["added"][0]["clause_id"] == "4.0"

        # Verify LLM was called EXACTLY ONCE: only for the modified clause, never for unchanged, added, or removed!
        mock_change_service.analyze_change.assert_awaited_once_with(
            "Payment shall be made within 30 days of receiving the invoice.",
            "Payment shall be made within 45 days of receiving the final invoice.",
            user_id="u1"
        )

    asyncio.run(_run())


def test_change_analysis_handles_quota_exception():
    async def _run():
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_json = AsyncMock(side_effect=QuotaExceededException("Quota exceeded"))

        service = ChangeAnalysisService(router=mock_router)
        result = await service.analyze_change(old_text="Old", new_text="New", user_id="u1")

        assert result["what_changed"] == "Comparison explanation unavailable (Offline Mode)"
        assert "Unknown due to API limit" in result["compliance_impact"]
        assert "Unknown due to API limit" in result["risk_impact"]

    asyncio.run(_run())


def test_change_analysis_handles_parsing_exception():
    async def _run():
        mock_router = MagicMock(spec=LLMRouter)
        mock_router.generate_json = AsyncMock(side_effect=RuntimeError("JSON malformed"))

        service = ChangeAnalysisService(router=mock_router)
        result = await service.analyze_change(old_text="Old", new_text="New", user_id="u1")

        assert result["what_changed"] == "Failed to parse AI response."
        assert result["compliance_impact"] == "Unknown"
        assert result["risk_impact"] == "Unknown"

    asyncio.run(_run())
