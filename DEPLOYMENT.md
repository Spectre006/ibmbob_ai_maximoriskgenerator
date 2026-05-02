# Deployment Guide

Complete deployment guide for the Maximo Risk Assessment Generator.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Monitoring & Logging](#monitoring--logging)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Python**: 3.10 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 1GB free space
- **Network**: Internet access for IBM Cloud services

### Required IBM Services

1. **IBM Watsonx.ai**
   - Active account with API access
   - Project ID and API key
   - Model: `ibm/granite-13b-chat-v2`

2. **IBM Maximo**
   - API endpoint URL
   - Valid credentials (API key or username/password)
   - Read access to work orders

3. **IBM Cloudant**
   - Database instance created
   - API key with read/write permissions
   - Database name configured

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/maximo_riskassessement_generator.git
cd maximo_riskassessement_generator
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# IBM Maximo
MAXIMO_API_URL=https://your-maximo-instance.com/api
MAXIMO_API_KEY=your_api_key
MAXIMO_USERNAME=your_username
MAXIMO_PASSWORD=your_password

# IBM Watsonx.ai
WATSONX_API_KEY=your_watsonx_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-chat-v2

# IBM Cloudant
CLOUDANT_URL=https://your-account.cloudantnosqldb.appdomain.cloud
CLOUDANT_API_KEY=your_cloudant_key
CLOUDANT_DATABASE=jha_reports

# Application
APP_ENV=development
APP_DEBUG=True
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=generate_a_secure_random_key_here
```

### 5. Create Required Directories

```bash
mkdir -p logs
mkdir -p static/uploads
```

### 6. Run Application

```bash
python app.py
```

Access at: `http://localhost:8000`

---

## Production Deployment

### Option 1: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs static/uploads

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./static/uploads:/app/static/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### 3. Build and Run

```bash
docker-compose up -d
```

### Option 2: IBM Cloud Foundry

#### 1. Create manifest.yml

```yaml
applications:
- name: maximo-risk-assessment
  memory: 512M
  instances: 1
  buildpack: python_buildpack
  command: python app.py
  env:
    PYTHONUNBUFFERED: true
```

#### 2. Deploy

```bash
ibmcloud login
ibmcloud target --cf
ibmcloud cf push
```

### Option 3: Kubernetes Deployment

#### 1. Create deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maximo-risk-assessment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: maximo-risk-assessment
  template:
    metadata:
      labels:
        app: maximo-risk-assessment
    spec:
      containers:
      - name: app
        image: your-registry/maximo-risk-assessment:latest
        ports:
        - containerPort: 8000
        env:
        - name: APP_ENV
          value: "production"
        envFrom:
        - secretRef:
            name: maximo-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: maximo-risk-assessment
spec:
  selector:
    app: maximo-risk-assessment
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### 2. Deploy to Kubernetes

```bash
kubectl apply -f deployment.yaml
kubectl apply -f secrets.yaml
```

---

## Environment Configuration

### Production Environment Variables

```env
# Application
APP_ENV=production
APP_DEBUG=False
APP_HOST=0.0.0.0
APP_PORT=8000
SECRET_KEY=<generate-secure-key>

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Performance
MAXIMO_CACHE_TTL=300
AI_TIMEOUT=30
MAX_RETRIES=3
WORKERS=4

# Security (if implementing authentication)
JWT_SECRET_KEY=<generate-secure-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Generating Secure Keys

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Database Setup

### IBM Cloudant Configuration

#### 1. Create Database

```bash
curl -X PUT https://$CLOUDANT_URL/jha_reports \
  -H "Authorization: Bearer $CLOUDANT_API_KEY"
```

#### 2. Create Indexes

```bash
curl -X POST https://$CLOUDANT_URL/jha_reports/_index \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CLOUDANT_API_KEY" \
  -d '{
    "index": {
      "fields": ["work_order_id", "created_at"]
    },
    "name": "work-order-index",
    "type": "json"
  }'
