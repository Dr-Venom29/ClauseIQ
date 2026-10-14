import json
from app.core.config import settings
from app.core.exceptions import QuotaExceededException
from app.services.llm_router import get_llm_router, LLMRouter

class ChangeAnalysisService:
    def __init__(self, router: LLMRouter | None = None):
        self.router = router if router is not None else get_llm_router()

    async def analyze_change(self, old_text: str, new_text: str, user_id: str = None) -> dict:
        prompt = f"""
        You are a legal AI that analyzes the difference between two versions of a document clause.
        Compare the OLD CLAUSE to the NEW CLAUSE.
        Explain what changed, the compliance impact, and the risk impact.
        ClauseIQ provides AI-assisted research support only and does not constitute legal advice.

        Output valid JSON matching this schema:
        {{
            "what_changed": "str (concise explanation)",
            "compliance_impact": "str (e.g. High/Medium/Low and why)",
            "risk_impact": "str (e.g. Risk Increased/Decreased/Neutral and why)"
        }}

        OLD CLAUSE:
        {old_text}

        NEW CLAUSE:
        {new_text}
        """

        try:
            result = await self.router.generate_json(prompt, task="version_impact", user_id=user_id)
            return result
        except QuotaExceededException:
            return {
                "what_changed": "Comparison explanation unavailable (Offline Mode)",
                "compliance_impact": "Unknown due to API limit.",
                "risk_impact": "Unknown due to API limit."
            }
        except Exception:
            return {
                "what_changed": "Failed to parse AI response.",
                "compliance_impact": "Unknown",
                "risk_impact": "Unknown"
            }
