# Plan Mode Rules

This file provides architectural guidance for the Maximo Risk Assessment Generator project.

## Project Status
**Architecture Defined** - Comprehensive architecture in ARCHITECTURE.md. Ready for implementation.

## System Architecture Overview
```
Web Application (FastAPI/Flask)
    ↓
┌───────────────┬──────────────────┬────────────────┐
│   Maximo API  │  Watsonx.ai      │  IBM Cloudant  │
│  (Work Orders)│  (AI Analysis)   │  (Storage)     │
└───────────────┴──────────────────┴────────────────┘
```

## Key Architectural Decisions
1. **Framework**: FastAPI recommended over Flask for async support and auto-documentation
2. **AI Model**: IBM Watsonx.ai granite-13b-chat-v2 for risk assessment
3. **Database**: IBM Cloudant (NoSQL) for flexible report storage
4. **Deployment**: Local development first, no authentication initially
5. **Report Formats**: PDF (primary), DOCX (secondary), HTML (web view)

## Data Flow (Non-Obvious)
1. User enters Work Order ID → Backend fetches from Maximo API
2. Work order data sent to Watsonx.ai with structured prompt
3. AI returns JSON with hazards, risk levels, controls, PPE
4. Backend generates formatted JHA report (PDF/DOCX/HTML)
5. Report stored in Cloudant with full audit trail
6. User views/downloads report

## Critical Architectural Constraints
- **Performance**: Total JHA generation must be < 10 seconds
- **UI Design**: MUST follow `report_design.png` exactly for report layout and styling
- **Async Operations**: All external API calls must use async/await
- **Error Handling**: Retry logic with exponential backoff for API failures
- **Caching**: Cache Maximo work orders (5-minute TTL) to reduce API calls
- **Modularity**: Strict separation: services/ (logic), routes/ (endpoints), models/ (data)

## Integration Architecture
- **Maximo API**: RESTful, requires authentication, returns work order details
- **Watsonx.ai**: Prompt-based, JSON response, 3-5 second latency
- **Cloudant**: Document-based, RESTful API, supports replication

## Implementation Phases
1. **Phase 1**: Foundation (project structure, config, logging)
2. **Phase 2**: Integrations (Maximo, Watsonx, Cloudant clients)
3. **Phase 3**: Core Features (JHA generation, report formatting)
4. **Phase 4**: Frontend (UI, forms, report display)
5. **Phase 5**: Testing & Polish (integration tests, optimization)
6. **Phase 6**: Future Enhancements (authentication, workflows)

## Performance Architecture
- **Target**: < 10 seconds end-to-end
- **Breakdown**: Maximo (2s) + AI (3-5s) + Report (1s) + Storage (1s)
- **Optimization**: Connection pooling, async operations, caching

## Security Architecture
- **Credentials**: All in .env file (never commit)
- **API Keys**: Environment variables for Maximo, Watsonx, Cloudant
- **Authentication**: None initially (direct load), IBM ID planned for future
- **Data Privacy**: Audit trail in Cloudant, no sensitive data in logs

## Notes
- Focus on high-level design decisions and architectural constraints
- All detailed specifications in ARCHITECTURE.md
- Modular design allows independent testing of each service
- Hackathon focus: working demo with professional output