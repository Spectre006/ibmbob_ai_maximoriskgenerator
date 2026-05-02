# AI-Powered Risk Assessment Generator - Architecture Document

## Project Overview
**IBM BoB Hackathon Submission**

AI-enabled Risk Assessment Generator that evaluates IBM Maximo work orders and automatically generates JHA (Job Hazard Analysis) reports to help technicians identify and mitigate safety risks.

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Application                          │
│                     (Python Flask/FastAPI)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Maximo     │    │  IBM Watsonx.ai  │    │    IBM       │
│     API      │    │   (AI Model)     │    │  Cloudant    │
│              │    │                  │    │  (Database)  │
└──────────────┘    └──────────────────┘    └──────────────┘
```

### Component Architecture

#### 1. Frontend Layer
- **Technology**: HTML5, CSS3, JavaScript (Vanilla or React)
- **Responsibilities**:
  - Work order input form
  - Display generated JHA reports
  - Download/Print functionality
  - **UI Design Reference**: `report_design.png` (MUST follow this design for report layout)
  - Report history view

#### 2. Backend Layer (Python)
- **Framework**: Flask or FastAPI
- **Modules**:
  - `app.py` - Main application entry point
  - `routes/` - API endpoints
  - `services/` - Business logic
    - `maximo_service.py` - Maximo API integration
    - `ai_service.py` - Watsonx.ai integration
    - `jha_generator.py` - JHA report generation
    - `cloudant_service.py` - Database operations
  - `models/` - Data models
  - `utils/` - Helper functions
  - `config/` - Configuration management

#### 3. Integration Layer
- **IBM Maximo API**: Fetch work order details
- **IBM Watsonx.ai**: AI-powered risk assessment
- **IBM Cloudant**: NoSQL database for report storage

## Data Flow

### JHA Report Generation Flow
```
1. User Input
   └─> Work Order ID entered in web form
   
2. Fetch Work Order
   └─> Backend calls Maximo API
   └─> Retrieve: task description, location, equipment, procedures
   
3. AI Risk Assessment
   └─> Send work order data to Watsonx.ai
   └─> AI analyzes:
       - Potential hazards
       - Risk levels (High/Medium/Low)
       - Safety controls
       - PPE requirements
       - Emergency procedures
   
4. Generate JHA Report
   └─> Structure AI output into JHA format
   └─> Include:
       - Work order details
       - Identified hazards
       - Risk assessment matrix
       - Control measures
       - Required PPE
       - Emergency contacts
   
5. Store & Display
   └─> Save report to Cloudant
   └─> Display formatted report to user
   └─> Provide download options (PDF/Word)
```

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: Flask or FastAPI
- **Key Libraries**:
  - `ibm-watson` - Watsonx.ai SDK
  - `requests` - HTTP client for Maximo API
  - `cloudant` - IBM Cloudant Python client
  - `python-dotenv` - Environment configuration
  - `reportlab` or `weasyprint` - PDF generation
  - `python-docx` - Word document generation
  - `pydantic` - Data validation (if using FastAPI)

### Frontend
- **Core**: HTML5, CSS3, JavaScript
- **Optional**: React.js or Vue.js for enhanced UX
- **UI Framework**: Bootstrap 5 or Tailwind CSS
- **Icons**: Font Awesome or Material Icons

### Database
- **IBM Cloudant** (CouchDB-based NoSQL)
- **Document Structure**:
```json
{
  "_id": "jha_report_uuid",
  "work_order_id": "WO12345",
  "created_at": "2026-05-02T10:30:00Z",
  "work_order_details": {
    "description": "...",
    "location": "...",
    "equipment": "..."
  },
  "risk_assessment": {
    "hazards": [...],
    "risk_levels": {...},
    "controls": [...]
  },
  "jha_report": {
    "pdf_url": "...",
    "html_content": "..."
  }
}
```

### External Services
- **IBM Watsonx.ai**: LLM for risk assessment
- **IBM Maximo API**: Work order data source
- **IBM Cloudant**: Report persistence

## API Design

### Backend REST API Endpoints

#### 1. Work Order Operations
```
GET  /api/workorders/{work_order_id}
     - Fetch work order from Maximo
     - Response: Work order details

