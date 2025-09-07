from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from routes.uptime import router as uptime_router
from routes.auth_routes.auth_routes import auth_router
from routes.monitor_routes.monitor_route import router as monitor_router
from scheduler import TaskScheduler  # 👈 single scheduler

# ----------------- Logging -----------------
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
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(uptime_router, prefix="/api/v1", tags=["uptime"])
app.include_router(monitor_router, prefix="/api/v1", tags=["monitors"])

# ----------------- Scheduler reference -----------------
task_scheduler: TaskScheduler | None = None

# ----------------- Startup & Shutdown -----------------
@app.on_event("startup")
async def startup_event():
    global task_scheduler
    logger.info("🚀 Starting Website Maintenance Agent")

    # Set your desired interval here (in minutes)
    INTERVAL_MINUTES = 50  # 👈 change this once, not in scheduler.py

    task_scheduler = TaskScheduler()
    task_scheduler.start(interval_minutes=INTERVAL_MINUTES)

    logger.info("✅ Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down Website Maintenance Agent")


# ----------------- Health & Root -----------------
@app.get("/")
async def root():
    return {"message": "Website Maintenance Agent is running", "version": "1.0.0", "status": "healthy"}


@app.get("/api/v1/health")
async def health_check():
    try:
        return {"status": "healthy", "message": "All systems operational using UptimeRobot API"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="System unhealthy")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
