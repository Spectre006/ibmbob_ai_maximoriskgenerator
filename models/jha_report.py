"""JHA Report data models."""

from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from config.constants import RiskLevel, ReportStatus

# ---------------------------------------------------------------------------
# Multilingual / mixed-case risk-level normaliser
# The AI may return any of these variants depending on the language selected.
# All are mapped to the canonical RiskLevel enum values expected by Pydantic.
# ---------------------------------------------------------------------------
_RISK_LEVEL_MAP: dict[str, str] = {
    # English variants
    "high":    "High",  "medium":  "Medium",  "low":    "Low",
    "High":    "High",  "Medium":  "Medium",  "Low":    "Low",
    "HIGH":    "High",  "MEDIUM":  "Medium",  "LOW":    "Low",
    # French variants
    "élevé":   "High",  "eleve":   "High",    "élevée": "High",
    "moyen":   "Medium","moyenne": "Medium",
    "faible":  "Low",
    # Hindi variants (Devanagari)
    "उच्च":    "High",
    "मध्यम":   "Medium",
    "निम्न":   "Low",   "कम":      "Low",
}


def normalise_risk_level(value: Any) -> str:
    """Return a canonical risk-level string, defaulting to 'Medium' if unknown."""
    raw = str(value).strip()
    return _RISK_LEVEL_MAP.get(raw) or _RISK_LEVEL_MAP.get(raw.lower(), "Medium")


class Hazard(BaseModel):
    """Hazard identification model."""

    id: int = Field(..., description="Hazard identifier")
    description: str = Field(..., description="Hazard description")
    risk_level: RiskLevel = Field(..., description="Risk level (High/Medium/Low)")
    controls: List[str] = Field(default_factory=list, description="Control measures")
    ppe: List[str] = Field(default_factory=list, description="Required PPE")

    @field_validator("risk_level", mode="before")
    @classmethod
    def normalise_risk(cls, v: Any) -> str:
        """Accept any case/language variant and map to High / Medium / Low."""
        return normalise_risk_level(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "description": "Electrical shock from live wires",
                "risk_level": "High",
                "controls": ["Lockout/Tagout procedure", "Use insulated tools"],
                "ppe": ["Insulated gloves", "Safety glasses", "Electrical-rated boots"]
            }
        }


class EmergencyContacts(BaseModel):
    """Emergency contact information."""
    
    supervisor: Optional[str] = Field(None, description="Supervisor contact")
    safety_officer: Optional[str] = Field(None, description="Safety officer contact")
    emergency: Optional[str] = Field("911", description="Emergency services")
    
    class Config:
        json_schema_extra = {
            "example": {
                "supervisor": "John Doe - 555-0100",
                "safety_officer": "Jane Smith - 555-0200",
                "emergency": "911"
            }
        }


class JHAReport(BaseModel):
    """Complete JHA Report model."""
    
    report_id: str = Field(..., description="Unique report identifier")
    work_order_id: str = Field(..., description="Associated work order ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Report creation timestamp")
    created_by: str = Field(default="system", description="Report creator")
    status: ReportStatus = Field(default=ReportStatus.COMPLETED, description="Report status")
    language: str = Field(default="en", description="Report language (en, zh, hi)")
    
    # Work order details
    work_order: Dict[str, Any] = Field(..., description="Work order information")
    
    # Risk assessment
    hazards: List[Hazard] = Field(default_factory=list, description="Identified hazards")
    emergency_contacts: Optional[EmergencyContacts] = Field(None, description="Emergency contacts")
    additional_notes: Optional[str] = Field(None, description="Additional safety notes")
    
    # Metadata
    report_metadata: Dict[str, Any] = Field(default_factory=dict, description="Report generation metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "jha_123456",
                "work_order_id": "WO12345",
                "created_at": "2024-01-15T10:30:00Z",
                "status": "completed",
                "work_order": {
                    "id": "WO12345",
                    "description": "Repair HVAC system",
                    "location": "Building A, Floor 3"
                },
                "hazards": [
                    {
                        "id": 1,
                        "description": "Electrical shock",
                        "risk_level": "High",
                        "controls": ["Lockout/Tagout"],
                        "ppe": ["Insulated gloves"]
                    }
                ],
                "emergency_contacts": {
                    "supervisor": "John Doe - 555-0100",
                    "safety_officer": "Jane Smith - 555-0200"
                }
            }
        }


class JHAGenerateRequest(BaseModel):
    """Request model for JHA report generation."""
    
    work_order_id: str = Field(..., description="Work order ID to generate JHA for")
    language: str = Field(default="en", description="Report language (en, zh, hi)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "work_order_id": "WO12345",
                "language": "en"
            }
        }


class JHAReportResponse(BaseModel):
    """API response for JHA report."""
    
    success: bool = Field(..., description="Request success status")
    report_id: Optional[str] = Field(None, description="Generated report ID")
    report: Optional[JHAReport] = Field(None, description="Complete JHA report")
    message: Optional[str] = Field(None, description="Response message")
    error: Optional[str] = Field(None, description="Error message if failed")
    generation_time_ms: Optional[float] = Field(None, description="Report generation time in milliseconds")


class JHAReportListResponse(BaseModel):
    """API response for list of JHA reports."""
    
    success: bool = Field(..., description="Request success status")
    reports: List[Dict[str, Any]] = Field(default_factory=list, description="List of reports")
    total: int = Field(0, description="Total number of reports")
    limit: int = Field(10, description="Results limit")
    offset: int = Field(0, description="Results offset")
    message: Optional[str] = Field(None, description="Response message")

# Made with Bob