POST /api/workorders/validate
     - Validate work order ID exists
     - Request: { "work_order_id": "WO12345" }
     - Response: { "valid": true, "details": {...} }
```

#### 2. JHA Report Generation
```
POST /api/jha/generate
     - Generate JHA report for work order
     - Request: { "work_order_id": "WO12345" }
     - Response: { "report_id": "uuid", "report": {...} }

GET  /api/jha/{report_id}
     - Retrieve existing JHA report
     - Response: Full report details

GET  /api/jha/{report_id}/download?format=pdf
     - Download report in specified format
     - Formats: pdf, docx, html
```

#### 3. Report History
```
GET  /api/jha/history
     - List all generated reports
     - Query params: ?limit=10&offset=0
     - Response: Paginated list of reports

DELETE /api/jha/{report_id}
     - Delete a report (soft delete)
```

#### 4. Health & Status
```
GET  /api/health
     - System health check
     - Response: { "status": "healthy", "services": {...} }
```

## AI Integration Strategy

### Watsonx.ai Prompt Engineering

#### System Prompt Template
```
You are a safety expert analyzing work orders to generate Job Hazard Analysis (JHA) reports.

Analyze the following work order and identify:
1. All potential hazards (physical, chemical, biological, ergonomic)
2. Risk level for each hazard (High/Medium/Low)
3. Recommended safety controls and mitigation measures
4. Required Personal Protective Equipment (PPE)
5. Emergency procedures and contacts

Work Order Details:
- ID: {work_order_id}
- Description: {description}
- Location: {location}
- Equipment: {equipment}
- Procedures: {procedures}

Provide a structured response in JSON format.
```

#### Response Processing
- Parse AI JSON response
- Validate completeness
- Enrich with standard safety guidelines
- Format into JHA report structure

## Database Schema (Cloudant)

### Collections/Document Types

#### 1. jha_reports
```json
{
  "_id": "report_uuid",
  "_rev": "revision_id",
  "type": "jha_report",
  "work_order_id": "WO12345",
  "created_at": "ISO8601_timestamp",
  "created_by": "system",
  "status": "completed",
  "work_order": {
    "id": "WO12345",
    "description": "Repair HVAC system",
    "location": "Building A, Floor 3",
    "equipment": "HVAC Unit #5",
    "priority": "High"
  },
  "hazards": [
    {
      "id": 1,
      "description": "Electrical shock from live wires",
      "risk_level": "High",
      "controls": ["Lockout/Tagout", "Insulated tools"],
      "ppe": ["Insulated gloves", "Safety glasses"]
    }
  ],
  "emergency_contacts": {
    "supervisor": "John Doe - 555-0100",
    "safety_officer": "Jane Smith - 555-0200"
  },
  "report_metadata": {
    "ai_model": "watsonx.ai/granite-13b",
    "generation_time_ms": 2500,
    "pdf_generated": true
  }
}
```

#### 2. system_config
```json
{
  "_id": "config_v1",
  "type": "system_config",
  "maximo_api_endpoint": "https://...",
  "watsonx_model_id": "ibm/granite-13b-chat-v2",
  "default_emergency_contacts": {...}
}
```

## Security Considerations

### API Security
- Store credentials in environment variables (`.env` file)
- Use HTTPS for all external API calls
- Implement rate limiting for AI API calls
- Validate all user inputs

### Data Privacy
- No authentication required initially (as per requirements)
- Future: Add IBM ID authentication
- Audit trail for all report generations
- Secure storage of API keys

## Deployment Strategy

### Local Development Setup
```bash
# 1. Clone repository
git clone <repo-url>
cd maximo_riskassessement_generator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with API credentials

