"""Health check API routes."""

from fastapi import APIRouter
from typing import Dict, Any

from utils.logger import get_logger
from services.maximo_service import maximo_service
from services.ai_service import watsonx_service
from services.cloudant_service import cloudant_service

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Maximo Risk Assessment Generator is running"
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with service status.
    
    Returns:
        Detailed health status including all services
    """
    services_status = {
        "maximo": "unknown",
        "watsonx": "unknown",
        "cloudant": "unknown"
    }
    
    # Check Maximo service
    try:
        # Simple check - service is initialized
        if maximo_service.base_url:
            services_status["maximo"] = "configured"
        else:
            services_status["maximo"] = "not_configured"
    except Exception as e:
        logger.error(f"Maximo health check failed: {e}")
        services_status["maximo"] = "error"
    
    # Check Watsonx.ai service
    try:
        if watsonx_service.api_key:
            services_status["watsonx"] = "configured"
        else:
            services_status["watsonx"] = "not_configured"
    except Exception as e:
        logger.error(f"Watsonx health check failed: {e}")
        services_status["watsonx"] = "error"
    
    # Check Cloudant service
    try:
        if cloudant_service.url:
            services_status["cloudant"] = "configured"
        else:
            services_status["cloudant"] = "not_configured"
    except Exception as e:
        logger.error(f"Cloudant health check failed: {e}")
        services_status["cloudant"] = "error"
    
    # Determine overall status
    all_configured = all(
        status == "configured" for status in services_status.values()
    )
    
    overall_status = "healthy" if all_configured else "degraded"
    
    return {
        "status": overall_status,
        "version": "1.0.0",
        "services": services_status,
        "message": "Service health check complete"
    }

# Made with Bob
