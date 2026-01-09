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
    PLATFORM MODEL: Includes evidence summary, scores, compliance, gaps, recommendations.
    """
    # DEMO MODE: Return mock report response for demo batches
    if request.batch_id.startswith("demo-"):
        return ReportGenerateResponse(
            batch_id=request.batch_id,
            report_path=f"reports/demo_report_{request.batch_id}.pdf",
            download_url=f"/api/reports/download/{request.batch_id}",
            generated_at=datetime.utcnow().isoformat()
        )
    
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
    """Download generated report"""
    
    # DEMO MODE: Generate and return a demo PDF for demo batches
    if batch_id.startswith("demo-"):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO
        import tempfile
        
        # Create demo report directory if needed
        reports_dir = getattr(settings, 'REPORTS_DIR', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        demo_report_path = os.path.join(reports_dir, f"demo_report_{batch_id}.pdf")
        
        # Generate a simple demo PDF if it doesn't exist
        if not os.path.exists(demo_report_path):
            try:
                c = canvas.Canvas(demo_report_path, pagesize=letter)
                width, height = letter
                
                # Title
                c.setFont("Helvetica-Bold", 24)
                c.drawString(100, height - 100, "Smart Approval AI")
                
                c.setFont("Helvetica-Bold", 18)
                c.drawString(100, height - 140, "Institutional Evaluation Report")
                
                # Institution info
                c.setFont("Helvetica", 12)
                mode = "AICTE" if "aicte" in batch_id else "UGC"
                inst_name = "Indian Institute of Technology Delhi" if "aicte" in batch_id else "Delhi University - North Campus"
                c.drawString(100, height - 180, f"Institution: {inst_name}")
                c.drawString(100, height - 200, f"Batch ID: {batch_id}")
                c.drawString(100, height - 220, f"Mode: {mode}")
                c.drawString(100, height - 240, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
                c.drawString(100, height - 260, "Report Type: FULL")
                
                # KPI Scores section
                c.setFont("Helvetica-Bold", 14)
                c.drawString(100, height - 310, "KPI Performance Scores")
                
                c.setFont("Helvetica", 12)
                c.drawString(100, height - 340, "Faculty-Student Ratio (FSR) Score: 85.2 / 100")
                c.drawString(100, height - 360, "Infrastructure Score: 72.0 / 100")
                c.drawString(100, height - 380, "Placement Index: 92.3 / 100")
                c.drawString(100, height - 400, "Lab Compliance Index: 68.5 / 100")
                c.drawString(100, height - 420, "Overall Score: 78.5 / 100")
                
                # Document sufficiency
                c.setFont("Helvetica-Bold", 14)
                c.drawString(100, height - 470, "Information Block Sufficiency")
                
                c.setFont("Helvetica", 12)
                c.drawString(100, height - 500, "Blocks Present: 8 of 10 required blocks")
                c.drawString(100, height - 520, "Sufficiency Score: 80%")
                c.drawString(100, height - 540, "Missing: safety_compliance_information, research_innovation_information")
                
                # Compliance
                c.setFont("Helvetica-Bold", 14)
                c.drawString(100, height - 590, "Compliance Status")
                
                c.setFont("Helvetica", 12)
                c.drawString(100, height - 620, "0 compliance issues identified")
                c.drawString(100, height - 640, "Status: All regulatory requirements met")
                
                # Approval Readiness
                c.setFont("Helvetica-Bold", 14)
                c.drawString(100, height - 690, "Approval Readiness")
                
                c.setFont("Helvetica", 12)
                c.drawString(100, height - 720, "Classification: Continuation")
                c.drawString(100, height - 740, "Readiness Score: 95%")
                c.drawString(100, height - 760, "Recommendation: Ready for approval with minor improvements")
                
                # Footer
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(100, 50, "This is a demo report. Upload actual documents for real institutional evaluation.")
                
                c.save()
            except ImportError:
                # If reportlab is not installed, create a simple text file as fallback
                with open(demo_report_path.replace('.pdf', '.txt'), 'w') as f:
                    f.write(f"Smart Approval AI - Demo Report\n")
                    f.write(f"Batch ID: {batch_id}\n")
                    f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
                    f.write(f"\nThis is a demo report.\n")
                raise HTTPException(status_code=500, detail="PDF generation library not available")
        
        return FileResponse(
            demo_report_path,
            media_type="application/pdf",
            filename=f"demo_report_{batch_id}.pdf"
        )
    
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
