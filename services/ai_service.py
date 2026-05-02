"""IBM Watsonx.ai integration service."""

import json
from typing import Dict, Any, List, Optional
import httpx

from config.settings import settings
from config.constants import (
    SYSTEM_PROMPT_TEMPLATE,
    SYSTEM_PROMPT_TEMPLATES,
    LANGUAGE_INSTRUCTION,
    DEFAULT_EMERGENCY_CONTACTS
)
from utils.logger import get_logger
from models.work_order import WorkOrder
from models.jha_report import Hazard
from services.iam_auth import IAMAuthenticator

logger = get_logger(__name__)


class WatsonxAIService:
    """Service for interacting with IBM Watsonx.ai."""
    
    def __init__(self):
        """Initialize Watsonx.ai service with configuration."""
        self.api_key = settings.watsonx_api_key
        self.project_id = settings.watsonx_project_id
        self.url = settings.watsonx_url
        self.model_id = settings.watsonx_model_id
        self.timeout = settings.ai_timeout
        
        # Initialize IAM authenticator
        self.authenticator = IAMAuthenticator(self.api_key)
        
        logger.info(f"Watsonx.ai service initialized with model: {self.model_id}")
    
    async def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for Watsonx.ai API requests with IAM token.
        
        Returns:
            Dictionary of HTTP headers with valid IAM access token
        """
        # Get valid IAM access token
        access_token = await self.authenticator.get_access_token()
        
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    
    def _build_prompt(self, work_order: WorkOrder, language: str = "en") -> str:
        """
        Build AI prompt from work order data in specified language.
        
        Args:
            work_order: Work order object
            language: Target language code (en, zh, hi)
        
        Returns:
            Formatted prompt string in specified language
        """
        # Get language-specific template, fallback to English
        template = SYSTEM_PROMPT_TEMPLATES.get(language, SYSTEM_PROMPT_TEMPLATE)
        
        # Format the prompt with work order data
        prompt = template.format(
            work_order_id=work_order.work_order_id,
            description=work_order.description or "No description provided",
            location=work_order.location or "Location not specified",
            equipment=work_order.equipment or "Equipment not specified",
            procedures=work_order.procedures or "Procedures not specified"
        )
        
        # Add language instruction to ensure response is in correct language
        language_suffix = LANGUAGE_INSTRUCTION.get(language, LANGUAGE_INSTRUCTION["en"])
        prompt += language_suffix
        
        return prompt
    
    async def analyze_work_order(self, work_order: WorkOrder, language: str = "en") -> Dict[str, Any]:
        """
        Analyze work order using Watsonx.ai to identify hazards and risks.
        
        Args:
            work_order: Work order to analyze
            language: Target language for report generation (en, zh, hi)
        
        Returns:
            Dictionary containing hazards, risk assessment, and recommendations
        
        Raises:
            Exception: If AI analysis fails
        """
        logger.info(f"Analyzing work order {work_order.work_order_id} with Watsonx.ai in language: {language}")
        
        try:
            prompt = self._build_prompt(work_order, language)
            
            # Prepare request payload for Watsonx.ai
            # According to IBM documentation: https://www.ibm.com/watsonx/developer/capabilities/text-generation/
            payload = {
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 2000,
                    "min_new_tokens": 100,
                    "temperature": 0.7,
                    "top_k": 50,
                    "top_p": 1,
                    "repetition_penalty": 1.0
                },
                "model_id": self.model_id,
                "project_id": self.project_id
            }
            
            # Make API request with IAM authentication
            headers = await self._get_headers()
            
            # Watsonx.ai endpoint according to official documentation
            # https://www.ibm.com/watsonx/developer/capabilities/text-generation/
            endpoint = f"{self.url}/ml/v1/text/generation?version=2024-03-14"
            
            logger.debug(f"Calling Watsonx.ai endpoint: {endpoint}")
            logger.debug(f"Using model: {self.model_id}")
            logger.debug(f"Project ID: {self.project_id}")
            logger.debug(f"Payload: {payload}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )
                
                # Log response for debugging
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    logger.error(f"Response body: {response.text}")
                    logger.error(f"Request URL: {response.request.url}")
                    logger.error(f"Request headers: {dict(response.request.headers)}")
                
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Watsonx.ai raw response: {result}")
                
                # Extract generated text
                generated_text = result.get("results", [{}])[0].get("generated_text", "")
                
                # Parse AI response
                analysis = self._parse_ai_response(generated_text)
                
                logger.info(f"Successfully analyzed work order {work_order.work_order_id}")
                return analysis
                
        except httpx.HTTPError as e:
            logger.error(f"Watsonx.ai API error: {e}")
            raise Exception(f"AI analysis failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during AI analysis: {e}")
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _parse_ai_response(self, generated_text: str) -> Dict[str, Any]:
        """
        Parse AI-generated text into structured format.
        
        Args:
            generated_text: Raw text from AI model
        
        Returns:
            Structured dictionary with hazards and recommendations
        """
        try:
            # Try to parse as JSON first
            # AI should return JSON format based on prompt
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = generated_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Validate and structure the response
                return self._validate_and_structure_response(parsed)
            else:
                # Fallback: parse unstructured text
                logger.warning("AI response not in JSON format, using fallback parser")
                return self._parse_unstructured_response(generated_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            return self._parse_unstructured_response(generated_text)
    
    def _validate_and_structure_response(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and structure AI response.
        
        Args:
            parsed: Parsed JSON from AI
        
        Returns:
            Validated and structured response
        """
        hazards = parsed.get("hazards", [])
        
        # Ensure each hazard has required fields
        structured_hazards = []
        for idx, hazard in enumerate(hazards, 1):
            structured_hazards.append({
                "id": hazard.get("id", idx),
                "description": hazard.get("description", "Unspecified hazard"),
                "risk_level": hazard.get("risk_level", "Medium"),
                "controls": hazard.get("controls", []),
                "ppe": hazard.get("ppe", [])
            })
        
        return {
            "hazards": structured_hazards,
            "emergency_contacts": parsed.get("emergency_contacts", DEFAULT_EMERGENCY_CONTACTS),
            "additional_notes": parsed.get("additional_notes", "")
        }
    
    def _parse_unstructured_response(self, text: str) -> Dict[str, Any]:
        """
        Fallback parser for unstructured AI response.
        
        Args:
            text: Unstructured text from AI
        
        Returns:
            Best-effort structured response
        """
        logger.info("Using fallback parser for unstructured AI response")
        
        # Simple fallback: create a single hazard from the text
        return {
            "hazards": [
                {
                    "id": 1,
                    "description": "General safety concerns identified. Please review work order details carefully.",
                    "risk_level": "Medium",
                    "controls": ["Follow standard safety procedures", "Consult with supervisor"],
                    "ppe": ["Standard PPE as per company policy"]
                }
            ],
            "emergency_contacts": DEFAULT_EMERGENCY_CONTACTS,
            "additional_notes": f"AI analysis summary: {text[:500]}"
        }
    
    async def test_connection(self) -> bool:
        """
        Test connection to Watsonx.ai API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test request
            payload = {
                "input": "Test connection",
                "parameters": {
                    "max_new_tokens": 10
                },
                "model_id": self.model_id,
                "project_id": self.project_id
            }
            
            headers = await self._get_headers()
            
            logger.debug(f"Testing connection to: {self.url}/ml/v1/text/generation")
            logger.debug(f"Test payload: {payload}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.url}/ml/v1/text/generation?version=2023-05-29",
                    headers=headers,
                    json=payload
                )
                
                logger.debug(f"Test response status: {response.status_code}")
                if response.status_code != 200:
                    logger.error(f"Test response body: {response.text}")
                
                response.raise_for_status()
                
            logger.info("Watsonx.ai connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Watsonx.ai connection test failed: {e}")
            return False


# Global service instance
watsonx_service = WatsonxAIService()

# Made with Bob
