from google import genai
from google.genai import types
from app.core.config import settings
from app.core.exceptions import handle_gemini_error
from app.db.session import get_db
from app.models.document import Metrics
import json

from app.repositories.metrics_repository import MetricsRepository

class AIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return cls._instance

    def _log_metric(self, action: str, user_id: str = None):
        if not user_id:
            return
        try:
            db = next(get_db())
            repo = MetricsRepository(db)
            repo.increment(action, user_id=user_id)
        except Exception as e:
            print(f"Failed to log metric: {e}")

    async def generate_json(self, prompt: str, user_id: str = None, model_name: str = 'gemini-2.5-flash') -> dict:
        self._log_metric("gemini_call", user_id=user_id)
        try:
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
        except Exception as e:
            handle_gemini_error(e)
            
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    async def generate_text(self, prompt: str, user_id: str = None, model_name: str = 'gemini-2.5-flash') -> str:
        self._log_metric("gemini_call", user_id=user_id)
        try:
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            handle_gemini_error(e)
