"""Work order API routes."""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from utils.logger import get_logger
from models.work_order import WorkOrderResponse, WorkOrderValidateRequest, WorkOrderValidateResponse
from services.maximo_service import maximo_service
from utils.validators import validate_work_order_id

logger = get_logger(__name__)

router = APIRouter(prefix="/api/workorders", tags=["workorders"])


@router.get("/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(work_order_id: str) -> WorkOrderResponse:
    """
    Fetch work order details from Maximo.
    
    Args:
        work_order_id: Work order identifier
    
    Returns:
        Work order details
    
    Raises:
        HTTPException: If work order not found or fetch fails
    """
    logger.info(f"API request: Get work order {work_order_id}")
    
    # Validate work order ID format
    if not validate_work_order_id(work_order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid work order ID format"
        )
    
    try:
        work_order = await maximo_service.get_work_order(work_order_id)
        
        if not work_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work order {work_order_id} not found"
            )
        
        return WorkOrderResponse(
            success=True,
            work_order=work_order,
            message="Work order retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch work order {work_order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch work order: {str(e)}"
        )


@router.post("/validate", response_model=WorkOrderValidateResponse)
async def validate_work_order(request: WorkOrderValidateRequest) -> WorkOrderValidateResponse:
    """
    Validate work order ID and check if it exists in Maximo.
    
    Args:
        request: Validation request with work order ID
    
    Returns:
        Validation result
    """
    logger.info(f"API request: Validate work order {request.work_order_id}")
    
    work_order_id = request.work_order_id
    
    # Validate format
    if not validate_work_order_id(work_order_id):
        return WorkOrderValidateResponse(
            valid=False,
            exists=False,
            message="Invalid work order ID format"
        )
    
    try:
        # Check if exists in Maximo
        exists = await maximo_service.validate_work_order(work_order_id)
        
        if exists:
            # Get basic details
            work_order = await maximo_service.get_work_order(work_order_id)
            details = {
                "work_order_id": work_order.work_order_id,
                "description": work_order.description[:100] if work_order.description else None,
                "location": work_order.location,
                "status": work_order.status
            } if work_order else None
            
            return WorkOrderValidateResponse(
                valid=True,
                exists=True,
                details=details,
                message="Work order is valid and exists"
            )
        else:
            return WorkOrderValidateResponse(
                valid=True,
                exists=False,
                message="Work order ID format is valid but not found in Maximo"
            )
            
    except Exception as e:
        logger.error(f"Failed to validate work order {work_order_id}: {e}")
        return WorkOrderValidateResponse(
            valid=False,
            exists=False,
            message=f"Validation failed: {str(e)}"
        )

# Made with Bob
