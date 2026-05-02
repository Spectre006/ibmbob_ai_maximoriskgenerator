"""JHA report API routes."""

from fastapi import APIRouter, HTTPException, status, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
import tempfile

from utils.logger import get_logger
from models.jha_report import (
    JHAGenerateRequest,
    JHAReportResponse,
    JHAReportListResponse
)
from services.jha_generator import jha_generator
from services.pdf_generator import pdf_generator
from services.docx_generator import docx_generator
from utils.validators import validate_work_order_id, validate_report_format
from config.constants import LABEL_TRANSLATIONS

logger = get_logger(__name__)

router = APIRouter(prefix="/api/jha", tags=["jha"])
templates = Jinja2Templates(directory="templates")


@router.post("/generate", response_model=JHAReportResponse)
async def generate_jha_report(request: JHAGenerateRequest) -> JHAReportResponse:
    """
    Generate JHA report for a work order.
    
    Args:
        request: Generation request with work order ID
    
    Returns:
        Generated JHA report
    
    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"API request: Generate JHA for work order {request.work_order_id} in language {request.language}")
    
    # Validate work order ID
    if not validate_work_order_id(request.work_order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid work order ID format"
        )
    
    # Validate language code
    if request.language not in ["en", "fr", "hi"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language code. Supported languages: en, fr, hi"
        )
    
    try:
        result = await jha_generator.generate_jha_report(request.work_order_id, request.language)
        
        if result["success"]:
            return JHAReportResponse(
                success=True,
                report_id=result["report_id"],
                report=result["report"],
                generation_time_ms=result["generation_time_ms"],
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "JHA generation failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate JHA report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate JHA report: {str(e)}"
        )


@router.get("/history", response_model=JHAReportListResponse)
async def list_jha_reports(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    work_order_id: Optional[str] = None
) -> JHAReportListResponse:
    """
    List JHA reports with pagination.
    
    Args:
        limit: Maximum number of reports (1-100)
        offset: Number of reports to skip
        work_order_id: Filter by work order ID (optional)
    
    Returns:
        List of JHA reports
    """
    logger.info(f"API request: List JHA reports (limit={limit}, offset={offset})")
    
    try:
        result = await jha_generator.list_reports(limit, offset, work_order_id)
        
        return JHAReportListResponse(
            success=result["success"],
            reports=result.get("reports", []),
            total=result.get("total", 0),
            limit=limit,
            offset=offset,
            message=result.get("message", "No reports available")
        )
        
    except Exception as e:
        logger.warning(f"Failed to list JHA reports (Cloudant may not be configured): {e}")
        # Return empty list instead of error if Cloudant is not configured
        return JHAReportListResponse(
            success=True,
            reports=[],
            total=0,
            limit=limit,
            offset=offset,
            message="No reports available. Database may not be configured."
        )


@router.get("/{report_id}", response_model=JHAReportResponse)
async def get_jha_report(report_id: str) -> JHAReportResponse:
    """
    Retrieve existing JHA report.

    Args:
        report_id: Report identifier

    Returns:
        JHA report

    Raises:
        HTTPException: If report not found
    """
    logger.info(f"API request: Get JHA report {report_id}")

    try:
        result = await jha_generator.get_report(report_id)

        if result["success"]:
            return JHAReportResponse(
                success=True,
                report_id=report_id,
                report=result["report"],
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Report not found")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve JHA report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}"
        )


@router.get("/{report_id}/download")
async def download_jha_report(
    report_id: str,
    format: str = Query("pdf", regex="^(pdf|docx|html)$")
):
    """
    Download JHA report in specified format.
    
    Args:
        report_id: Report identifier
        format: Export format (pdf, docx, html)
    
    Returns:
        File download response
    
    Raises:
        HTTPException: If report not found or export fails
    """
    logger.info(f"API request: Download JHA report {report_id} as {format}")
    
    # Validate format
    if not validate_report_format(format):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report format. Use: pdf, docx, or html"
        )
    
    try:
        # Get report
        result = await jha_generator.get_report(report_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        report = result["report"]
        
        # Generate file based on format
        if format == "pdf":
            # Generate PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                output_path = tmp_file.name
            
            pdf_generator.generate_pdf(report, output_path)
            
            return FileResponse(
                path=output_path,
                filename=f"JHA_Report_{report_id}.pdf",
                media_type="application/pdf",
                background=None  # File will be deleted after response
            )
        
        elif format == "docx":
            # Generate Word document
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                output_path = tmp_file.name
            
            docx_generator.generate_docx(report, output_path)
            
            return FileResponse(
                path=output_path,
                filename=f"JHA_Report_{report_id}.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                background=None
            )
        
        elif format == "html":
            # Return HTML view
            # Note: This returns HTML content, not a download
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="HTML format should be viewed using /api/jha/{report_id}/view endpoint"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download report: {str(e)}"
        )


@router.get("/{report_id}/view", response_class=HTMLResponse)
async def view_jha_report(report_id: str, request: Request):
    """
    View JHA report as HTML page.
    
    Args:
        report_id: Report identifier
        request: FastAPI request object
    
    Returns:
        HTML page with report
    
    Raises:
        HTTPException: If report not found
    """
    logger.info(f"API request: View JHA report {report_id}")
    
    try:
        # Get report
        result = await jha_generator.get_report(report_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        report = result["report"]

        # Determine language – works for both JHAReport objects and raw dicts
        if hasattr(report, "language"):
            language = report.language or "en"
        elif hasattr(report, "report_metadata"):
            language = (report.report_metadata or {}).get("language", "en")
        elif isinstance(report, dict):
            language = report.get("language") or (report.get("report_metadata") or {}).get("language", "en")
        else:
            language = "en"

        labels = LABEL_TRANSLATIONS.get(language, LABEL_TRANSLATIONS["en"])

        # Render HTML template
        return templates.TemplateResponse(
            "report.html",
            {"request": request, "report": report, "labels": labels, "language": language}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to view report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to view report: {str(e)}"
        )


@router.delete("/{report_id}")
async def delete_jha_report(report_id: str):
    """
    Delete JHA report (soft delete).
    
    Args:
        report_id: Report identifier
    
    Returns:
        Deletion confirmation
    
    Raises:
        HTTPException: If deletion fails
    """
    logger.info(f"API request: Delete JHA report {report_id}")
    
    try:
        result = await jha_generator.delete_report(report_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Report not found")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}"
        )

# Made with Bob
