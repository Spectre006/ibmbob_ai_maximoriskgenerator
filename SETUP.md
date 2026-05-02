# Setup Guide - Maximo Risk Assessment Generator

## Prerequisites

- Python 3.10 or higher
- IBM Watsonx.ai API credentials
- IBM Maximo API access
- IBM Cloudant database credentials

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/maximo_riskassessement_generator.git
cd maximo_riskassessement_generator
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required environment variables:

```env
# IBM Maximo API
MAXIMO_API_URL=https://your-maximo-instance.com/api
MAXIMO_API_KEY=your_api_key
MAXIMO_USERNAME=your_username
MAXIMO_PASSWORD=your_password

# IBM Watsonx.ai
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2

# IBM Cloudant
CLOUDANT_URL=https://your-account.cloudant.com
CLOUDANT_API_KEY=your_cloudant_api_key
CLOUDANT_DATABASE=jha_reports

# Application
APP_ENV=development
APP_DEBUG=True
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=your_secret_key_here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 5. Create Logs Directory

```bash
mkdir -p logs
```

### 6. Initialize Cloudant Database

The application will automatically create the database on first connection if it doesn't exist.

## Running the Application

### Development Mode

```bash
python app.py
```

The application will start on `http://localhost:8000`

### Production Mode

```bash
# Set environment to production
export APP_ENV=production
export APP_DEBUG=False

# Run with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing the Setup

### 1. Check Health Status

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "message": "Maximo Risk Assessment Generator is running"
}
```

### 2. Check Detailed Health

```bash
curl http://localhost:8000/api/health/detailed
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "maximo": "configured",
    "watsonx": "configured",
    "cloudant": "configured"
  },
  "message": "Service health check complete"
}
```

### 3. Test Work Order Validation

```bash
curl -X POST http://localhost:8000/api/workorders/validate \
  -H "Content-Type: application/json" \
  -d '{"work_order_id": "WO12345"}'
```

### 4. Generate JHA Report

```bash
curl -X POST http://localhost:8000/api/jha/generate \
  -H "Content-Type: application/json" \
  -d '{"work_order_id": "WO12345"}'
```

### 5. List Reports

```bash
curl http://localhost:8000/api/jha/history?limit=5
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Issue: Import errors when starting

**Solution**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt
```

### Issue: Connection errors to IBM services

**Solution**: Verify your credentials in `.env` file
```bash
# Test Maximo connection
curl -H "apikey: YOUR_API_KEY" https://your-maximo-instance.com/api/os/mxwo

# Test Watsonx.ai connection
# Check your API key and project ID in IBM Cloud console

# Test Cloudant connection
curl -H "Authorization: Bearer YOUR_API_KEY" https://your-account.cloudant.com
```

### Issue: Database errors

**Solution**: Ensure Cloudant database exists or application has permission to create it
```bash
# The application will auto-create the database on first run
# Check logs/app.log for detailed error messages
```

### Issue: Port already in use

**Solution**: Change the port in `.env` or kill the process using port 8000
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
export APP_PORT=8001
python app.py
```

## Development Tips

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
python app.py
```

### Clear Maximo Cache

The application caches work orders for 5 minutes. To clear cache, restart the application.

### Monitor Logs

```bash
# Watch logs in real-time
tail -f logs/app.log
```

### Test with Mock Data

For development without IBM services, you can modify the services to return mock data:

1. Edit `services/maximo_service.py` - add mock work order data
2. Edit `services/ai_service.py` - return mock hazard analysis
3. Edit `services/cloudant_service.py` - use in-memory storage

## Next Steps

- **Phase 3**: Implement PDF/Word report generation
- **Phase 4**: Enhance frontend UI
- **Phase 5**: Add comprehensive testing

## Support

For issues or questions:
1. Check logs in `logs/app.log`
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check [README.md](README.md) for project overview