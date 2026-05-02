# Maximo API Integration Guide

This document explains how the application integrates with IBM Maximo API based on the actual API structure.

## API Endpoint Structure

### Base URL
```
https://maseam360.manage.maseam360.apps.masdev.eam360.com/maximo/api
```

### Work Order Endpoint
```
GET /os/C_WO
```

## Query Parameters

The application uses OSLC (Open Services for Lifecycle Collaboration) query parameters:

### Required Parameters

1. **lean=1**: Returns minimal response structure
2. **ignorecollectionref=1**: Ignores collection references for performance
3. **oslc.select**: Specifies which fields to return
4. **oslc.where**: Filters the results

### Field Selection (oslc.select)

```
wonum,workorderid,siteid,assetnum,location,
woactivity{taskid,description},
asset{assetnum,description},
locations{location,description}
```

**Fields Explained:**
- `wonum`: Work order number (primary identifier)
- `workorderid`: Internal work order ID
- `siteid`: Site identifier
- `assetnum`: Asset number
- `location`: Location code
- `woactivity`: Array of work activities/tasks
- `asset`: Asset details (nested)
- `locations`: Location details (nested)

### Filter Criteria (oslc.where)

```
siteid="BEDFORD" and WONUM="6455"
```

**Format:**
- Use double quotes for string values
- Combine conditions with `and`
- Field names are case-sensitive

## Authentication

### Headers Required

```http
apikey: your_api_key_here
Cookie: session_cookie_if_needed
```

**Configuration in .env:**
```env
MAXIMO_API_KEY=6l1cccr640vj72m6cn3uo88hbp6568sa3hiup6j
MAXIMO_SITE_ID=BEDFORD
MAXIMO_COOKIE=optional_session_cookie
```

## Response Structure

### Successful Response

```json
{
  "member": [
    {
      "wonum": "6455",
      "workorderid": 12345,
      "siteid": "BEDFORD",
      "assetnum": "HVAC-001",
      "location": "BLDG-A",
      "woactivity": [
        {
          "taskid": "10",
          "description": "Inspect HVAC system"
        },
        {
          "taskid": "20",
          "description": "Replace filters"
        }
      ],
      "asset": [
        {
          "assetnum": "HVAC-001",
          "description": "Main HVAC Unit - Building A"
        }
      ],
      "locations": [
        {
          "location": "BLDG-A",
          "description": "Building A - Floor 3"
        }
      ]
    }
  ]
}
```

### Response Parsing

The application extracts:

1. **Work Order Number**: `wonum` (used as work_order_id)
2. **Description**: From work order or first activity
3. **Location**: Combines location code and description
4. **Equipment**: Combines asset number and description
5. **Procedures**: Concatenates all woactivity descriptions

## Implementation Details

### Service Method

```python
async def get_work_order(self, wonum: str, site_id: Optional[str] = None) -> Optional[WorkOrder]:
    """
    Fetch work order from Maximo.
    
    Args:
        wonum: Work order number (e.g., "6455")
        site_id: Site ID (defaults to BEDFORD)
    
    Returns:
        WorkOrder object with parsed data
    """
```

### Example Usage

```python
from services.maximo_service import maximo_service

# Fetch work order
work_order = await maximo_service.get_work_order("6455")

# With custom site
work_order = await maximo_service.get_work_order("6455", site_id="CUSTOM_SITE")
```

## Caching

Work orders are cached for 5 minutes (300 seconds) to reduce API calls:

```python
MAXIMO_CACHE_TTL=300  # seconds
```

**Cache Key**: Work order number (wonum)

## Error Handling

### Common Errors

1. **404 Not Found**: Work order doesn't exist
   ```json
   {
     "detail": "Work order 6455 not found"
   }
   ```

2. **401 Unauthorized**: Invalid API key
   ```json
   {
     "detail": "Invalid API credentials"
   }
   ```

3. **500 Server Error**: Maximo API error
   ```json
   {
     "detail": "Maximo API connection failed"
   }
   ```

### Retry Logic

The service implements exponential backoff:
- Attempt 1: Immediate
- Attempt 2: 2 seconds delay
- Attempt 3: 5 seconds delay
- Attempt 4: 10 seconds delay (final)

## Testing

### Manual Test with curl

```bash
curl --location --globoff \
  'https://maseam360.manage.maseam360.apps.masdev.eam360.com/maximo/api/os/C_WO?lean=1&ignorecollectionref=1&oslc.select=wonum%2Cworkorderid%2Csiteid%2Cassetnum%2Clocation%2Cwoactivity{taskid%2Cdescription}%2Casset{assetnum%2Cdescription}%2Clocations{location%2Cdescription}&oslc.where=siteid%3D%22BEDFORD%22%20and%20WONUM%3D%226455%22' \
  --header 'apikey: your_api_key' \
  --header 'Cookie: your_session_cookie'
```

### Test via API

```bash
# Test work order fetch
curl http://localhost:8000/api/workorders/6455

# Validate work order
curl -X POST http://localhost:8000/api/workorders/validate \
  -H "Content-Type: application/json" \
  -d '{"work_order_id": "6455"}'
```

## Configuration Checklist

- [ ] Set `MAXIMO_API_URL` in .env
- [ ] Set `MAXIMO_API_KEY` in .env
- [ ] Set `MAXIMO_SITE_ID` in .env (default: BEDFORD)
- [ ] Set `MAXIMO_COOKIE` if required (optional)
- [ ] Test connection with a known work order number
- [ ] Verify response parsing with actual data

## Troubleshooting

### Issue: Empty Response

**Cause**: Work order doesn't exist or wrong site ID

**Solution**: 
- Verify work order number exists in Maximo
- Check site ID matches the work order's site
- Review Maximo logs for access issues

### Issue: Authentication Failed

**Cause**: Invalid API key or expired session

**Solution**:
- Verify API key is correct
- Regenerate API key if expired
- Update Cookie header if using session authentication

### Issue: Parsing Errors

**Cause**: Response structure differs from expected

**Solution**:
- Log raw response: `logger.debug(f"Raw response: {data}")`
- Adjust parsing in `_parse_work_order_response()`
- Check if Maximo version has different field names

## Best Practices

1. **Always specify site_id** when querying work orders
2. **Cache aggressively** to reduce API load
3. **Handle nested arrays** (woactivity, asset, locations) safely
4. **Log API responses** during development for debugging
5. **Use retry logic** for transient failures
6. **Validate work order numbers** before API calls

## API Limits

- **Rate Limit**: Check with Maximo administrator
- **Timeout**: 30 seconds (configurable)
- **Max Retries**: 4 attempts with exponential backoff

## Support

For Maximo API issues:
1. Check Maximo API documentation
2. Verify API key permissions
3. Contact Maximo administrator
4. Review application logs: `logs/app.log`

---

**Last Updated**: 2024-01-15  
**Maximo Version**: Compatible with Maximo 7.6+