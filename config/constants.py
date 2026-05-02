"""Application constants and enums."""

from enum import Enum


class RiskLevel(str, Enum):
    """Risk level classifications for hazards."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ReportFormat(str, Enum):
    """Supported report export formats."""
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"


class ReportStatus(str, Enum):
    """JHA report generation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# AI Prompt Templates
SYSTEM_PROMPT_TEMPLATE = """You are a safety expert analyzing work orders to generate Job Hazard Analysis (JHA) reports.

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

Provide a structured response in JSON format with the following structure:
{{
  "hazards": [
    {{
      "id": 1,
      "description": "Hazard description",
      "risk_level": "High|Medium|Low",
      "controls": ["Control measure 1", "Control measure 2"],
      "ppe": ["PPE item 1", "PPE item 2"]
    }}
  ],
  "emergency_contacts": {{
    "supervisor": "Name - Phone",
    "safety_officer": "Name - Phone"
  }},
  "additional_notes": "Any additional safety considerations"
}}
"""

# Multilingual Prompt Templates
SYSTEM_PROMPT_TEMPLATES = {
    "en": SYSTEM_PROMPT_TEMPLATE,
    "hi": """आप एक सुरक्षा विशेषज्ञ हैं जो जॉब हैज़र्ड एनालिसिस (JHA) रिपोर्ट तैयार करने के लिए वर्क ऑर्डर का विश्लेषण कर रहे हैं।

निम्नलिखित वर्क ऑर्डर का विश्लेषण करें और पहचानें:
1. सभी संभावित खतरे (भौतिक, रासायनिक, जैविक, एर्गोनोमिक)
2. प्रत्येक खतरे के लिए जोखिम स्तर (उच्च/मध्यम/निम्न)
3. अनुशंसित सुरक्षा नियंत्रण और शमन उपाय
4. आवश्यक व्यक्तिगत सुरक्षा उपकरण (PPE)
5. आपातकालीन प्रक्रियाएं और संपर्क

वर्क ऑर्डर विवरण:
- आईडी: {work_order_id}
- विवरण: {description}
- स्थान: {location}
- उपकरण: {equipment}
- प्रक्रियाएं: {procedures}

निम्नलिखित संरचना के साथ JSON प्रारूप में संरचित प्रतिक्रिया प्रदान करें:
{{
  "hazards": [
    {{
      "id": 1,
      "description": "खतरे का विवरण",
      "risk_level": "High|Medium|Low",
      "controls": ["नियंत्रण उपाय 1", "नियंत्रण उपाय 2"],
      "ppe": ["PPE आइटम 1", "PPE आइटम 2"]
    }}
  ],
  "emergency_contacts": {{
    "supervisor": "नाम - फोन",
    "safety_officer": "नाम - फोन"
  }},
  "additional_notes": "कोई अतिरिक्त सुरक्षा विचार"
}}
""",
    "fr": """Vous êtes un expert en sécurité chargé d'analyser les ordres de travail pour générer des rapports d'Analyse des Risques au Travail (JHA).

Analysez l'ordre de travail suivant et identifiez :
1. Tous les risques potentiels (physiques, chimiques, biologiques, ergonomiques)
2. Le niveau de risque pour chaque danger (Élevé/Moyen/Faible)
3. Les mesures de contrôle et d'atténuation recommandées
4. Les équipements de protection individuelle (EPI) requis
5. Les procédures d'urgence et les contacts

Détails de l'ordre de travail :
- ID : {work_order_id}
- Description : {description}
- Lieu : {location}
- Équipement : {equipment}
- Procédures : {procedures}

Fournissez une réponse structurée au format JSON avec la structure suivante :
{{
  "hazards": [
    {{
      "id": 1,
      "description": "Description du danger",
      "risk_level": "High|Medium|Low",
      "controls": ["Mesure de contrôle 1", "Mesure de contrôle 2"],
      "ppe": ["EPI 1", "EPI 2"]
    }}
  ],
  "emergency_contacts": {{
    "supervisor": "Nom - Téléphone",
    "safety_officer": "Nom - Téléphone"
  }},
  "additional_notes": "Toute considération de sécurité supplémentaire"
}}
"""
}

# Language instruction suffix to ensure response language matches
LANGUAGE_INSTRUCTION = {
    "en": "\n\nIMPORTANT: Provide all descriptions, controls, and notes in English.",
    "hi": "\n\nमहत्वपूर्ण: सभी विवरण, नियंत्रण और नोट्स हिंदी में प्रदान करें।",
    "fr": "\n\nIMPORTANT : Fournissez toutes les descriptions, mesures de contrôle et notes en français."
}

