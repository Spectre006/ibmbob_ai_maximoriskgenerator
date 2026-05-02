"""IBM Maximo API integration service."""

import asyncio
from typing import Optional, Dict, Any
import httpx
from datetime import datetime, timedelta

from config.settings import settings
from config.constants import RETRY_DELAYS, MAX_RETRY_ATTEMPTS
from utils.logger import get_logger
from models.work_order import WorkOrder

logger = get_logger(__name__)


class MaximoService:
    """Service for interacting with IBM Maximo API."""
    
    def __init__(self):
        """Initialize Maximo service with configuration."""
        self.base_url = settings.maximo_api_url
        self.api_key = settings.maximo_api_key
        self.username = settings.maximo_username
        self.password = settings.maximo_password
        self.site_id = getattr(settings, 'maximo_site_id', 'BEDFORD')  # Default site
        self.timeout = httpx.Timeout(30.0)
        self._cache: Dict[str, tuple[WorkOrder, datetime]] = {}
        self._cache_ttl = settings.maximo_cache_ttl
        
        logger.info("Maximo service initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Maximo API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apikey": self.api_key,
        }
        
        # Add Cookie header if available in settings
        if hasattr(settings, 'maximo_cookie') and settings.maximo_cookie:
            headers["Cookie"] = settings.maximo_cookie
            
        return headers
    
    def _is_cache_valid(self, work_order_id: str) -> bool:
        """Check if cached work order is still valid."""
        if work_order_id not in self._cache:
            return False
        
        _, cached_time = self._cache[work_order_id]
        return datetime.utcnow() - cached_time < timedelta(seconds=self._cache_ttl)
    
    def _get_from_cache(self, work_order_id: str) -> Optional[WorkOrder]:
        """Get work order from cache if valid."""
        if self._is_cache_valid(work_order_id):
            work_order, _ = self._cache[work_order_id]
            logger.info(f"Retrieved work order {work_order_id} from cache")
            return work_order
        return None
    
    def _add_to_cache(self, work_order: WorkOrder):
        """Add work order to cache."""
        # Cache by wonum (work order number)
        cache_key = work_order.work_order_id
        self._cache[cache_key] = (work_order, datetime.utcnow())
        logger.debug(f"Cached work order {cache_key}")
    
    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with exponential backoff retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
        
        Returns:
            HTTP response
        
        Raises:
            httpx.HTTPError: If all retry attempts fail
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=self._get_headers(),
                        **kwargs
                    )
                    response.raise_for_status()
                    return response
                    
            except httpx.HTTPError as e:
                logger.warning(
                    f"Maximo API request failed (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}): {e}"
                )
                
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed for {endpoint}")
                    raise
    
    async def get_work_order(self, wonum: str, site_id: Optional[str] = None) -> Optional[WorkOrder]:
        """
        Fetch work order details from Maximo API.
        
        Args:
            wonum: Work order number (WONUM in Maximo)
            site_id: Site ID (optional, uses default if not provided)
        
        Returns:
            WorkOrder object if found, None otherwise
        """
        logger.info(f"Fetching work order: {wonum}")
        
        # Check cache first
        cached_wo = self._get_from_cache(wonum)
        if cached_wo:
            return cached_wo
        
        try:
            # Use provided site_id or default
            site = site_id or self.site_id
            
            # Build query parameters matching the curl command
            params = {
                "lean": "1",
                "ignorecollectionref": "1",
                "oslc.select": "wonum,workorderid,description,siteid,assetnum,location,status,lead,wopriority,woactivity{taskid,description},asset{assetnum,description},locations{location,description}",
                "oslc.where": f'siteid="{site}" and WONUM="{wonum}"'
            }
            
            # Endpoint is os/C_WO with query parameters
            endpoint = "os/C_WO"
            
            response = await self._make_request_with_retry("GET", endpoint, params=params)
            data = response.json()
            
            # Parse Maximo response
            work_order = self._parse_work_order_response(data, wonum)
            
            # Cache the result
            self._add_to_cache(work_order)
            
            logger.info(f"Successfully fetched work order: {wonum}")
            return work_order
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch work order {wonum}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching work order {wonum}: {e}")
            return None
    
    def _parse_work_order_response(self, data: Dict[str, Any], wonum: str) -> WorkOrder:
        """
        Parse Maximo API response into WorkOrder model.
        
        Args:
            data: Raw API response data
            wonum: Work order number
        
        Returns:
            WorkOrder object
        """
        # Extract member array from response
        members = data.get("member", [])
        
        if not members:
            raise ValueError(f"No work order found for WONUM: {wonum}")
        
        # Get first member (should be only one with our query)
        wo_data = members[0]
        
        # Extract location description
        location_desc = ""
        locations = wo_data.get("locations", [])
        if locations and len(locations) > 0:
            location_desc = f"{locations[0].get('location', '')} - {locations[0].get('description', '')}"
        elif wo_data.get("location"):
            location_desc = wo_data.get("location", "")
        
        # Extract asset description
        equipment_desc = ""
        asset = wo_data.get("asset", [])
        if asset and len(asset) > 0:
            equipment_desc = f"{asset[0].get('assetnum', '')} - {asset[0].get('description', '')}"
        elif wo_data.get("assetnum"):
            equipment_desc = wo_data.get("assetnum", "")
        
        # Extract work activities/tasks as procedures
        procedures = []
        woactivity = wo_data.get("woactivity", [])
        for activity in woactivity:
            task_id = activity.get("taskid", "")
            description = activity.get("description", "")
            if task_id or description:
                procedures.append(f"{task_id}: {description}" if task_id else description)
        
        # WOPRIORITY is an integer in Maximo — cast to str; LEAD and STATUS are strings.
        raw_priority    = wo_data.get("wopriority")
        raw_status      = wo_data.get("status")
        raw_lead        = wo_data.get("lead")

        return WorkOrder(
            work_order_id=wo_data.get("wonum", wonum),
            description=wo_data.get("description", ""),
            location=location_desc,
            equipment=equipment_desc,
            procedures="\n".join(procedures) if procedures else "No procedures specified",
            priority=str(raw_priority) if raw_priority is not None else None,
            status=str(raw_status)   if raw_status   is not None else None,
            assigned_to=str(raw_lead) if raw_lead    is not None else None,
            created_date=self._parse_date(wo_data.get("reportdate")),
            scheduled_date=self._parse_date(wo_data.get("schedstart"))
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string from Maximo API."""
        if not date_str:
            return None
        
        try:
            # Adjust date format based on Maximo API
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    async def validate_work_order(self, wonum: str, site_id: Optional[str] = None) -> bool:
        """
        Validate if work order exists in Maximo.
        
        Args:
            wonum: Work order number
            site_id: Site ID (optional)
        
        Returns:
            True if work order exists, False otherwise
        """
        work_order = await self.get_work_order(wonum, site_id)
        return work_order is not None
    
    def clear_cache(self):
        """Clear the work order cache."""
        self._cache.clear()
        logger.info("Maximo cache cleared")


# Global service instance
maximo_service = MaximoService()

# Made with Bob
