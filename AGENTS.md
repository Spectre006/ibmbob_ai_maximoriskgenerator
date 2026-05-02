# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Status
**Architecture Defined** - Comprehensive architecture documented in ARCHITECTURE.md. Ready for implementation.

## Project Purpose
AI-enabled Risk Assessment Generator for IBM Maximo work orders that generates JHA (Job Hazard Analysis) reports for IBM BoB Hackathon.

## Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI (recommended) or Flask
- **AI**: IBM Watsonx.ai (granite-13b-chat-v2)
- **Database**: IBM Cloudant (NoSQL)
- **External APIs**: IBM Maximo API
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap/Tailwind)
- **UI Design**: Follow `report_design.png` for report layout (CRITICAL)

## Key Architecture Points
- **Deployment**: Local development (no authentication initially)
- **Data Flow**: Maximo → AI Analysis → JHA Report → Cloudant Storage
- **Report Formats**: PDF (primary), DOCX (secondary), HTML (web view)
- **API Design**: RESTful endpoints for work orders and JHA generation

## Critical Integration Details
1. **IBM Watsonx.ai**: Use for AI-powered risk assessment and hazard identification
2. **IBM Maximo API**: Fetch work order details (description, location, equipment, procedures)
3. **IBM Cloudant**: Store generated JHA reports with full audit trail
4. **No Authentication**: Direct application load (authentication planned for future)

## Setup Instructions
See ARCHITECTURE.md for detailed setup, environment variables, and deployment strategy.

## Notes for AI Assistants
- Refer to ARCHITECTURE.md for complete system design and data flow
- Follow modular structure: services/, routes/, models/, utils/
- Use async/await for external API calls (FastAPI advantage)
- Implement proper error handling and logging for all integrations
- Store API credentials in .env file (never commit)
- Focus on hackathon demo: < 10 second JHA generation, professional output

## Dependencies and Services
- **IBM Watsonx.ai**: AI LLM service for risk assessment (credentials required)
- **IBM Maximo API**: Work order data source (credentials required)
- **IBM Cloudant**: NoSQL database for report storage (credentials required)