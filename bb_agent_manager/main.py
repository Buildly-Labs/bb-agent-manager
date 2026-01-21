#!/usr/bin/env python3
"""
Production ASGI application for bb-agent-manager microservice
"""
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import secrets
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

# Add CORS and session middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32)))

# OAuth setup
oauth = OAuth()
labs_oauth = oauth.register(
    name='labs',
    client_id=os.getenv('LABS_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('LABS_OAUTH_CLIENT_SECRET'),
    access_token_url='https://labs.buildly.io/api/v1/oauth/token',
    authorize_url='https://labs.buildly.io/api/v1/oauth/authorize',
    api_base_url='https://labs.buildly.io/api/v1/',
    client_kwargs={'scope': 'openid profile email'},
)

# OAuth2 login endpoint
@app.get("/auth/login/labs")
async def login_labs(request: Request):
    redirect_uri = request.url_for('auth_labs_callback')
    return await labs_oauth.authorize_redirect(request, redirect_uri)

# OAuth2 callback endpoint
@app.get("/auth/callback/labs")
async def auth_labs_callback(request: Request):
    token = await labs_oauth.authorize_access_token(request)
    user = await labs_oauth.parse_id_token(request, token)
    # Store token in session
    request.session['labs_token'] = token['access_token']
    request.session['labs_user'] = user
    logger.info(f"Labs OAuth login: {user}")
    return RedirectResponse(url="/auth/success")

# Auth success endpoint
@app.get("/auth/success")
async def auth_success(request: Request):
    user = request.session.get('labs_user')
    return JSONResponse({"message": "Logged in via Labs OAuth", "user": user})

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
