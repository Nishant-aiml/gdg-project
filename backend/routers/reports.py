"""
Report generation router - SQLite version
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Optional
from schemas.reports import ReportGenerateRequest, ReportGenerateResponse
from services.report_generator import ReportGenerator
from config.database import get_db, Batch, close_db
from config.settings import settings
from middleware.auth_middleware import get_current_user
from datetime import datetime
import os

router = APIRouter()
report_generator = ReportGenerator()

@router.post("/generate", response_model=ReportGenerateResponse)
def generate_report(
    request: ReportGenerateRequest,
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Generate PDF report for a batch.
    PLATFORM MODEL: Only real batches - no demo mode.
    Includes evidence summary, scores, compliance, gaps, recommendations.
    """
    db = get_db()
    
    try:
        batch = db.query(Batch).filter(Batch.id == request.batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")

        
        # PLATFORM MODEL: Enforce user access control
        if user:
            user_id = user.get("uid")
            role = user.get("role", "department")
            
            if role != "institution":
                department_id = user.get("department_id")
                if department_id:
                    if batch.department_id != department_id:
                        raise HTTPException(status_code=403, detail="Access denied")
                elif user_id:
                    if batch.user_id != user_id:
                        raise HTTPException(status_code=403, detail="Access denied")
        
        # INVALID BATCH ENFORCEMENT
        if batch.is_invalid == 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot generate report for invalid batch"
            )
        
        if batch.status != "completed":
            raise HTTPException(status_code=400, detail="Batch processing not completed")
        
        # Generate report
        report_path = report_generator.generate_report(
            request.batch_id,
            include_evidence=request.include_evidence if hasattr(request, 'include_evidence') else True,
            include_trends=request.include_trends if hasattr(request, 'include_trends') else False,
            report_type=request.report_type if hasattr(request, 'report_type') else "full",
        )
        
        download_url = f"/api/reports/download/{request.batch_id}"
        
        return ReportGenerateResponse(
            batch_id=request.batch_id,
            report_path=report_path,
            download_url=download_url,
            generated_at=datetime.utcnow().isoformat()
        )
    finally:
        close_db(db)

@router.get("/download/{batch_id}")
def download_report(
    batch_id: str,
    user: Optional[dict] = Depends(get_current_user)
):
    """Download generated report - only real batches, no demo mode"""
    db = get_db()
    
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # PLATFORM MODEL: Enforce user access control
        if user:
            user_id = user.get("uid")
            role = user.get("role", "department")
            
            if role != "institution":
                department_id = user.get("department_id")
                if department_id:
                    if batch.department_id != department_id:
                        raise HTTPException(status_code=403, detail="Access denied")
                elif user_id:
                    if batch.user_id != user_id:
                        raise HTTPException(status_code=403, detail="Access denied")
        
        # Find report file - check for both PDF and HTML (WeasyPrint fallback)
        report_filename_pdf = f"report_{batch_id}.pdf"
        report_filename_html = f"report_{batch_id}.html"
        reports_dir = getattr(settings, 'REPORTS_DIR', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        report_path_pdf = os.path.join(reports_dir, report_filename_pdf)
        report_path_html = os.path.join(reports_dir, report_filename_html)
        
        # Try PDF first, then HTML
        if os.path.exists(report_path_pdf):
            return FileResponse(
                report_path_pdf,
                media_type="application/pdf",
                filename=report_filename_pdf
            )
        elif os.path.exists(report_path_html):
            return FileResponse(
                report_path_html,
                media_type="text/html",
                filename=report_filename_html
            )
        else:
            raise HTTPException(status_code=404, detail="Report not generated. Please generate it first.")
    finally:
        close_db(db)
