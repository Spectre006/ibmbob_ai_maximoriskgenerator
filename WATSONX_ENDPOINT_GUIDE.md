# Watsonx.ai Endpoint Configuration Guide

## Current Error: 404 Not Found

```
ERROR - Watsonx.ai API error: Client error '404 Not Found' for url 
'https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29'
```

## Root Cause

The 404 error indicates one of these issues:
1. **Wrong API endpoint URL**
2. **Wrong API version**
3. **Wrong region**
4. **Model not available in your instance**

## Solution Steps

### Step 1: Verify Your Watsonx.ai Instance

Check your IBM Cloud Watsonx.ai dashboard to find:
1. **Service URL** - The correct base URL for your instance
2. **Project ID** - Your project identifier
3. **Available Models** - Which models you have access to

### Step 2: Common Watsonx.ai Endpoints

IBM Watsonx.ai has different endpoint formats depending on the service type:

#### Option 1: Watsonx.ai SaaS (Cloud)
```
https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29
```

#### Option 2: Watsonx.ai on IBM Cloud Pak for Data
```
https://{cpd_cluster_host}/ml/v4/deployments/{deployment_id}/predictions
```

#### Option 3: Watsonx.ai with Different Regions
- **US South**: `https://us-south.ml.cloud.ibm.com`
- **EU Germany**: `https://eu-de.ml.cloud.ibm.com`
- **Japan Tokyo**: `https://jp-tok.ml.cloud.ibm.com`
- **UK London**: `https://eu-gb.ml.cloud.ibm.com`

### Step 3: Check API Version

Try different API versions:
- `version=2023-05-29` (current)
- `version=2024-01-01` (newer)
- `version=2023-10-25` (alternative)

### Step 4: Verify Model ID

Common Watsonx.ai model IDs:
- `ibm/granite-13b-chat-v2` (current setting)
- `ibm/granite-13b-instruct-v2`
- `meta-llama/llama-2-70b-chat`
- `google/flan-ul2`

Check which models are available in your Watsonx.ai project.

## Testing the Endpoint

### Test 1: Check Service Availability

```bash
# Get IAM token
IAM_TOKEN=$(curl -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_API_KEY" \
  | jq -r '.access_token')

# Test endpoint
curl -X POST "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29" \
  -H "Authorization: Bearer $IAM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "ibm/granite-13b-chat-v2",
    "input": "Hello",
    "parameters": {"max_new_tokens": 10},
    "project_id": "YOUR_PROJECT_ID"
  }'
```

### Test 2: List Available Models

```bash
# List models in your project
curl -X GET "https://us-south.ml.cloud.ibm.com/ml/v4/foundation_model_specs?version=2023-05-29" \
  -H "Authorization: Bearer $IAM_TOKEN"
```

### Test 3: Verify Project Access

```bash
# Get project details
curl -X GET "https://us-south.ml.cloud.ibm.com/v2/projects/YOUR_PROJECT_ID" \
  -H "Authorization: Bearer $IAM_TOKEN"
```

## Configuration Updates

### Update .env File

Based on your Watsonx.ai instance, update these values:

```env
# Watsonx.ai Configuration
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
```

### Alternative Endpoints to Try

If the current endpoint doesn't work, try these in order:

1. **With v4 API**:
   ```env
   WATSONX_URL=https://us-south.ml.cloud.ibm.com
   # Update code to use: /ml/v4/text/generation
   ```

2. **Different version**:
   ```env
   # Try version=2024-01-01 or version=2023-10-25
   ```

3. **Different region**:
   ```env
   WATSONX_URL=https://eu-de.ml.cloud.ibm.com
   ```

## Code Changes for Different Endpoints

### For v4 API (if needed)

Update `services/ai_service.py`:

```python
# Change endpoint from:
endpoint = f"{self.url}/ml/v1/text/generation?version=2023-05-29"

# To:
endpoint = f"{self.url}/ml/v4/text/generation?version=2023-05-29"
```

### For Deployment-based Endpoint

If using a specific deployment:

```python
# Add to settings
WATSONX_DEPLOYMENT_ID=your_deployment_id

# Update endpoint
endpoint = f"{self.url}/ml/v4/deployments/{self.deployment_id}/text/generation?version=2023-05-29"
```

## Debugging Steps

### Enable Debug Logging

Set in `.env`:
```env
LOG_LEVEL=DEBUG
```

This will show:
- Exact endpoint being called
- Model ID being used
- Project ID being sent
- Response status and body

### Check Logs

```bash
tail -f logs/app.log
```

Look for:
```
DEBUG - Calling Watsonx.ai endpoint: https://...
DEBUG - Using model: ibm/granite-13b-chat-v2
DEBUG - Project ID: your-project-id
DEBUG - Response status: 404
ERROR - Response body: {"error": "..."}
```

## Common 404 Causes and Fixes

### Cause 1: Wrong Project ID

**Symptom**: 404 with message about project not found

**Fix**: 
1. Go to IBM Cloud Watsonx.ai console
2. Open your project
3. Copy the correct Project ID from URL or settings
4. Update `WATSONX_PROJECT_ID` in `.env`

### Cause 2: Model Not Available

**Symptom**: 404 with message about model not found

**Fix**:
1. Check available models in your project
2. Use a model you have access to
3. Update `WATSONX_MODEL_ID` in `.env`

### Cause 3: Wrong API Version

**Symptom**: 404 on the endpoint itself

**Fix**:
Try different versions:
- `version=2024-01-01`
- `version=2023-10-25`
- `version=2023-05-29`

### Cause 4: Service Not Provisioned

**Symptom**: 404 on base URL

**Fix**:
1. Verify Watsonx.ai service is provisioned in IBM Cloud
2. Check service status in IBM Cloud dashboard
3. Ensure you have the correct service URL

## Quick Diagnostic Script

Create `test_watsonx.py`:

```python
import asyncio
import httpx
from services.iam_auth import IAMAuthenticator
from config.settings import settings

async def test_watsonx():
    # Get IAM token
    auth = IAMAuthenticator(settings.watsonx_api_key)
    token = await auth.get_access_token()
    print(f"✓ IAM Token obtained: {token[:20]}...")
    
    # Test different endpoints
    endpoints = [
        f"{settings.watsonx_url}/ml/v1/text/generation?version=2023-05-29",
        f"{settings.watsonx_url}/ml/v4/text/generation?version=2023-05-29",
        f"{settings.watsonx_url}/ml/v1/text/generation?version=2024-01-01",
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        
        payload = {
            "model_id": settings.watsonx_model_id,
            "input": "Test",
            "parameters": {"max_new_tokens": 5},
            "project_id": settings.watsonx_project_id
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                print(f"  Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"  ✓ SUCCESS!")
                    print(f"  Response: {response.json()}")
                    return
                else:
                    print(f"  ✗ Error: {response.text[:200]}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_watsonx())
```

Run it:
```bash
python test_watsonx.py
```

## Next Steps

1. **Check IBM Cloud Console**:
   - Verify Watsonx.ai service is active
   - Note the exact service URL
   - Confirm Project ID
   - Check available models

2. **Run Diagnostic Script**:
   - Test different endpoint variations
   - Identify which one works

3. **Update Configuration**:
   - Update `.env` with correct values
   - Restart application

4. **Test JHA Generation**:
   - Try generating a report again
   - Check logs for success

## Support

If still getting 404:
1. Check IBM Cloud Watsonx.ai documentation for your specific instance
2. Verify service provisioning in IBM Cloud console
3. Contact IBM Cloud support with:
   - Your Project ID
   - Service instance details
   - Error logs

---

**Last Updated**: 2024-01-15