# Default Emergency Contacts
DEFAULT_EMERGENCY_CONTACTS = {
    "supervisor": "Contact Supervisor - 555-0100",
    "safety_officer": "Safety Officer - 555-0200",
    "emergency": "Emergency Services - 911"
}

# UI Label Translations
LABEL_TRANSLATIONS = {
    "en": {
        "report_title": "Job Hazard Analysis Report",
        "report_subtitle": "AI-Powered Risk Assessment",
        "report_id": "Report ID",
        "work_order": "Work Order",
        "generated": "Generated",
        "wo_status": "WO Status",
        "work_order_details": "Work Order Details",
        "work_order_number": "Work Order #",
        "description": "Description",
        "location": "Location",
        "equipment": "Equipment",
        "priority": "Priority",
        "status": "Status",
        "assigned_to": "Assigned To",
        "identified_hazards": "Identified Hazards",
        "hazard": "Hazard",
        "risk_level": "Risk Level",
        "controls": "Controls",
        "required_ppe": "Required PPE",
        "emergency_contacts": "Emergency Contacts",
        "supervisor": "Supervisor",
        "safety_officer": "Safety Officer",
        "emergency_services": "Emergency Services",
        "additional_notes": "Additional Notes",
        "field": "Field",
        "value": "Value",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "procedures": "Procedures"
    },
    "hi": {
        "report_title": "जॉब हैज़र्ड एनालिसिस रिपोर्ट",
        "report_subtitle": "AI-संचालित जोखिम मूल्यांकन",
        "report_id": "रिपोर्ट आईडी",
        "work_order": "वर्क ऑर्डर",
        "generated": "उत्पन्न",
        "wo_status": "WO स्थिति",
        "work_order_details": "वर्क ऑर्डर विवरण",
        "work_order_number": "वर्क ऑर्डर नंबर",
        "description": "विवरण",
        "location": "स्थान",
        "equipment": "उपकरण",
        "priority": "प्राथमिकता",
        "status": "स्थिति",
        "assigned_to": "को सौंपा गया",
        "identified_hazards": "पहचाने गए खतरे",
        "hazard": "खतरा",
        "risk_level": "जोखिम स्तर",
        "controls": "नियंत्रण उपाय",
        "required_ppe": "आवश्यक PPE",
        "emergency_contacts": "आपातकालीन संपर्क",
        "supervisor": "पर्यवेक्षक",
        "safety_officer": "सुरक्षा अधिकारी",
        "emergency_services": "आपातकालीन सेवाएं",
        "additional_notes": "अतिरिक्त नोट्स",
        "field": "फील्ड",
        "value": "मान",
        "high": "उच्च",
        "medium": "मध्यम",
        "low": "निम्न",
        "procedures": "प्रक्रियाएं"
    },
    "fr": {
        "report_title": "Rapport d'Analyse des Risques au Travail",
        "report_subtitle": "Évaluation des Risques par IA",
        "report_id": "ID du Rapport",
        "work_order": "Ordre de Travail",
        "generated": "Généré",
        "wo_status": "Statut OT",
        "work_order_details": "Détails de l'Ordre de Travail",
        "work_order_number": "N° d'Ordre de Travail",
        "description": "Description",
        "location": "Lieu",
        "equipment": "Équipement",
        "priority": "Priorité",
        "status": "Statut",
        "assigned_to": "Assigné à",
        "identified_hazards": "Dangers Identifiés",
        "hazard": "Danger",
        "risk_level": "Niveau de Risque",
        "controls": "Mesures de Contrôle",
        "required_ppe": "EPI Requis",
        "emergency_contacts": "Contacts d'Urgence",
        "supervisor": "Superviseur",
        "safety_officer": "Responsable Sécurité",
        "emergency_services": "Services d'Urgence",
        "additional_notes": "Notes Supplémentaires",
        "field": "Champ",
        "value": "Valeur",
        "high": "Élevé",
        "medium": "Moyen",
        "low": "Faible",
        "procedures": "Procédures"
    }
}

# HTTP Status Messages
HTTP_STATUS_MESSAGES = {
    200: "Success",
    201: "Created",
    400: "Bad Request",
    401: "Unauthorized",
    404: "Not Found",
    500: "Internal Server Error",
    503: "Service Unavailable"
}

# API Retry Configuration
RETRY_DELAYS = [1, 2, 4, 8, 16]  # Exponential backoff in seconds
MAX_RETRY_ATTEMPTS = 3

# Cache Configuration
CACHE_KEY_PREFIX = "jha_"
WORK_ORDER_CACHE_KEY = "work_order_{work_order_id}"

# Report Generation
REPORT_TITLE = "Job Hazard Analysis Report"
REPORT_SUBTITLE = "AI-Powered Risk Assessment"
COMPANY_NAME = "IBM Maximo"

# Made with Bob
