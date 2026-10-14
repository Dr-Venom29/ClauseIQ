from pydantic import BaseModel, Field
from typing import List, Optional

class ChecklistItem(BaseModel):
    title: str
    status: str = Field(description="Must be 'present', 'missing', or 'unclear'")
    explanation: str
    citation: str

class ChecklistResponse(BaseModel):
    items: List[ChecklistItem]

class SummaryResponse(BaseModel):
    executive_summary: str
    purpose: str
    key_obligations: List[str]
    important_clauses: List[str]
    penalties: List[str]
    exceptions: List[str]
    takeaways: List[str]

class RiskItem(BaseModel):
    risk: str
    severity: str = Field(description="Must be 'high', 'medium', or 'low'")
    reason: str
    citation: str

class RiskResponse(BaseModel):
    high_risks: List[RiskItem]
    medium_risks: List[RiskItem]
    low_risks: List[RiskItem]
    assumptions: List[str]

class ExportResponse(BaseModel):
    download_url: str
