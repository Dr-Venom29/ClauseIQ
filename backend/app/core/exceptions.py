from fastapi import HTTPException
from google.api_core.exceptions import ResourceExhausted

class QuotaExceededException(Exception):
    def __init__(self, message: str = "AI analysis temporarily unavailable. Please retry later."):
        self.message = message

def handle_gemini_error(e: Exception):
    error_str = str(e).lower()

    # Handle quota exhaustion (429) and temporary unavailability (503)
    if isinstance(e, ResourceExhausted) or "429" in error_str or "quota" in error_str:
        raise QuotaExceededException("Gemini API quota exceeded. Please try again later.")

    if "503" in error_str or "unavailable" in error_str or "high demand" in error_str:
        raise QuotaExceededException("Gemini API is temporarily unavailable due to high demand. Please retry in a moment.")

    import traceback
    traceback.print_exc()

    raise HTTPException(
        status_code=500,
        detail=str(e)
    )
