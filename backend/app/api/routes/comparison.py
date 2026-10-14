import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.comparison import ComparisonRequest, ComparisonDashboardResponse
from app.services.comparison_service import ComparisonService
from app.services.comparison_export_service import ComparisonExportService
from app.db.session import get_db
from app.models.document import AnalysisSnapshot, Document
from app.repositories.document_repository import DocumentRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.services.activity_service import ActivityService

router = APIRouter()
export_service = ComparisonExportService()

@router.post("/compare")
async def compare_documents(
    request: ComparisonRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        document_repo = DocumentRepository(db)
        doc_a = document_repo.get_by_id(request.doc_a_id, user_id=None)
        doc_b = document_repo.get_by_id(request.doc_b_id, user_id=None)
        if not doc_a or not doc_b:
            raise HTTPException(status_code=404, detail="One or both documents not found")
        if doc_a.user_id != current_user.id or doc_b.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not own one or both of these documents")

        snapshot_repo = SnapshotRepository(db)
        comparison_service = ComparisonService(db)
        cache_key = f"{request.doc_a_id}_{request.doc_b_id}"
        
        # Check cache
        cached = snapshot_repo.get_snapshot(cache_key, "comparison", user_id=current_user.id)
        if cached:
            return json.loads(cached.result_json)
        
        result = await comparison_service.compare_documents(request.doc_a_id, request.doc_b_id, user_id=current_user.id)
        
        # Calculate Risk Delta and Compliance Delta simply
        risk_increased = []
        risk_decreased = []
        high_compliance = []
        for m in result.get('modified', []):
            ri = m['analysis']['risk_impact'].lower()
            ci = m['analysis']['compliance_impact'].lower()
            if 'increase' in ri or 'high' in ri: risk_increased.append(m['old_clause']['title'])
            if 'decrease' in ri or 'low' in ri: risk_decreased.append(m['old_clause']['title'])
            if 'high' in ci: high_compliance.append(m['old_clause']['title'])
            
        final_response = {
            "comparison_id": cache_key,
            "comparison_result": result,
            "risk_delta": {
                "risk_increased": risk_increased,
                "risk_decreased": risk_decreased,
                "new_risks": [c['title'] for c in result.get('added', [])],
                "removed_risks": [c['title'] for c in result.get('removed', [])]
            },
            "compliance_impact": {
                "HIGH": high_compliance,
                "MEDIUM": [],
                "LOW": []
            }
        }
        
        cache_entry = AnalysisSnapshot(
            document_id=cache_key,
            analysis_type="comparison",
            result_json=json.dumps(final_response)
        )
        snapshot_repo.create_snapshot(cache_entry, user_id=current_user.id)
        
        # Log the activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(user_id=current_user.id, action="comparison", document_id=request.doc_b_id)

        return final_response
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare/{comparison_id}")
async def get_comparison(
    comparison_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        snapshot_repo = SnapshotRepository(db)
        cached = snapshot_repo.get_snapshot(comparison_id, "comparison", user_id=current_user.id)
        if cached:
            return json.loads(cached.result_json)
        raise HTTPException(status_code=404, detail="Comparison not found")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/comparison")
async def export_comparison(
    request: ComparisonRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        document_repo = DocumentRepository(db)
        snapshot_repo = SnapshotRepository(db)
        
        doc_a = document_repo.get_by_id(request.doc_a_id, user_id=None)
        doc_b = document_repo.get_by_id(request.doc_b_id, user_id=None)
        
        if not doc_a or not doc_b:
            raise HTTPException(status_code=404, detail="One or both documents not found")
        if doc_a.user_id != current_user.id or doc_b.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: You do not own one or both of these documents")
        
        cache_key = f"{request.doc_a_id}_{request.doc_b_id}"
        cached = snapshot_repo.get_snapshot(cache_key, "comparison", user_id=current_user.id)
        
        if cached:
            result = json.loads(cached.result_json)
        else:
            result = await compare_documents(request, db, current_user=current_user)
            
        download = await export_service.export_comparison_report(doc_a.filename, doc_b.filename, result['comparison_result'])
        
        # Log the activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(user_id=current_user.id, action="comparison", document_id=request.doc_b_id)

        return download
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
