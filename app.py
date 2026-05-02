"""
Main application entry point for Maximo Risk Assessment Generator.

This FastAPI application provides AI-powered JHA (Job Hazard Analysis) report
generation for IBM Maximo work orders.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config.settings import settings
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Maximo Risk Assessment Generator...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.app_debug}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Maximo Risk Assessment Generator...")


# Create FastAPI application
app = FastAPI(
    title="Maximo Risk Assessment Generator",
    description="AI-powered JHA (Job Hazard Analysis) report generation for IBM Maximo work orders",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.app_debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Include API routers
from routes import workorder_router, jha_router, health_router

app.include_router(health_router)
app.include_router(workorder_router)
app.include_router(jha_router)


@app.get("/")
async def root(request: Request):
    """Root endpoint - serves the main application page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Maximo Risk Assessment Generator"}
    )


if __name__ == "__main__":
    logger.info(f"Starting server on {settings.app_host}:{settings.app_port}")
    uvicorn.run(
        "app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level=settings.log_level.lower()
    )

# Made with Bob