```

#### 3. Verify Setup

```python
from services.cloudant_service import CloudantService

service = CloudantService()
# Test connection
result = service.test_connection()
print(f"Connection status: {result}")
```

---

## Monitoring & Logging

### Application Logs

Logs are stored in `logs/app.log` with rotation:

```python
# Log format
[2024-01-15 10:30:00] INFO - JHA report generated for WO12345 in 8.5s
[2024-01-15 10:30:05] ERROR - Maximo API connection failed: timeout
```

### Health Check Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/api/health/detailed
```

### Monitoring Metrics

Key metrics to monitor:

- **Response Time**: Target < 10 seconds for JHA generation
- **Error Rate**: Should be < 5%
- **API Availability**: Maximo, Watsonx, Cloudant uptime
- **Memory Usage**: Should stay under 1GB
- **CPU Usage**: Should stay under 50%

### Log Aggregation (Production)

For production, consider using:

- **IBM Log Analysis**: Native IBM Cloud solution
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Splunk**: Enterprise log management

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
pip install -r requirements.txt
```

#### 2. API Connection Failures

**Problem**: Cannot connect to IBM services

**Solution**:
- Verify credentials in `.env`
- Check network connectivity
- Verify API endpoints are correct
- Check API key permissions

#### 3. Database Errors

**Problem**: Cloudant connection fails

**Solution**:
```bash
# Test Cloudant connection
curl -X GET https://$CLOUDANT_URL/_all_dbs \
  -H "Authorization: Bearer $CLOUDANT_API_KEY"
```

#### 4. Performance Issues

**Problem**: Report generation takes > 10 seconds

**Solution**:
- Check Watsonx.ai API quota
- Verify network latency
- Review logs for bottlenecks
- Consider caching work order data

#### 5. Memory Issues

**Problem**: Application crashes with memory errors

**Solution**:
- Increase container memory limits
- Reduce concurrent requests
- Implement request queuing
- Monitor memory usage

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
APP_DEBUG=True
```

View detailed logs:

```bash
tail -f logs/app.log
```

### Testing Deployment

```bash
# Run health check
curl http://localhost:8000/health

# Test work order fetch
curl http://localhost:8000/api/workorders/WO12345

# Generate test report
curl -X POST http://localhost:8000/api/jha/generate \
  -H "Content-Type: application/json" \
  -d '{"work_order_id": "WO12345"}'
```

---

## Security Best Practices

### 1. Environment Variables

- Never commit `.env` file to version control
- Use secrets management in production (e.g., IBM Secrets Manager)
- Rotate API keys regularly

### 2. HTTPS

Enable HTTPS in production:

```python
# In app.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="path/to/key.pem",
        ssl_certfile="path/to/cert.pem"
    )
```

### 3. Rate Limiting

Implement rate limiting for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### 4. Input Validation

All inputs are validated using Pydantic models. Ensure validation is enabled.

---

## Backup & Recovery

### Database Backup

```bash
# Backup Cloudant database
curl -X GET https://$CLOUDANT_URL/jha_reports/_all_docs?include_docs=true \
  -H "Authorization: Bearer $CLOUDANT_API_KEY" \
  > backup_$(date +%Y%m%d).json
```

### Restore Database

```bash
# Restore from backup
curl -X POST https://$CLOUDANT_URL/jha_reports/_bulk_docs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CLOUDANT_API_KEY" \
  -d @backup_20240115.json
```

---

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple instances behind a load balancer
- Use session affinity if needed
- Share logs via centralized logging

### Vertical Scaling

- Increase memory allocation
- Add more CPU cores
- Optimize database queries

### Caching Strategy

- Cache work order data (5-minute TTL)
- Cache AI responses for identical requests
- Use Redis for distributed caching

---

## Support

For deployment issues:

1. Check logs: `logs/app.log`
2. Review [ARCHITECTURE.md](ARCHITECTURE.md)
3. Consult [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
4. Contact development team

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0