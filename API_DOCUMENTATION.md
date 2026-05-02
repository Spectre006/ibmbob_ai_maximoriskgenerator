# API Documentation

Complete API reference for the Maximo Risk Assessment Generator.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required (local development mode). Future versions will implement IBM ID authentication.

## Response Format

All API responses follow this structure:

**Success Response:**
```json
{
  "data": { ... },
  "message": "Success message",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Endpoints

### Health Check

#### GET /health
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/health/detailed
Detailed health check with service status.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "maximo": "connected",
    "watsonx": "connected",
    "cloudant": "connected"
  },
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Work Orders

#### GET /api/workorders/{work_order_id}
Fetch work order details from Maximo.

**Parameters:**
- `work_order_id` (path, required): Maximo work order ID

**Response:**
```json
{
  "work_order_id": "WO12345",
  "description": "Repair HVAC system",
  "location": "Building A, Floor 3",
  "equipment": "HVAC-001",
  "procedures": ["Inspect system", "Replace filters"],
  "status": "APPROVED",
  "priority": "HIGH"
}
```

**Error Codes:**
- `404`: Work order not found
- `500`: Maximo API error

#### POST /api/workorders/validate
Validate if a work order exists.

**Request Body:**
```json
{
  "work_order_id": "WO12345"
}
```

**Response:**
```json
{
  "valid": true,
  "work_order_id": "WO12345",
  "exists": true
}
```

---

### JHA Reports

#### POST /api/jha/generate
Generate a new JHA report for a work order.

**Request Body:**
```json
{
  "work_order_id": "WO12345"
}
```

**Response:**
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "work_order_id": "WO12345",
  "report": {
    "work_order_id": "WO12345",
    "work_order": {
      "description": "Repair HVAC system",
      "location": "Building A, Floor 3",
      "equipment": "HVAC-001"
    },
    "hazards": [
      {
        "description": "Electrical shock from exposed wiring",
        "risk_level": "HIGH",
        "controls": [
          "Lock out/tag out procedures",
          "Use insulated tools"
        ],
        "ppe": [
          "Insulated gloves",
          "Safety glasses",
          "Electrical-rated boots"
        ]
      }
    ],
    "emergency_contacts": {
      "supervisor": "John Doe - ext. 1234",
      "safety_officer": "Jane Smith - ext. 5678",
      "emergency": "911"
    },
    "risk_assessment": {
      "overall_risk": "HIGH",
      "high_risk_count": 2,
      "medium_risk_count": 3,
      "low_risk_count": 1
    },
    "created_at": "2024-01-15T10:30:00Z",
    "status": "COMPLETED"
  },
  "generation_time": 8.5,
  "message": "JHA report generated successfully"
}
```

**Error Codes:**
- `400`: Invalid work order ID
- `404`: Work order not found
- `500`: Generation failed

**Performance:**
- Target: < 10 seconds
- Typical: 5-8 seconds

#### GET /api/jha/{report_id}
Retrieve a specific JHA report.

**Parameters:**
- `report_id` (path, required): UUID of the report

