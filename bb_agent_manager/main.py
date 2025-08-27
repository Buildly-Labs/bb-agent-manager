#!/usr/bin/env python3
"""
Production ASGI application for bb-agent-manager microservice
"""
from fastapi import FastAPI
from bb_agent_manager.plugin import register
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BB Agent Manager",
    description="AI-powered development assistant for Buildly Labs workflows",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for microservice communication
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "bb-agent-manager",
        "version": "0.1.0",
        "mode": "microservice"
    }

# Register the bb-agent-manager plugin
try:
    result = register(app, {})
    logger.info(f"Plugin registered successfully: {result}")
except Exception as e:
    logger.error(f"Failed to register plugin: {e}")
    raise

# Log startup information
@app.on_event("startup")
async def startup_event():
    logger.info("BB Agent Manager microservice starting up")
    logger.info(f"Mount path: {os.getenv('BB_AM_MOUNT_PATH', '/agent')}")
    logger.info(f"Default provider: {os.getenv('BB_AM_DEFAULT_PROVIDER', 'gemini')}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
