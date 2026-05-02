"""JHA Report generation service - orchestrates all components."""

import time
from typing import Dict, Any, Optional
from datetime import datetime

from utils.logger import get_logger
from models.work_order import WorkOrder
from models.jha_report import JHAReport, Hazard, EmergencyContacts, normalise_risk_level
from services.maximo_service import maximo_service
from services.ai_service import watsonx_service
from services.cloudant_service import cloudant_service
from config.constants import ReportStatus

logger = get_logger(__name__)


class JHAGeneratorService:
    """Service for generating complete JHA reports."""
    
    def __init__(self):
        """Initialize JHA generator service."""
        self.maximo = maximo_service
        self.ai = watsonx_service
        self.db = cloudant_service
        
        logger.info("JHA Generator service initialized")
    
    async def generate_jha_report(self, work_order_id: str, language: str = "en") -> Dict[str, Any]:
        """
        Generate complete JHA report for a work order in specified language.
        
        This orchestrates the entire process:
        1. Fetch work order from Maximo
        2. Analyze with Watsonx.ai in specified language
        3. Generate JHA report
        4. Store in Cloudant
        5. Return report with metadata
        
        Args:
            work_order_id: Work order identifier
            language: Target language for report (en, zh, hi)
        
        Returns:
            Dictionary containing report and metadata
        
        Raises:
            Exception: If any step fails
        """
        start_time = time.time()
        logger.info(f"Starting JHA generation for work order: {work_order_id} in language: {language}")
        
        try:
            # Step 1: Fetch work order from Maximo
            logger.info("Step 1: Fetching work order from Maximo...")
            work_order = await self.maximo.get_work_order(work_order_id)
            
            if not work_order:
                raise Exception(f"Work order {work_order_id} not found in Maximo")
            
            logger.info(f"Work order fetched: {work_order.description[:50]}...")
            
            # Step 2: Analyze with Watsonx.ai in specified language
            logger.info(f"Step 2: Analyzing work order with Watsonx.ai in {language}...")
            ai_analysis = await self.ai.analyze_work_order(work_order, language)
            
            logger.info(f"AI analysis complete: {len(ai_analysis.get('hazards', []))} hazards identified")
            
            # Step 3: Generate JHA report
            logger.info("Step 3: Generating JHA report...")
            report = self._create_jha_report(work_order, ai_analysis, language)
            
            # Step 4: Store in Cloudant
            logger.info("Step 4: Storing report in Cloudant...")
            report_id = await self.db.save_report(report)
            
            # Calculate generation time
            generation_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"JHA report generated successfully in {generation_time_ms:.0f}ms: {report_id}"
            )
            
            # Step 5: Return complete result
            return {
                "success": True,
                "report_id": report_id,
                "report": report,
                "generation_time_ms": generation_time_ms,
                "message": "JHA report generated successfully"
            }
            
        except Exception as e:
            generation_time_ms = (time.time() - start_time) * 1000
            logger.error(f"JHA generation failed after {generation_time_ms:.0f}ms: {e}")
            
            return {
                "success": False,
                "report_id": None,
                "report": None,
                "generation_time_ms": generation_time_ms,
                "error": str(e),
                "message": "JHA report generation failed"
            }
    
    def _create_jha_report(
        self,
        work_order: WorkOrder,
        ai_analysis: Dict[str, Any],
        language: str = "en"
    ) -> JHAReport:
        """
        Create JHA report from work order and AI analysis.
        
        Args:
            work_order: Work order data
            ai_analysis: AI analysis results
        
        Returns:
            Complete JHA report
        """
        # Generate unique report ID
        report_id = self.db.generate_report_id()
        
        # Parse hazards from AI analysis
        # normalise_risk_level converts any case/language variant → "High"|"Medium"|"Low"
        hazards = []
        for hazard_data in ai_analysis.get("hazards", []):
            hazards.append(Hazard(
                id=hazard_data.get("id", len(hazards) + 1),
                description=hazard_data.get("description", ""),
                risk_level=normalise_risk_level(hazard_data.get("risk_level", "Medium")),
                controls=hazard_data.get("controls", []),
                ppe=hazard_data.get("ppe", [])
            ))
        
        # Parse emergency contacts
        emergency_contacts_data = ai_analysis.get("emergency_contacts", {})
        emergency_contacts = EmergencyContacts(
            supervisor=emergency_contacts_data.get("supervisor"),
            safety_officer=emergency_contacts_data.get("safety_officer"),
            emergency=emergency_contacts_data.get("emergency", "911")
        )
        
        # Create work order summary
        work_order_summary = {
            "id": work_order.work_order_id,
            "description": work_order.description,
            "location": work_order.location,
            "equipment": work_order.equipment,
            "procedures": work_order.procedures,
            "priority": work_order.priority,
            "status": work_order.status,
            "assigned_to": work_order.assigned_to
        }
        
        # Create report metadata — language stored here so PDF generator picks correct font
        report_metadata = {
            "ai_model": self.ai.model_id,
            "maximo_source": self.maximo.base_url,
            "hazards_count": len(hazards),
            "generated_by": "system",
            "version": "1.0.0",
            "language": language
        }
        
        # Create complete JHA report
        report = JHAReport(
            report_id=report_id,
            work_order_id=work_order.work_order_id,
            created_at=datetime.utcnow(),
            created_by="system",
            status=ReportStatus.COMPLETED,
            language=language,
            work_order=work_order_summary,
            hazards=hazards,
            emergency_contacts=emergency_contacts,
            additional_notes=ai_analysis.get("additional_notes"),
            report_metadata=report_metadata
        )
        
        return report
    
    async def get_report(self, report_id: str) -> Dict[str, Any]:
        """
        Retrieve existing JHA report.
        
        Args:
            report_id: Report identifier
        
        Returns:
            Dictionary containing report or error
        """
        try:
            report = await self.db.get_report(report_id)
            
            if report:
                return {
                    "success": True,
                    "report": report,
                    "message": "Report retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "report": None,
                    "error": "Report not found",
                    "message": "Report not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to retrieve report {report_id}: {e}")
            return {
                "success": False,
                "report": None,
                "error": str(e),
                "message": "Failed to retrieve report"
            }
    
    async def list_reports(
        self,
        limit: int = 10,
        offset: int = 0,
        work_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List JHA reports with pagination.
        
        Args:
            limit: Maximum number of reports
            offset: Number of reports to skip
            work_order_id: Filter by work order ID (optional)
        
        Returns:
            Dictionary containing list of reports
        """
        try:
            reports = await self.db.list_reports(limit, offset, work_order_id)
            total = await self.db.get_report_count(work_order_id)
            
            return {
                "success": True,
                "reports": reports,
                "total": total,
                "limit": limit,
                "offset": offset,
                "message": f"Retrieved {len(reports)} reports"
            }
            
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return {
                "success": False,
                "reports": [],
                "total": 0,
                "error": str(e),
                "message": "Failed to list reports"
            }
    
    async def delete_report(self, report_id: str) -> Dict[str, Any]:
        """
        Delete JHA report (soft delete).
        
        Args:
            report_id: Report identifier
        
        Returns:
            Dictionary containing success status
        """
        try:
            success = await self.db.delete_report(report_id)
            
            if success:
                return {
                    "success": True,
                    "message": "Report deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Report not found",
                    "message": "Report not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to delete report {report_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete report"
            }


# Global service instance
jha_generator = JHAGeneratorService()

# Made with Bob
