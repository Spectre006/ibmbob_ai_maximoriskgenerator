"""Work Order data models."""

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class WorkOrder(BaseModel):
    """Work order data model from Maximo."""

    work_order_id: str = Field(..., description="Unique work order identifier")
    description: str = Field(..., description="Work order description")
    location: Optional[str] = Field(None, description="Work location")
    equipment: Optional[str] = Field(None, description="Equipment involved")
    procedures: Optional[str] = Field(None, description="Work procedures")
    priority: Optional[str] = Field(None, description="Work order priority")
    status: Optional[str] = Field(None, description="Work order status")
    assigned_to: Optional[str] = Field(None, description="Assigned technician")
    created_date: Optional[datetime] = Field(None, description="Creation date")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date")

    # Maximo returns WOPRIORITY as an integer and LEAD/STATUS as strings.
    # Coerce all three to str so the model accepts any scalar value.
    @field_validator('priority', 'status', 'assigned_to', mode='before')
    @classmethod
    def coerce_to_str(cls, v: Any) -> Optional[str]:
        if v is None or v == '':
            return None
        return str(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "work_order_id": "WO12345",
                "description": "Repair HVAC system in Building A",
                "location": "Building A, Floor 3, Room 301",
                "equipment": "HVAC Unit #5",
                "procedures": "1. Lockout/Tagout 2. Inspect system 3. Replace filters",
                "priority": "High",
                "status": "Approved",
                "assigned_to": "John Doe"
            }
        }


class WorkOrderResponse(BaseModel):
    """API response for work order data."""
    
    success: bool = Field(..., description="Request success status")
    work_order: Optional[WorkOrder] = Field(None, description="Work order data")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")


class WorkOrderValidateRequest(BaseModel):
    """Request model for work order validation."""
    
    work_order_id: str = Field(..., description="Work order ID to validate")


class WorkOrderValidateResponse(BaseModel):
    """Response model for work order validation."""
    
    valid: bool = Field(..., description="Whether work order ID is valid")
    exists: bool = Field(False, description="Whether work order exists in Maximo")
    details: Optional[dict] = Field(None, description="Basic work order details if exists")
    message: Optional[str] = Field(None, description="Validation message")

# Made with Bob
