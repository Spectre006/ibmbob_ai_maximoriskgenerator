# Ask Mode Rules

This file provides documentation context for the Maximo Risk Assessment Generator project.

## Project Status
**Architecture Defined** - Comprehensive architecture in ARCHITECTURE.md. Ready for implementation.

## Project Structure
```
maximo_riskassessement_generator/
├── ARCHITECTURE.md          # Complete system design and architecture
├── AGENTS.md               # General AI assistant guidance
├── requirements.md         # Project requirements
├── app.py                  # Main application entry (to be created)
├── services/               # Business logic and integrations
├── routes/                 # API endpoints
├── models/                 # Data models
└── templates/              # HTML templates
```

## Key Documentation
- **ARCHITECTURE.md**: Complete system design, data flow, API endpoints, deployment strategy
- **requirements.md**: Original project requirements and use case
- **AGENTS.md**: Quick reference for AI assistants
- **report_design.png**: UI design reference for report layout (CRITICAL - must follow exactly)

## Non-Obvious Documentation Patterns
- **UI Design**: `report_design.png` contains the exact layout, colors, and styling for JHA reports
- **IBM Watsonx.ai Integration**: Prompt engineering templates in ARCHITECTURE.md
- **Maximo API**: Work order data structure and required fields documented
- **Cloudant Schema**: Document structure for JHA reports with all required fields
- **Performance Targets**: < 10 second end-to-end JHA generation documented

## Integration Points
1. **IBM Maximo API**: Fetch work order details (description, location, equipment)
2. **IBM Watsonx.ai**: AI-powered risk assessment and hazard identification
3. **IBM Cloudant**: NoSQL database for storing generated JHA reports

## Deployment Context
- **Environment**: Local development initially
- **Authentication**: None (direct load) - to be added later
- **Database**: IBM Cloudant for report persistence
- **Report Formats**: PDF (primary), DOCX (secondary), HTML (web view)

## Notes
- Focus on helping users understand project structure and documentation
- All architectural decisions are documented in ARCHITECTURE.md
- Implementation roadmap includes 6 phases over 3 weeks
- Target: IBM BoB Hackathon submission