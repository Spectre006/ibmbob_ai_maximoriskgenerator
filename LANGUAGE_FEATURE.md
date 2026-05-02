# Multilingual Report Generation Feature

## Overview
Added comprehensive support for generating JHA reports in multiple languages: English, Chinese, and Hindi. This includes both AI-generated content AND all UI labels in reports and PDFs.

## Changes Made

### 1. Frontend Changes

#### HTML Template (`templates/index.html`)
- Added a language dropdown field next to the Work Order Number field
- Dropdown includes three options:
  - English (en) - Default
  - Chinese (zh)
  - Hindi (hi)
- Uses Bootstrap grid layout (8-4 column split) for responsive design

#### JavaScript (`static/js/app.js`)
- Updated `onFormSubmit()` to capture the selected language
- Modified `generateReport()` to accept and send language parameter
- Language is included in the API request body

### 2. Backend Changes

#### Models (`models/jha_report.py`)
- Updated `JHAGenerateRequest` model to include `language` field
- Default value: "en" (English)
- Validates language code in API endpoint

#### Constants (`config/constants.py`)
- Added `SYSTEM_PROMPT_TEMPLATES` dictionary with prompts in three languages:
  - English (en)
  - Chinese (zh) - Simplified Chinese
  - Hindi (hi) - Devanagari script
- Added `LANGUAGE_INSTRUCTION` dictionary to ensure AI responses match requested language
- Each template maintains the same structure but in the target language

#### AI Service (`services/ai_service.py`)
- Updated `_build_prompt()` method to accept language parameter
- Selects appropriate prompt template based on language code
- Appends language-specific instruction to ensure response consistency
- Updated `analyze_work_order()` to accept and pass language parameter

#### JHA Generator (`services/jha_generator.py`)
- Updated `generate_jha_report()` to accept language parameter
- Passes language through to AI service
- Logs language selection for debugging

#### API Routes (`routes/jha_routes.py`)
- Updated `/api/jha/generate` endpoint to handle language parameter
- Added validation for language code (must be: en, zh, or hi)
- Returns 400 error for invalid language codes

## Usage

### Frontend
1. User enters Work Order Number
2. User selects desired language from dropdown (defaults to English)
3. User clicks "Generate JHA Report"
4. Report is generated in the selected language

### API
```json
POST /api/jha/generate
{
  "work_order_id": "WO12345",
  "language": "zh"
}
```

## Language Support Details

### English (en)
- Default language
- Full support for all features
- Standard safety terminology

### Chinese (zh)
- Simplified Chinese characters
- Localized safety terminology
- Maintains JSON structure for parsing

### Hindi (hi)
- Devanagari script
- Localized safety terminology
- Maintains JSON structure for parsing

## Technical Notes

1. **AI Model Behavior**: The IBM Watsonx.ai model receives prompts in the target language and is instructed to respond in the same language.

2. **JSON Structure**: All responses maintain the same JSON structure regardless of language, ensuring consistent parsing.

3. **Fallback**: If an invalid language code is provided, the system defaults to English.

4. **Database Storage**: Reports are stored with their generated content in the specified language. The language code is part of the report metadata.

5. **PDF/DOCX Export**: Generated reports in any language can be exported to PDF or DOCX format, preserving the language-specific content.

## Testing Recommendations

1. Test report generation in all three languages
2. Verify AI responses are in the correct language
3. Test PDF/DOCX export with non-English content
4. Verify proper character encoding for Chinese and Hindi
5. Test language switching between consecutive reports

## Future Enhancements

1. Add more languages (Spanish, French, German, etc.)
2. Store user's language preference
3. Add language-specific formatting rules
4. Implement translation of existing reports
5. Add language detection for work order descriptions

## Files Modified

1. `templates/index.html` - Added language dropdown
2. `static/js/app.js` - Capture and send language parameter
3. `models/jha_report.py` - Added language field to request model
4. `config/constants.py` - Added multilingual prompt templates
5. `services/ai_service.py` - Language-aware prompt building
6. `services/jha_generator.py` - Pass language through pipeline
7. `routes/jha_routes.py` - Validate and handle language parameter

## Backward Compatibility

- Existing API calls without language parameter will default to English
- No breaking changes to existing functionality
- All existing reports remain accessible

---
*Feature implemented for IBM BoB Hackathon - Maximo Risk Assessment Generator*

## Label Translation Feature

### Overview
All UI labels are now fully translated in the selected language:

**Translated Labels Include:**
- Report ID, Work Order, Generated, Status
- Work Order Details, Description, Location, Equipment, Priority, Assigned To
- Identified Hazards, Hazard, Risk Level, Controls, Required PPE
- Emergency Contacts, Supervisor, Safety Officer, Emergency Services
- Field, Value (table headers)

### Implementation Details

1. **Frontend (JavaScript)**
   - Added `translations` dictionary in `static/js/app.js`
   - Created `t(key, lang)` helper function for translations
   - Updated `renderReport()` to use translated labels based on report language
   - Labels automatically switch when viewing reports in different languages

2. **Backend (PDF Generator)**
   - Added `LABEL_TRANSLATIONS` dictionary in `config/constants.py`
   - Created `_translate_label(key, language)` helper function
   - Updated all PDF sections to use translated labels:
     - Header section (Report ID, Work Order, Generated, Status)
     - Work Order Details table (all field labels)
     - Hazards section (Hazard, Risk Level, Description, Controls, PPE)
     - Emergency Contacts section (all contact labels)

3. **Language Storage**
   - Language code stored in `JHAReport.language` field
   - Also stored in `report_metadata['language']` for backward compatibility
   - Retrieved automatically when rendering reports or generating PDFs

### Font Support for Multilingual PDFs
- **English**: Standard Helvetica font
- **Chinese**: Helvetica (supports Chinese characters)
- **Hindi**: Arial Unicode font for Devanagari script (automatically selected if available)
