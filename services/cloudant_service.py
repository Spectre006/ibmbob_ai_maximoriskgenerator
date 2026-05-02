"""IBM Cloudant database integration service."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from cloudant.client import Cloudant
from cloudant.error import CloudantException

from config.settings import settings
from utils.logger import get_logger
from models.jha_report import JHAReport

logger = get_logger(__name__)


class CloudantService:
    """Service for interacting with IBM Cloudant database."""
    
    def __init__(self):
        """Initialize Cloudant service with configuration."""
        self.url = settings.cloudant_url
        self.api_key = settings.cloudant_api_key
        self.database_name = settings.cloudant_database
        self.client: Optional[Cloudant] = None
        self.database = None
        
        logger.info("Cloudant service initialized")
    
    def connect(self):
        """Establish connection to Cloudant database."""
        try:
            # Check if credentials are configured
            if not self.url or not self.api_key or self.url == "your-cloudant-url" or self.api_key == "your-api-key":
                logger.warning("Cloudant credentials not configured. Database features will be unavailable.")
                return
            
            # Initialize Cloudant client
            self.client = Cloudant.iam(
                account_name=self._extract_account_name(self.url),
                api_key=self.api_key,
                connect=True
            )
            
            # Get or create database
            if self.database_name in self.client.all_dbs():
                self.database = self.client[self.database_name]
                logger.info(f"Connected to existing database: {self.database_name}")
            else:
                self.database = self.client.create_database(self.database_name)
                logger.info(f"Created new database: {self.database_name}")
                
        except CloudantException as e:
            logger.warning(f"Failed to connect to Cloudant (database features unavailable): {e}")
            self.client = None
            self.database = None
        except Exception as e:
            logger.warning(f"Cloudant connection error (database features unavailable): {e}")
            self.client = None
            self.database = None
    
    def disconnect(self):
        """Close connection to Cloudant database."""
        if self.client:
            self.client.disconnect()
            logger.info("Disconnected from Cloudant")
    
    def _extract_account_name(self, url: str) -> str:
        """Extract account name from Cloudant URL."""
        # URL format: https://account-name.cloudant.com
        if "cloudant.com" in url:
            return url.split("//")[1].split(".")[0]
        return "account"
    
    def _ensure_connected(self):
        """Ensure database connection is established."""
        if self.client is None or self.database is None:
            self.connect()

        # If still not connected after attempt, raise exception
        if self.database is None:
            raise Exception("Database not available. Please configure Cloudant credentials.")
    
    async def save_report(self, report: JHAReport) -> str:
        """
        Save JHA report to Cloudant database.
        
        Args:
            report: JHA report to save
        
        Returns:
            Report ID
        
        Raises:
            Exception: If save operation fails
        """
        self._ensure_connected()
        
        try:
            # Convert report to dictionary
            report_dict = report.model_dump()
            
            # Ensure _id field for Cloudant
            report_dict["_id"] = report.report_id
            report_dict["type"] = "jha_report"
            
            # Convert datetime to ISO string
            if isinstance(report_dict.get("created_at"), datetime):
                report_dict["created_at"] = report_dict["created_at"].isoformat()
            
            # Save to database
            document = self.database.create_document(report_dict)
            
            if document.exists():
                logger.info(f"Successfully saved report: {report.report_id}")
                return report.report_id
            else:
                raise Exception("Document creation failed")
                
        except CloudantException as e:
            logger.error(f"Failed to save report {report.report_id}: {e}")
            raise Exception(f"Failed to save report: {str(e)}")
    
    async def get_report(self, report_id: str) -> Optional[JHAReport]:
        """
        Retrieve JHA report from Cloudant database.
        
        Args:
            report_id: Report identifier
        
        Returns:
            JHA report if found, None otherwise
        """
        self._ensure_connected()
        
        try:
            document = self.database[report_id]
            
            if document.exists():
                # Convert to JHAReport model
                report_data = dict(document)
                
                # Remove Cloudant-specific fields
                report_data.pop("_id", None)
                report_data.pop("_rev", None)
                report_data.pop("type", None)
                
                logger.info(f"Retrieved report: {report_id}")
                return JHAReport(**report_data)
            else:
                logger.warning(f"Report not found: {report_id}")
                return None
                
        except KeyError:
            logger.warning(f"Report not found: {report_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve report {report_id}: {e}")
            return None
    
    async def list_reports(
        self,
        limit: int = 10,
        offset: int = 0,
        work_order_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List JHA reports from database.
        
        Args:
            limit: Maximum number of reports to return
            offset: Number of reports to skip
            work_order_id: Filter by work order ID (optional)
        
        Returns:
            List of report summaries
        """
        try:
            self._ensure_connected()
            
            logger.info(f"Querying Cloudant for reports (limit={limit}, offset={offset}, work_order_id={work_order_id})")
            
            # Build query selector
            selector = {"type": "jha_report"}
            if work_order_id:
                selector["work_order_id"] = work_order_id
            
            # Query database - try with sort first (requires index)
            try:
                result = self.database.get_query_result(
                    selector=selector,
                    sort=[{"created_at": "desc"}]
                )
                # Use result slicing instead of limit/skip in query
                docs = result[offset:offset + limit]
                logger.info(f"Query with sort successful, found {len(docs)} documents")
            except Exception as sort_error:
                logger.warning(f"Sort failed (index may not exist): {sort_error}. Trying without sort...")
                # Fallback: query without sort
                result = self.database.get_query_result(
                    selector=selector
                )
                # Use result slicing instead of limit/skip in query
                docs = result[offset:offset + limit]
                logger.info(f"Query without sort successful, found {len(docs)} documents")

            reports = []
            for doc in docs:
                report_data = {
                    "report_id": doc.get("_id"),
                    "work_order_id": doc.get("work_order_id"),
                    "created_at": doc.get("created_at"),
                    "status": doc.get("status"),
                    "hazards": doc.get("hazards", []),
                    "work_order": doc.get("work_order", {})
                }
                reports.append(report_data)
                logger.debug(f"Added report: {report_data['report_id']}")
            
            logger.info(f"Successfully retrieved {len(reports)} reports from Cloudant")
            return reports
            
        except CloudantException as e:
            logger.error(f"Cloudant error listing reports: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Failed to list reports: {e}", exc_info=True)
            return []
    
    async def delete_report(self, report_id: str) -> bool:
        """
        Delete JHA report from database (soft delete).
        
        Args:
            report_id: Report identifier
        
        Returns:
            True if deleted successfully, False otherwise
        """
        self._ensure_connected()
        
        try:
            document = self.database[report_id]
            
            if document.exists():
                # Soft delete: mark as deleted instead of removing
                document["deleted"] = True
                document["deleted_at"] = datetime.utcnow().isoformat()
                document.save()
                
                logger.info(f"Soft deleted report: {report_id}")
                return True
            else:
                logger.warning(f"Report not found for deletion: {report_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete report {report_id}: {e}")
            return False
    
    async def get_report_count(self, work_order_id: Optional[str] = None) -> int:
        """
        Get total count of reports.
        
        Args:
            work_order_id: Filter by work order ID (optional)
        
        Returns:
            Total number of reports
        """
        try:
            self._ensure_connected()
            
            selector = {"type": "jha_report", "deleted": {"$ne": True}}
            if work_order_id:
                selector["work_order_id"] = work_order_id
            
            result = self.database.get_query_result(
                selector=selector,
                fields=["_id"]
            )
            
            # Convert iterator to list to get count
            docs = list(result)
            count = len(docs)
            logger.info(f"Total reports: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get report count: {e}")
            return 0
    
    def generate_report_id(self) -> str:
        """
        Generate unique report ID.
        
        Returns:
            Unique report identifier
        """
        return f"jha_{uuid.uuid4().hex[:12]}"


# Global service instance
cloudant_service = CloudantService()

# Made with Bob
