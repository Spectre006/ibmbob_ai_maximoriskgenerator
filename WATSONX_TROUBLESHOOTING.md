# Watsonx.ai Authentication Troubleshooting

## Error: 401 Unauthorized

```
ERROR - Watsonx.ai API error: Client error '401 Unauthorized' for url 'https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29'
```

**Location**: `services/ai_service.py` line 92-96

## Root Cause

The 401 error indicates authentication failure. IBM Watsonx.ai requires proper authentication setup.

## Authentication Methods

IBM Watsonx.ai supports two authentication methods:

### Method 1: IAM API Key (Recommended)

IBM Cloud uses IAM (Identity and Access Management) tokens, not direct API keys as Bearer tokens.

**Steps to fix:**

1. **Get IAM Token from API Key**

The API key needs to be exchanged for an IAM access token first:

```python
import httpx

async def get_iam_token(api_key: str) -> str:
    """Exchange API key for IAM access token."""
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
```

2. **Update `_get_headers()` method in `ai_service.py`:**

```python
async def _get_headers(self) -> Dict[str, str]:
    """Get HTTP headers for Watsonx.ai API requests."""
    # Get IAM token
    iam_token = await self._get_iam_token()
    
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {iam_token}"
    }

async def _get_iam_token(self) -> str:
    """Get IAM access token from API key."""
    if hasattr(self, '_cached_token') and self._token_valid():
        return self._cached_token
    
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": self.api_key
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        self._cached_token = token_data["access_token"]
        self._token_expiry = time.time() + token_data.get("expires_in", 3600) - 300
        
        return self._cached_token

def _token_valid(self) -> bool:
    """Check if cached token is still valid."""
    return hasattr(self, '_token_expiry') and time.time() < self._token_expiry
```

### Method 2: Direct API Key (If Supported)

Some IBM services accept API key directly in headers:

```python
def _get_headers(self) -> Dict[str, str]:
    """Get HTTP headers for Watsonx.ai API requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {self.api_key}",  # Current method
        # OR
        "X-IBM-Client-Id": self.api_key,  # Alternative
        # OR  
        "apikey": self.api_key  # Alternative
    }
```

## Quick Fix Steps

### Step 1: Verify API Key

```bash
# Test if API key is valid
curl -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "expiration": 1234567890
}
```

### Step 2: Test Watsonx.ai with IAM Token

```bash
# Get IAM token first
IAM_TOKEN=$(curl -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY" \
  | jq -r '.access_token')

# Test Watsonx.ai
curl -X POST "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29" \
  -H "Authorization: Bearer $IAM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "ibm/granite-13b-chat-v2",
    "input": "Test",
    "parameters": {"max_new_tokens": 10},
    "project_id": "YOUR_PROJECT_ID"
  }'
```

### Step 3: Update Configuration

Ensure `.env` has correct values:

```env
# Watsonx.ai Configuration
WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

## Common Issues

### Issue 1: Wrong API Key Format

**Symptom**: 401 Unauthorized

**Solution**: 
- API key should start with specific prefix (check IBM Cloud console)
- Ensure no extra spaces or newlines
- Regenerate API key if unsure

### Issue 2: Wrong Project ID

**Symptom**: 401 or 403 error

**Solution**:
- Verify project ID in IBM Cloud Watsonx.ai console
- Ensure API key has access to the project
- Check project permissions

### Issue 3: Wrong Region/URL

**Symptom**: Connection timeout or 404

**Solution**:
- Verify region: `us-south`, `eu-de`, `jp-tok`, etc.
- Update URL: `https://{region}.ml.cloud.ibm.com`

### Issue 4: Token Expiration

**Symptom**: Works initially, then fails after ~1 hour

**Solution**:
- Implement token caching with refresh
- IAM tokens expire after 1 hour
- Cache and refresh before expiry

## Recommended Implementation

Create a new file `services/iam_auth.py`:

```python
"""IBM Cloud IAM authentication helper."""

import time
from typing import Optional
import httpx
from utils.logger import get_logger

logger = get_logger(__name__)


class IAMAuthenticator:
    """Handle IBM Cloud IAM authentication."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.iam_url = "https://iam.cloud.ibm.com/identity/token"
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0
    
    async def get_access_token(self) -> str:
        """Get valid IAM access token."""
        if self._is_token_valid():
            return self._access_token
        
        return await self._fetch_new_token()
    
    def _is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        if not self._access_token:
            return False
        
        # Refresh 5 minutes before expiry
        return time.time() < (self._token_expiry - 300)
    
    async def _fetch_new_token(self) -> str:
        """Fetch new IAM access token."""
        logger.info("Fetching new IAM access token")
        
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
                self._token_expiry = time.time() + token_data.get("expires_in", 3600)
                
                logger.info("Successfully obtained IAM access token")
                return self._access_token
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get IAM token: {e}")
            raise Exception(f"IAM authentication failed: {str(e)}")
```

Then update `ai_service.py`:

```python
from services.iam_auth import IAMAuthenticator

class WatsonxAIService:
    def __init__(self):
        # ... existing code ...
        self.authenticator = IAMAuthenticator(self.api_key)
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with valid IAM token."""
        access_token = await self.authenticator.get_access_token()
        
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
```

## Testing Authentication

Add this test endpoint to verify authentication:

```python
# In routes/health_routes.py

@router.get("/api/health/watsonx")
async def test_watsonx_connection():
    """Test Watsonx.ai connection and authentication."""
    from services.ai_service import watsonx_service
    
    try:
        is_connected = await watsonx_service.test_connection()
        return {
            "service": "watsonx",
            "status": "connected" if is_connected else "failed",
            "authenticated": is_connected
        }
    except Exception as e:
        return {
            "service": "watsonx",
            "status": "error",
            "error": str(e)
        }
```

Test it:
```bash
curl http://localhost:8000/api/health/watsonx
```

## Support Resources

- **IBM Cloud IAM Docs**: https://cloud.ibm.com/docs/account?topic=account-iamoverview
- **Watsonx.ai API Docs**: https://cloud.ibm.com/apidocs/watsonx-ai
- **API Key Management**: https://cloud.ibm.com/iam/apikeys

## Next Steps

1. Implement IAM token authentication
2. Test with your actual API key
3. Add token caching for performance
4. Monitor token refresh in logs
5. Add retry logic for token refresh failures

---

**Last Updated**: 2024-01-15