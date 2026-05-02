"""IBM Cloud IAM authentication helper."""

import time
from typing import Optional
import httpx
from utils.logger import get_logger

logger = get_logger(__name__)


class IAMAuthenticator:
    """Handle IBM Cloud IAM authentication."""
    
    def __init__(self, api_key: str):
        """
        Initialize IAM authenticator.
        
        Args:
            api_key: IBM Cloud API key
        """
        self.api_key = api_key
        self.iam_url = "https://iam.cloud.ibm.com/identity/token"
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0
        
        logger.info("IAM Authenticator initialized")
    
    async def get_access_token(self) -> str:
        """
        Get valid IAM access token.
        
        Returns:
            Valid IAM access token
        
        Raises:
            Exception: If token fetch fails
        """
        if self._is_token_valid():
            logger.debug("Using cached IAM token")
            return self._access_token
        
        logger.info("Fetching new IAM access token")
        return await self._fetch_new_token()
    
    def _is_token_valid(self) -> bool:
        """
        Check if current token is still valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self._access_token:
            return False
        
        # Refresh 5 minutes (300 seconds) before expiry
        return time.time() < (self._token_expiry - 300)
    
    async def _fetch_new_token(self) -> str:
        """
        Fetch new IAM access token from IBM Cloud.
        
        Returns:
            New access token
        
        Raises:
            Exception: If token fetch fails
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.iam_url,
                    headers=headers,
                    data=data
                )
                response.raise_for_status()
                
                token_data = response.json()
                self._access_token = token_data["access_token"]
                
                # Set expiry time (default 3600 seconds = 1 hour)
                expires_in = token_data.get("expires_in", 3600)
                self._token_expiry = time.time() + expires_in
                
                logger.info(f"Successfully obtained IAM access token (expires in {expires_in}s)")
                return self._access_token
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get IAM token: {e}")
            raise Exception(f"IAM authentication failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting IAM token: {e}")
            raise Exception(f"IAM authentication failed: {str(e)}")
    
    def clear_token(self):
        """Clear cached token (force refresh on next request)."""
        self._access_token = None
        self._token_expiry = 0
        logger.info("IAM token cache cleared")


# Made with Bob