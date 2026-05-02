"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json


@pytest.fixture
def client():
    """Create test client"""
    from app import app
    return TestClient(app)


def test_health_endpoint(client):
    """Test basic health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_health_endpoint(client):
    """Test API health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()


@pytest.mark.asyncio
async def test_generate_jha_report_endpoint(client, mock_jha_report):
    """Test JHA report generation endpoint"""
    with patch('services.jha_generator.JHAGenerator.generate_jha_report') as mock_generate:
        mock_generate.return_value = mock_jha_report
        
        response = client.post(
            "/api/jha/generate",
            json={"work_order_id": "WO12345"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["work_order_id"] == "WO12345"
        assert "report_id" in data


def test_generate_jha_report_invalid_input(client):
    """Test JHA generation with invalid input"""
    response = client.post(
        "/api/jha/generate",
        json={"work_order_id": ""}
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_report_endpoint(client, mock_jha_report):
    """Test get report by ID endpoint"""
    report_id = mock_jha_report["report_id"]
    
    with patch('services.cloudant_service.CloudantService.get_report') as mock_get:
        mock_get.return_value = mock_jha_report
        
        response = client.get(f"/api/jha/{report_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["report_id"] == report_id


def test_get_report_not_found(client):
    """Test get report with invalid ID"""
    with patch('services.cloudant_service.CloudantService.get_report') as mock_get:
        mock_get.return_value = None
        
        response = client.get("/api/jha/invalid-id")
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_report_pdf(client, mock_jha_report):
    """Test download report as PDF"""
    report_id = mock_jha_report["report_id"]
    
    with patch('services.cloudant_service.CloudantService.get_report') as mock_get:
        with patch('services.pdf_generator.PDFGenerator.generate_pdf') as mock_pdf:
            mock_get.return_value = mock_jha_report
            mock_pdf.return_value = b"PDF content"
            
            response = client.get(f"/api/jha/{report_id}/download?format=pdf")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_download_report_docx(client, mock_jha_report):
    """Test download report as DOCX"""
    report_id = mock_jha_report["report_id"]
    
    with patch('services.cloudant_service.CloudantService.get_report') as mock_get:
        with patch('services.docx_generator.DOCXGenerator.generate_docx') as mock_docx:
            mock_get.return_value = mock_jha_report
            mock_docx.return_value = b"DOCX content"
            
            response = client.get(f"/api/jha/{report_id}/download?format=docx")
            
            assert response.status_code == 200
            assert "application/vnd.openxmlformats" in response.headers["content-type"]


def test_download_report_invalid_format(client, mock_jha_report):
    """Test download with invalid format"""
    report_id = mock_jha_report["report_id"]
    
    response = client.get(f"/api/jha/{report_id}/download?format=invalid")
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_reports_endpoint(client, mock_jha_report):
    """Test list reports with pagination"""
    with patch('services.cloudant_service.CloudantService.list_reports') as mock_list:
        mock_list.return_value = {
            "reports": [mock_jha_report],
            "total": 1,
            "limit": 10,
            "offset": 0
        }
        
        response = client.get("/api/jha/history?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        assert data["total"] == 1


@pytest.mark.asyncio
async def test_delete_report_endpoint(client, mock_jha_report):
    """Test delete report endpoint"""
    report_id = mock_jha_report["report_id"]
    
    with patch('services.cloudant_service.CloudantService.delete_report') as mock_delete:
        mock_delete.return_value = True
        
        response = client.delete(f"/api/jha/{report_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


def test_get_work_order_endpoint(client, mock_work_order):
    """Test get work order endpoint"""
    with patch('services.maximo_service.MaximoService.get_work_order') as mock_get:
        mock_get.return_value = mock_work_order
        
        response = client.get("/api/workorders/WO12345")
        
        assert response.status_code == 200
        data = response.json()
        assert data["work_order_id"] == "WO12345"


def test_validate_work_order_endpoint(client):
    """Test validate work order endpoint"""
    with patch('services.maximo_service.MaximoService.validate_work_order') as mock_validate:
        mock_validate.return_value = True
        
        response = client.post(
            "/api/workorders/validate",
            json={"work_order_id": "WO12345"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True


def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.options("/api/health")
    
    # Should have CORS headers configured
    assert response.status_code in [200, 204]


def test_api_documentation_available(client):
    """Test that API documentation is accessible"""
    # Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    
    # ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200
    
    # OpenAPI JSON
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()

# Made with Bob