# 5. Run application
python app.py
# Access at http://localhost:5000
```

### Environment Variables
```
# .env file
MAXIMO_API_URL=https://your-maximo-instance.com/api
MAXIMO_API_KEY=your_api_key
MAXIMO_USERNAME=your_username
MAXIMO_PASSWORD=your_password

WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

CLOUDANT_URL=https://your-account.cloudant.com
CLOUDANT_API_KEY=your_cloudant_api_key
CLOUDANT_DATABASE=jha_reports

FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
```

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Set up project structure
- [ ] Configure development environment
- [ ] Create basic Flask/FastAPI application
- [ ] Implement configuration management
- [ ] Set up logging

### Phase 2: Integrations (Week 1-2)
- [ ] Implement Maximo API client
- [ ] Implement Watsonx.ai integration
- [ ] Implement Cloudant database operations
- [ ] Create data models and validation
- [ ] Write unit tests for integrations

### Phase 3: Core Features (Week 2)
- [ ] Build JHA generation logic
- [ ] Implement AI prompt engineering
- [ ] Create report formatting module
- [ ] Add PDF/Word export functionality
- [ ] Implement error handling

### Phase 4: Frontend (Week 2-3)
- [ ] Design UI/UX mockups
- [ ] Build work order input form
- [ ] Create report display page
- [ ] Add report history view
- [ ] Implement download functionality

### Phase 5: Testing & Polish (Week 3)
- [ ] Integration testing
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Documentation
- [ ] Demo preparation

### Phase 6: Future Enhancements
- [ ] Add IBM ID authentication
- [ ] Implement user roles (technician, supervisor, admin)
- [ ] Add report approval workflow
- [ ] Create analytics dashboard
- [ ] Mobile responsive design
- [ ] Multi-language support

## File Structure
```
maximo_riskassessement_generator/
├── app.py                      # Main application entry
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore
├── README.md
├── ARCHITECTURE.md            # This file
├── AGENTS.md                  # AI assistant guidance
│
├── config/
│   ├── __init__.py
│   ├── settings.py           # Configuration loader
│   └── constants.py          # Application constants
│
├── models/
│   ├── __init__.py
│   ├── work_order.py         # Work order data model
│   ├── jha_report.py         # JHA report data model
│   └── hazard.py             # Hazard data model
│
├── services/
│   ├── __init__.py
│   ├── maximo_service.py     # Maximo API integration
│   ├── ai_service.py         # Watsonx.ai integration
│   ├── cloudant_service.py   # Database operations
│   ├── jha_generator.py      # JHA report generation
│   └── pdf_generator.py      # PDF export functionality
│
├── routes/
│   ├── __init__.py
│   ├── workorder_routes.py   # Work order endpoints
│   ├── jha_routes.py         # JHA report endpoints
│   └── health_routes.py      # Health check endpoints
│
├── utils/
│   ├── __init__.py
│   ├── validators.py         # Input validation
│   ├── formatters.py         # Data formatting
│   └── logger.py             # Logging configuration
│
├── templates/                 # HTML templates (if using Flask)
│   ├── base.html
│   ├── index.html
│   ├── report.html
│   └── history.html
│
├── static/                    # Static assets
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── images/
│
└── tests/
    ├── __init__.py
    ├── test_maximo_service.py
    ├── test_ai_service.py
    ├── test_jha_generator.py
    └── test_routes.py
