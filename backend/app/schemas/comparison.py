from pydantic import BaseModel
from typing import List, Optional

class ClauseSchema(BaseModel):
    clause_id: str
    title: str
    content: str

class ComparisonRequest(BaseModel):
    doc_a_id: str
    doc_b_id: str

class ChangeAnalysis(BaseModel):
    what_changed: str
    compliance_impact: str
    risk_impact: str

class ModifiedClause(BaseModel):
    old_clause: ClauseSchema
    new_clause: ClauseSchema
    analysis: ChangeAnalysis

class ComparisonResult(BaseModel):
    added: List[ClauseSchema]
    removed: List[ClauseSchema]
    modified: List[ModifiedClause]
    unchanged: List[ClauseSchema]

class RiskDelta(BaseModel):
    risk_increased: List[str]
    risk_decreased: List[str]
    new_risks: List[str]
    removed_risks: List[str]

class ComparisonDashboardResponse(BaseModel):
    comparison_id: str
    comparison_result: ComparisonResult
    risk_delta: RiskDelta
    compliance_impact: dict # e.g. {"HIGH": [...], "MEDIUM": [...], "LOW": [...]}
