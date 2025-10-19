# Math Routing Agent - Deployment Guide

## Overview

This guide covers deploying the Math Routing Agent system in various environments, from local development to production.

## Prerequisites

- Python 3.8+
- Node.js 16+
- Docker and Docker Compose
- Qdrant vector database
- API keys for external services

## Local Development

### 1. Backend Setup

```bash
# Clone repository
git clone <repository-url>
cd math_rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Run backend
python -m src.main
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Docker Deployment

### 1. Create Docker Compose File

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - EXA_API_KEY=${EXA_API_KEY}
      - SERPER_API_KEY=${SERPER_API_KEY}
    depends_on:
      - qdrant
    volumes:
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  qdrant_data:
```

### 2. Create Dockerfiles

**Backend Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY env.example .env

EXPOSE 8000

CMD ["python", "-m", "src.main"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

### 3. Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Deployment

### 1. AWS Deployment

#### Using AWS ECS

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name math-routing-agent

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service --cluster math-routing-agent --service-name math-agent-service --task-definition math-routing-agent:1 --desired-count 1
```

#### Using AWS Lambda

```python
# lambda_handler.py
import json
from src.main import app

def lambda_handler(event, context):
    # Process API Gateway event
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Math Routing Agent'})
    }
```

### 2. Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/math-routing-agent

# Deploy to Cloud Run
gcloud run deploy math-routing-agent --image gcr.io/PROJECT_ID/math-routing-agent --platform managed --region us-central1
```

### 3. Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name math-routing-agent --location eastus

# Create container instance
az container create --resource-group math-routing-agent --name math-agent --image your-registry/math-routing-agent --dns-name-label math-agent --ports 8000
```

## Environment Configuration

### 1. Production Environment Variables

```env
# Production settings
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Redis for caching
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret

# External APIs
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key
EXA_API_KEY=your-exa-key
SERPER_API_KEY=your-serper-key

# Qdrant
QDRANT_URL=https://your-qdrant-cluster.com
QDRANT_API_KEY=your-qdrant-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### 2. Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Database Setup

### 1. Qdrant Cloud

```bash
# Create cluster
curl -X POST "https://api.qdrant.tech/collections" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_API_KEY" \
  -d '{
    "name": "math_knowledge",
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }'
```

### 2. PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE math_agent;

-- Create user
CREATE USER math_agent_user WITH PASSWORD 'your_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE math_agent TO math_agent_user;
```

## Monitoring and Logging

### 1. Application Monitoring

```python
# monitoring.py
import logging
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
query_counter = Counter('math_queries_total', 'Total math queries')
response_time = Histogram('math_response_time_seconds', 'Response time')

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Health Checks

```python
# health_check.py
import requests
import time

def check_health():
    try:
        response = requests.get('http://localhost:8000/health')
        return response.status_code == 200
    except:
        return False

def monitor_health():
    while True:
        if not check_health():
            # Send alert
            send_alert("Math Routing Agent is down")
        time.sleep(60)
```

## Security Considerations

### 1. API Security

```python
# security.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not verify_jwt_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials
```

### 2. Rate Limiting

```python
# rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/query")
@limiter.limit("10/minute")
async def query(request: Request, ...):
    # Your endpoint logic
```

## Backup and Recovery

### 1. Database Backup

```bash
# Qdrant backup
curl -X POST "https://api.qdrant.tech/collections/math_knowledge/snapshots" \
  -H "api-key: YOUR_API_KEY"

# PostgreSQL backup
pg_dump -h localhost -U math_agent_user math_agent > backup.sql
```

### 2. Application Backup

```bash
# Backup application data
tar -czf math_agent_backup_$(date +%Y%m%d).tar.gz /app/data/

# Backup configuration
cp .env config_backup_$(date +%Y%m%d).env
```

## Troubleshooting

### 1. Common Issues

**Qdrant Connection Error:**
```bash
# Check Qdrant status
curl http://localhost:6333/collections

# Restart Qdrant
docker restart qdrant
```

**API Key Issues:**
```bash
# Test API keys
python -c "import openai; print(openai.api_key)"
```

**Memory Issues:**
```bash
# Monitor memory usage
docker stats

# Increase memory limits
docker run -m 2g qdrant/qdrant
```

### 2. Log Analysis

```bash
# View application logs
docker-compose logs -f backend

# Search for errors
docker-compose logs backend | grep ERROR

# Monitor performance
docker-compose logs backend | grep "response_time"
```

## Performance Optimization

### 1. Caching

```python
# caching.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 2. Load Balancing

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

## Scaling

### 1. Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - WORKER_ID=${WORKER_ID}
```

### 2. Database Scaling

```yaml
# qdrant-cluster.yml
version: '3.8'
services:
  qdrant-1:
    image: qdrant/qdrant
    environment:
      - QDRANT__CLUSTER__ENABLED=true
      - QDRANT__CLUSTER__P2P__PORT=6335
  
  qdrant-2:
    image: qdrant/qdrant
    environment:
      - QDRANT__CLUSTER__ENABLED=true
      - QDRANT__CLUSTER__P2P__PORT=6335
```

This deployment guide provides comprehensive instructions for deploying the Math Routing Agent system in various environments. Choose the deployment method that best fits your requirements and infrastructure.
