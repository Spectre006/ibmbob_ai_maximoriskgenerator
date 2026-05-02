"""
Unit tests for JHA Generator service
"""
import pytest
from unittest.mock import AsyncMock, patch
from services.jha_generator import JHAGenerator
from models.jha_report import JHAReport


@pytest.mark.asyncio
async def test_generate_jha_report_success(
    mock_maximo_service,
    mock_ai_service,
    mock_cloudant_service,
    mock_work_order,
    mock_hazards,
    mock_jha_report
):
    """Test successful JHA report generation"""
    # Setup mocks
    mock_maximo_service.get_work_order.return_value = mock_work_order
    mock_ai_service.analyze_work_order.return_value = mock_hazards
    mock_cloudant_service.save_report.return_value = mock_jha_report["report_id"]
    
    # Create generator with mocked services
    generator = JHAGenerator(
        maximo_service=mock_maximo_service,
        ai_service=mock_ai_service,
        cloudant_service=mock_cloudant_service
    )
    
    # Generate report
    result = await generator.generate_jha_report("WO12345")
    
    # Assertions
    assert result["work_order_id"] == "WO12345"
    assert "report_id" in result
    assert len(result["report"]["hazards"]) == 3
    assert result["report"]["risk_assessment"]["high_risk_count"] == 1
    assert result["generation_time"] > 0
    
    # Verify service calls
    mock_maximo_service.get_work_order.assert_called_once_with("WO12345")
    mock_ai_service.analyze_work_order.assert_called_once()
    mock_cloudant_service.save_report.assert_called_once()


@pytest.mark.asyncio
async def test_generate_jha_report_work_order_not_found(
    mock_maximo_service,
    mock_ai_service,
    mock_cloudant_service
):
    """Test JHA generation when work order doesn't exist"""
    # Setup mock to raise exception
    mock_maximo_service.get_work_order.side_effect = Exception("Work order not found")
    
    generator = JHAGenerator(
        maximo_service=mock_maximo_service,
        ai_service=mock_ai_service,
        cloudant_service=mock_cloudant_service
    )
    
    # Should raise exception
    with pytest.raises(Exception) as exc_info:
        await generator.generate_jha_report("INVALID_WO")
    
    assert "Work order not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_jha_report_ai_failure(
    mock_maximo_service,
    mock_ai_service,
    mock_cloudant_service,
    mock_work_order
):
    """Test JHA generation when AI service fails"""
    # Setup mocks
    mock_maximo_service.get_work_order.return_value = mock_work_order
    mock_ai_service.analyze_work_order.side_effect = Exception("AI service error")
    
    generator = JHAGenerator(
        maximo_service=mock_maximo_service,
        ai_service=mock_ai_service,
        cloudant_service=mock_cloudant_service
    )
    
    # Should raise exception
    with pytest.raises(Exception) as exc_info:
        await generator.generate_jha_report("WO12345")
    
    assert "AI service error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_calculate_risk_assessment(mock_hazards):
    """Test risk assessment calculation"""
    from services.jha_generator import JHAGenerator
    
    risk_assessment = JHAGenerator._calculate_risk_assessment(mock_hazards)
    
    assert risk_assessment["high_risk_count"] == 1
    assert risk_assessment["medium_risk_count"] == 1
    assert risk_assessment["low_risk_count"] == 1
    assert risk_assessment["overall_risk"] == "HIGH"


def test_determine_overall_risk():
    """Test overall risk determination logic"""
    from services.jha_generator import JHAGenerator
    
    # High risk present
    assert JHAGenerator._determine_overall_risk(2, 1, 0) == "HIGH"
    
    # Only medium risk
    assert JHAGenerator._determine_overall_risk(0, 3, 1) == "MEDIUM"
    
    # Only low risk
    assert JHAGenerator._determine_overall_risk(0, 0, 5) == "LOW"
    
    # No hazards
    assert JHAGenerator._determine_overall_risk(0, 0, 0) == "LOW"


@pytest.mark.asyncio
async def test_generation_time_tracking(
    mock_maximo_service,
    mock_ai_service,
    mock_cloudant_service,
    mock_work_order,
    mock_hazards,
    mock_jha_report
):
    """Test that generation time is properly tracked"""
    # Setup mocks with delays
    async def delayed_get_work_order(wo_id):
        import asyncio
        await asyncio.sleep(0.1)
        return mock_work_order
    
    async def delayed_analyze(wo):
        import asyncio
        await asyncio.sleep(0.2)
        return mock_hazards
    
    mock_maximo_service.get_work_order = delayed_get_work_order
    mock_ai_service.analyze_work_order = delayed_analyze
    mock_cloudant_service.save_report.return_value = mock_jha_report["report_id"]
    
    generator = JHAGenerator(
        maximo_service=mock_maximo_service,
        ai_service=mock_ai_service,
        cloudant_service=mock_cloudant_service
    )
    
    result = await generator.generate_jha_report("WO12345")
    
    # Should have tracked time (at least 0.3 seconds from delays)
    assert result["generation_time"] >= 0.3
    assert result["generation_time"] < 10  # Should be under target

# Made with Bob
