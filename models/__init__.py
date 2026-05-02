"""Data models for the Maximo Risk Assessment Generator."""

from .work_order import WorkOrder, WorkOrderResponse
from .jha_report import JHAReport, Hazard, JHAReportResponse, JHAGenerateRequest

__all__ = [
    "WorkOrder",
    "WorkOrderResponse",
    "JHAReport",
    "Hazard",
    "JHAReportResponse",
    "JHAGenerateRequest",
]

# Made with Bob
