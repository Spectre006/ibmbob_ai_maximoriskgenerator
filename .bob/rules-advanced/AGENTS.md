# Advanced Mode Rules

This file provides advanced coding guidance for the Maximo Risk Assessment Generator project.

## Project Status
**Architecture Defined** - Comprehensive architecture in ARCHITECTURE.md. Ready for implementation.

## Technology Stack
- **Backend**: Python 3.10+ with FastAPI (recommended) or Flask
- **AI Integration**: IBM Watsonx.ai SDK (`ibm-watson`)
- **Database**: IBM Cloudant Python client
- **PDF Generation**: ReportLab or WeasyPrint
- **Word Export**: python-docx
- **UI Design**: Follow `report_design.png` for report layout (CRITICAL)

## Code Structure (Non-Obvious Patterns)
When implementing, follow this modular structure:
```
services/
  ├── maximo_service.py    # Maximo API client with retry logic
  ├── ai_service.py         # Watsonx.ai integration with prompt templates
  ├── cloudant_service.py   # Database operations with connection pooling
  ├── jha_generator.py      # Core JHA generation logic
  └── pdf_generator.py      # Report formatting and export
```

## Critical Implementation Notes
- **Async/Await**: Use async functions for all external API calls (Maximo, Watsonx, Cloudant)
- **Error Handling**: Implement retry logic with exponential backoff for API failures
- **Environment Variables**: All credentials MUST be in .env file (never hardcode)
- **Logging**: Use structured logging with context (work_order_id, duration_ms)
- **Validation**: Use Pydantic models for request/response validation (if FastAPI)

## AI Integration Pattern
```python
# Prompt template structure
system_prompt = """
You are a safety expert analyzing work orders...
[See ARCHITECTURE.md for full template]
"""

# Response must be parsed as JSON
# Validate completeness before storing
```

## Database Schema
- Document type: `jha_report`
- Required fields: `work_order_id`, `created_at`, `hazards[]`, `risk_assessment`
- See ARCHITECTURE.md for complete schema

## Testing Requirements
- Mock external APIs in unit tests
- Integration tests for complete JHA generation flow
- Target: 85% code coverage

## Performance Targets
- Total JHA generation: < 10 seconds
- Maximo API call: < 2 seconds
- AI assessment: 3-5 seconds
- Report formatting: < 1 second

## Notes
- Access to MCP and Browser tools available in Advanced mode
- Use MCP for complex external integrations if needed
- Focus on implementation details and code patterns
- Refer to ARCHITECTURE.md for complete system design