```

## Key Design Decisions

### 1. Framework Choice: Flask vs FastAPI
**Recommendation: FastAPI**
- Better async support for API calls
- Automatic API documentation (Swagger/OpenAPI)
- Built-in data validation with Pydantic
- Modern Python features
- Better performance for I/O-bound operations

### 2. AI Model Selection
**IBM Watsonx.ai Models**:
- Primary: `ibm/granite-13b-chat-v2` (balanced performance)
- Alternative: `meta-llama/llama-2-70b-chat` (higher accuracy)
- Fallback: `google/flan-ul2` (faster responses)

### 3. Report Format
**Primary**: PDF (professional, printable)
**Secondary**: Word/DOCX (editable)
**Web**: HTML (immediate viewing)

### 4. Database Choice
**IBM Cloudant** (as specified)
- NoSQL flexibility for varying report structures
- Built-in replication and backup
- RESTful API
- IBM Cloud integration

## Performance Considerations

### Optimization Strategies
1. **Caching**: Cache Maximo work order data (5-minute TTL)
2. **Async Processing**: Use async/await for API calls
3. **Connection Pooling**: Reuse HTTP connections
4. **Lazy Loading**: Load report history on demand
5. **CDN**: Serve static assets from CDN (future)

### Expected Performance
- Work order fetch: < 2 seconds
- AI risk assessment: 3-5 seconds
- Report generation: < 1 second
- Total end-to-end: < 10 seconds

## Monitoring & Logging

### Logging Strategy
```python
# Log levels
- DEBUG: Development debugging
- INFO: Request/response tracking
- WARNING: Recoverable errors
- ERROR: API failures, exceptions
- CRITICAL: System failures

# Log format
{
  "timestamp": "ISO8601",
  "level": "INFO",
  "service": "ai_service",
  "message": "Generated risk assessment",
  "work_order_id": "WO12345",
  "duration_ms": 3500
}
```

### Metrics to Track
- API response times
- AI model latency
- Report generation success rate
- Error rates by service
- Database query performance

## Testing Strategy

### Unit Tests
- Test each service independently
- Mock external API calls
- Validate data models
- Test utility functions

### Integration Tests
- Test API endpoints
- Verify database operations
- Test complete JHA generation flow
- Validate PDF generation

### Test Coverage Goal
- Minimum: 70%
- Target: 85%
- Critical paths: 100%

## Documentation Requirements

### Code Documentation
- Docstrings for all functions/classes
- Type hints for function parameters
- Inline comments for complex logic
- README with setup instructions

### API Documentation
- Swagger/OpenAPI (auto-generated with FastAPI)
- Request/response examples
- Error code reference
- Authentication guide (future)

## Success Metrics

### Hackathon Demo
- Generate JHA report in < 10 seconds
- Accurate hazard identification (90%+)
- Professional report formatting
- Smooth user experience
- No critical bugs

### Future Production Metrics
- User adoption rate
- Report generation volume
- Time saved vs manual JHA creation
- Safety incident reduction
- User satisfaction score

## Risk Mitigation

### Technical Risks
1. **AI API Rate Limits**: Implement request queuing
2. **Maximo API Downtime**: Cache recent work orders
3. **Database Connection Issues**: Retry logic with exponential backoff
4. **Large Work Orders**: Implement text truncation/summarization

### Business Risks
1. **Inaccurate Risk Assessment**: Human review workflow (future)
2. **Compliance Issues**: Include disclaimer on reports
3. **Data Privacy**: Anonymize sensitive information

## Conclusion
## UI Design Guidelines

### Report Design Reference
**CRITICAL**: The UI must follow the design specified in `report_design.png`

This design file contains:
- Report layout and structure
- Color scheme and branding
- Typography and spacing
- Section organization
- Visual hierarchy

**Implementation Notes**:
- Use the exact layout from `report_design.png` for JHA report display
- Maintain consistent styling across web view, PDF, and DOCX exports
- Ensure responsive design matches the reference on all screen sizes
- Follow the color palette and typography specified in the design
- Preserve the visual hierarchy and section organization

**Frontend Development**:
- Reference `report_design.png` when building HTML templates
- Use CSS to match the design specifications exactly
- Test report rendering against the design reference
- Ensure PDF generation maintains the same visual appearance


This architecture provides a solid foundation for the IBM BoB Hackathon submission while being extensible for future enhancements. The modular design allows for easy testing, maintenance, and scaling.

**Next Steps**:
1. Review and approve architecture
2. Set up development environment
3. Begin Phase 1 implementation
4. Schedule regular progress reviews