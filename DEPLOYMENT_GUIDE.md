# BB Agent Manager - Microservice Deployment Guide

## Deployment Architectures

BB Agent Manager supports multiple deployment patterns depending on your needs:

### 1. Plugin Mode (Embedded)
Best for: Single-node deployments, development, simple setups
- bb-agent-manager runs **inside** BabbleBeaver's process
- Lowest latency, shared resources
- Deployed as a Python package

### 2. Microservice Mode (Independent)
Best for: Production, scaling, isolation, cloud deployments
- bb-agent-manager runs as **separate service**
- Independent scaling, better isolation
- Communicates via HTTP APIs

---

## Plugin Mode Deployment

### Quick Setup
```bash
# Install in BabbleBeaver's environment
pip install git+https://github.com/Buildly-Labs/bb-agent-manager.git

# Modify BabbleBeaver's main.py
from bb_agent_manager import register as register_bb_agent
register_bb_agent(app, {})
```

### Docker Plugin Mode
```dockerfile
# In BabbleBeaver's Dockerfile
FROM python:3.11-slim
# ... BabbleBeaver setup ...
RUN pip install git+https://github.com/Buildly-Labs/bb-agent-manager.git
```

---

## Microservice Mode Deployment

### Architecture Overview
```
┌─────────────────┐    HTTP     ┌─────────────────┐
│   BabbleBeaver  │ ◄────────► │ BB Agent Manager│
│   Port: 8000    │             │   Port: 8001    │
└─────────────────┘             └─────────────────┘
         │                               │
         ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│   Chat UI       │             │   AI Tools      │
│   Templates     │             │   DevDocs       │
│   Static Files  │             │   Labs Sync     │
└─────────────────┘             └─────────────────┘
```

### Production Deployment

#### Option A: Docker Compose (Recommended)

```bash
# Clone both repositories
git clone https://github.com/Buildly-Labs/BabbleBeaver.git
git clone https://github.com/Buildly-Labs/bb-agent-manager.git

# Create environment file
cp bb-agent-manager/.env.example .env
# Edit .env with your API keys

# Deploy with Docker Compose
cd bb-agent-manager
docker-compose -f docker-compose.prod.yml up -d
```

**Services:**
- **BabbleBeaver**: `http://localhost:8000` - Main chat interface
- **BB Agent Manager**: `http://localhost:8001` - AI agent API
- **Ollama**: `http://localhost:11434` - Local AI models
- **Nginx** (optional): `http://localhost` - Unified proxy

#### Option B: Kubernetes Deployment

```yaml
# bb-agent-manager-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bb-agent-manager
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bb-agent-manager
  template:
    metadata:
      labels:
        app: bb-agent-manager
    spec:
      containers:
      - name: bb-agent-manager
        image: bb-agent-manager:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: gemini-api-key
        - name: LABS_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: buildly-secrets
              key: labs-api-token
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: bb-agent-manager-service
spec:
  selector:
    app: bb-agent-manager
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

#### Option C: Standalone Production

```bash
# Build production image
docker build -f Dockerfile.prod -t bb-agent-manager:prod .

# Run with production configuration
docker run -d \
  --name bb-agent-manager \
  -p 8001:8000 \
  -e GEMINI_API_KEY=your_key \
  -e LABS_API_TOKEN=your_token \
  -e GITHUB_TOKEN=your_token \
  --restart unless-stopped \
  bb-agent-manager:prod
```

### Connecting BabbleBeaver to Agent Microservice

#### Method 1: Direct HTTP Client

Add to BabbleBeaver's dependencies:
```python
# In BabbleBeaver's requirements.txt
httpx>=0.27.0
```

Modify BabbleBeaver to call agent service:
```python
# In BabbleBeaver's main.py or new agent_client.py
import httpx
import os

AGENT_SERVICE_URL = os.getenv("BB_AGENT_SERVICE_URL", "http://localhost:8001")

async def call_agent(messages: list, provider: str = "gemini"):
    """Call bb-agent-manager microservice"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AGENT_SERVICE_URL}/agent/chat",
            json={
                "provider": provider,
                "messages": messages
            },
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()

# Use in your chat endpoint
@app.post("/chatbot")
async def chatbot(request: Request):
    data = await request.json()
    user_message = data.get("prompt")
    
    messages = [
        {"role": "system", "content": "You are the Buildly Agent."},
        {"role": "user", "content": user_message}
    ]
    
    try:
        result = await call_agent(messages)
        return JSONResponse({"response": result.get("content", "")})
    except Exception as e:
        return JSONResponse({"response": f"Agent error: {e}"})
```

#### Method 2: Service Discovery (Advanced)

For production environments with service discovery:

```python
# Service discovery client
class AgentServiceClient:
    def __init__(self):
        self.service_url = self._discover_agent_service()
    
    def _discover_agent_service(self):
        # Consul, etcd, or Kubernetes service discovery
        return os.getenv("BB_AGENT_SERVICE_URL", "http://bb-agent-manager:8000")
    
    async def chat(self, messages, provider="gemini"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.service_url}/agent/chat",
                json={"provider": provider, "messages": messages}
            )
            return response.json()
```

### Monitoring & Operations

#### Health Checks
```bash
# Agent service health
curl http://localhost:8001/health

# Integration test
curl -X POST http://localhost:8001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

#### Logging
```bash
# Docker logs
docker logs bb-agent-manager

# Kubernetes logs
kubectl logs deployment/bb-agent-manager

# Log aggregation with ELK/EFK stack
# Configure log shipping to centralized logging
```

#### Metrics
```python
# Add to bb_agent_manager/main.py
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('bb_agent_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('bb_agent_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Security Considerations

#### API Security
```python
# Add authentication middleware
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # Verify JWT or API key
    if not validate_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

# Protect endpoints
@app.post("/agent/chat")
async def chat(req: ChatRequest, token=Depends(verify_token)):
    # ... implementation
```

#### Network Security
```yaml
# docker-compose.prod.yml with network isolation
networks:
  buildly-internal:
    driver: bridge
    internal: true  # No external access
  buildly-external:
    driver: bridge

services:
  bb-agent-manager:
    networks:
      - buildly-internal  # Only internal communication
  
  babblebeaver:
    networks:
      - buildly-internal
      - buildly-external  # Has external access
```

### Scaling & Performance

#### Horizontal Scaling
```bash
# Scale agent service replicas
docker-compose -f docker-compose.prod.yml up -d --scale bb-agent-manager=3

# With load balancer
# Nginx upstream will automatically load balance
```

#### Resource Optimization
```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

# HPA for auto-scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bb-agent-manager-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bb-agent-manager
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Comparison: Plugin vs Microservice

| Aspect | Plugin Mode | Microservice Mode |
|--------|-------------|-------------------|
| **Deployment** | Single process | Multiple containers |
| **Latency** | Lower (in-process) | Higher (network calls) |
| **Scaling** | Scale together | Independent scaling |
| **Isolation** | Shared resources | Complete isolation |
| **Complexity** | Simple | More complex |
| **Debugging** | Easier | Distributed tracing needed |
| **Resource Usage** | Lower | Higher overhead |
| **Fault Tolerance** | Single point of failure | Better fault isolation |
| **Development** | Tighter coupling | Loose coupling |

## Recommendations

- **Development/Small deployments**: Use Plugin Mode
- **Production/Cloud/Scale**: Use Microservice Mode
- **Hybrid**: Start with Plugin Mode, migrate to Microservice as you scale

Choose based on your specific requirements for scale, isolation, and operational complexity!