**Response:**
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "work_order_id": "WO12345",
  "hazards": [...],
  "created_at": "2024-01-15T10:30:00Z",
  "status": "COMPLETED"
}
```

**Error Codes:**
- `404`: Report not found

#### GET /api/jha/{report_id}/download
Download report in specified format.

**Parameters:**
- `report_id` (path, required): UUID of the report
- `format` (query, optional): `pdf` or `docx` (default: `pdf`)

**Response:**
- Content-Type: `application/pdf` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Binary file content

**Example:**
```
GET /api/jha/550e8400-e29b-41d4-a716-446655440000/download?format=pdf
```

**Error Codes:**
- `400`: Invalid format
- `404`: Report not found
- `500`: Generation failed

#### GET /api/jha/{report_id}/view
View report as HTML page.

**Parameters:**
- `report_id` (path, required): UUID of the report

**Response:**
- Content-Type: `text/html`
- Formatted HTML page with report content

**Error Codes:**
- `404`: Report not found

#### GET /api/jha/history
List recent JHA reports with pagination.

**Query Parameters:**
- `limit` (optional, default: 10): Number of reports to return (max: 100)
- `offset` (optional, default: 0): Number of reports to skip
- `work_order_id` (optional): Filter by work order ID

**Response:**
```json
{
  "reports": [
    {
      "report_id": "550e8400-e29b-41d4-a716-446655440000",
      "work_order_id": "WO12345",
      "created_at": "2024-01-15T10:30:00Z",
      "status": "COMPLETED",
      "hazards": [
        {
          "risk_level": "HIGH",
          "description": "Electrical shock"
        }
      ]
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0,
  "has_more": true
}
```

**Example:**
```
GET /api/jha/history?limit=5&offset=10&work_order_id=WO12345
```

#### DELETE /api/jha/{report_id}
Soft delete a JHA report.

**Parameters:**
- `report_id` (path, required): UUID of the report

**Response:**
```json
{
  "message": "Report deleted successfully",
  "report_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Codes:**
- `404`: Report not found
- `500`: Deletion failed

---

## Data Models

### Work Order
```json
{
  "work_order_id": "string",
  "description": "string",
  "location": "string",
  "equipment": "string",
  "procedures": ["string"],
  "status": "string",
  "priority": "string"
}
```

### Hazard
```json
{
  "description": "string",
  "risk_level": "HIGH|MEDIUM|LOW",
  "controls": ["string"],
  "ppe": ["string"]
}
```

### Emergency Contacts
```json
{
  "supervisor": "string",
  "safety_officer": "string",
  "emergency": "string"
}
```

### Risk Assessment
```json
{
  "overall_risk": "HIGH|MEDIUM|LOW",
  "high_risk_count": "integer",
  "medium_risk_count": "integer",
  "low_risk_count": "integer"
}
```

---

## Error Handling

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `404`: Not Found
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error
- `503`: Service Unavailable

### Error Response Format

```json
{
  "detail": "Detailed error message",
  "error_code": "MAXIMO_CONNECTION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Common Error Codes

- `WORK_ORDER_NOT_FOUND`: Work order doesn't exist in Maximo
- `MAXIMO_CONNECTION_ERROR`: Cannot connect to Maximo API
- `WATSONX_API_ERROR`: AI service error
- `CLOUDANT_ERROR`: Database operation failed
- `VALIDATION_ERROR`: Input validation failed
- `GENERATION_TIMEOUT`: Report generation exceeded time limit

---

## Rate Limiting

Currently no rate limiting is implemented. Future versions will include:
- 100 requests per minute per IP
- 10 report generations per minute per IP

---

## Interactive Documentation

When the application is running, visit these URLs for interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## SDK Examples

### Python (requests)

```python
import requests

# Generate JHA report
response = requests.post(
    "http://localhost:8000/api/jha/generate",
    json={"work_order_id": "WO12345"}
)
report_data = response.json()

# Download PDF
pdf_response = requests.get(
    f"http://localhost:8000/api/jha/{report_data['report_id']}/download?format=pdf"
)
with open("jha_report.pdf", "wb") as f:
    f.write(pdf_response.content)
```

### JavaScript (fetch)

```javascript
// Generate JHA report
const response = await fetch('/api/jha/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ work_order_id: 'WO12345' })
});
const reportData = await response.json();

// Download PDF
const pdfResponse = await fetch(
    `/api/jha/${reportData.report_id}/download?format=pdf`
);
const blob = await pdfResponse.blob();
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'jha_report.pdf';
a.click();
```

### cURL

```bash
# Generate report
curl -X POST "http://localhost:8000/api/jha/generate" \
     -H "Content-Type: application/json" \
     -d '{"work_order_id": "WO12345"}'

# Download PDF
curl -X GET "http://localhost:8000/api/jha/{report_id}/download?format=pdf" \
     -o "jha_report.pdf"

# Get report history
curl -X GET "http://localhost:8000/api/jha/history?limit=5"
```

---

## Changelog

### Version 1.0.0 (Current)
- Initial API implementation
- JHA report generation
- PDF/DOCX export
- Report history and management
- Maximo integration
- Watsonx.ai integration
- Cloudant storage

---

*For technical implementation details, see [ARCHITECTURE.md](ARCHITECTURE.md)*