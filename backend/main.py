from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes.uptime import router as uptime_router
from services.uptime_service import uptime_service
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Website Maintenance Agent",
    description="A comprehensive website monitoring and maintenance system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(uptime_router, prefix="/api/v1", tags=["uptime"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Website Maintenance Agent")
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Website Maintenance Agent")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Website Maintenance Agent is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/v1/health")
async def health_check():
    """Detailed health check"""
    try:
        return {
            "status": "healthy",
            "message": "All systems operational using UptimeRobot API"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="System unhealthy")

@app.get("/api/v1/ssl-cert")
async def get_ssl_cert():
    """Get SSL certificate info for monitored website"""
    cert_info = uptime_service.get_ssl_certificate_info()
    if cert_info.get("error"):
        raise HTTPException(status_code=502, detail=cert_info["error"])
    return cert_info

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
