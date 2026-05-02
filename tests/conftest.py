"""
Pytest configuration and fixtures for testing
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import uuid


@pytest.fixture
def mock_work_order():
    """Mock work order data from Maximo"""
    return {
        "work_order_id": "WO12345",
        "description": "Repair HVAC system in Building A",
        "location": "Building A, Floor 3, Room 301",
        "equipment": "HVAC-001",
        "procedures": [
            "Inspect HVAC system",
            "Replace air filters",
            "Check refrigerant levels",
            "Test system operation"
        ],
        "status": "APPROVED",
        "priority": "HIGH"
    }


@pytest.fixture
def mock_hazards():
    """Mock hazard analysis from AI"""
    return [
        {
            "description": "Electrical shock from exposed wiring during HVAC repair",
            "risk_level": "HIGH",
            "controls": [
                "Lock out/tag out procedures",
                "Use insulated tools",
                "Verify power is off before work"
            ],
            "ppe": [
                "Insulated gloves",
                "Safety glasses",
                "Electrical-rated boots"
            ]
        },
        {
            "description": "Fall hazard when accessing rooftop HVAC unit",
            "risk_level": "MEDIUM",
            "controls": [
                "Use proper ladder",
                "Maintain three points of contact",
                "Secure work area"
            ],
            "ppe": [
                "Hard hat",
                "Safety harness",
                "Non-slip boots"
            ]
        },
        {
            "description": "Refrigerant exposure during system maintenance",
            "risk_level": "LOW",
            "controls": [
                "Work in well-ventilated area",
                "Follow proper handling procedures",
                "Have spill kit available"
            ],
            "ppe": [
                "Chemical-resistant gloves",
                "Safety goggles",
                "Respirator if needed"
            ]
        }
    ]


@pytest.fixture
def mock_jha_report(mock_work_order, mock_hazards):
    """Mock complete JHA report"""
    return {
        "report_id": str(uuid.uuid4()),
        "work_order_id": mock_work_order["work_order_id"],
        "work_order": mock_work_order,
        "hazards": mock_hazards,
        "emergency_contacts": {
            "supervisor": "John Doe - ext. 1234",
            "safety_officer": "Jane Smith - ext. 5678",
            "emergency": "911"
        },
        "risk_assessment": {
            "overall_risk": "HIGH",
            "high_risk_count": 1,
            "medium_risk_count": 1,
            "low_risk_count": 1
        },
        "created_at": datetime.utcnow().isoformat(),
        "status": "COMPLETED"
    }


@pytest.fixture
def mock_maximo_service():
    """Mock Maximo service"""
    service = Mock()
    service.get_work_order = AsyncMock()
    service.validate_work_order = AsyncMock(return_value=True)
    return service


@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    service = Mock()
    service.analyze_work_order = AsyncMock()
    return service


@pytest.fixture
def mock_cloudant_service():
    """Mock Cloudant service"""
    service = Mock()
    service.save_report = AsyncMock()
    service.get_report = AsyncMock()
    service.list_reports = AsyncMock()
    service.delete_report = AsyncMock()
    return service


@pytest.fixture
def mock_settings():
    """Mock application settings"""
    from config.settings import Settings
    
    settings = Settings(
        # Maximo
        maximo_api_url="https://test-maximo.com/api",
        maximo_api_key="test_key",
        maximo_username="test_user",
        maximo_password="test_pass",
        
        # Watsonx
        watsonx_api_key="test_watsonx_key",
        watsonx_project_id="test_project",
        watsonx_url="https://test-watsonx.com",
        watsonx_model_id="ibm/granite-13b-chat-v2",
        
        # Cloudant
        cloudant_url="https://test-cloudant.com",
        cloudant_api_key="test_cloudant_key",
        cloudant_database="test_db",
        
        # App
        app_env="testing",
        app_debug=True,
        secret_key="test_secret_key"
    )
    return settings


@pytest.fixture
def sample_ai_response():
    """Sample AI response JSON"""
    return {
        "hazards": [
            {
                "description": "Electrical shock from exposed wiring",
                "risk_level": "HIGH",
                "controls": ["Lock out/tag out", "Use insulated tools"],
                "ppe": ["Insulated gloves", "Safety glasses"]
            }
        ],
        "emergency_contacts": {
            "supervisor": "John Doe - ext. 1234",
            "safety_officer": "Jane Smith - ext. 5678",
            "emergency": "911"
        }
    }

# Made with Bob
