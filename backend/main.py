from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes.uptime import router as uptime_router
from routes.auth_routes.auth_routes import auth_router
from routes.monitor_routes.monitor_route import router as monitor_router
from services.uptime_service import uptime_service
import logging
import uvicorn

# 👇 Import your TaskScheduler
from scheduler import TaskScheduler  

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Website Maintenance Agent",
    description="A comprehensive website monitoring and maintenance system with authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  
        "http://localhost:3001",  
        "http://127.0.0.1:3000"   
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(uptime_router, prefix="/api/v1", tags=["uptime"])
app.include_router(monitor_router, prefix="/api/v1", tags=["monitors"])

# Keep a reference to scheduler
task_scheduler: TaskScheduler | None = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global task_scheduler
    logger.info("🚀 Starting Website Maintenance Agent")

    # Start scheduler
    task_scheduler = TaskScheduler()
    task_scheduler.start(interval_minutes=1)   # 👈 run every 1 min (change as needed)

    logger.info("✅ Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Website Maintenance Agent")


@app.get("/")
async def root():
    return {
        "message": "Website Maintenance Agent is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/api/v1/health")
async def health_check():
    try:
        return {
            "status": "healthy",
            "message": "All systems operational using UptimeRobot API"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="System unhealthy")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
