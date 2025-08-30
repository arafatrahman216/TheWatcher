import logging
from datetime import datetime
from typing import List
from pydantic import BaseModel

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from database.AuthDB import get_db
from database.MonitorDB import MonitorCreate, _create_new_monitor, _delete_monitor
from services.monitor_service_pkg.api_client import UptimeRobotAPI

logger = logging.getLogger(__name__)

# Create a nested model for the request body
class MonitorRequest(BaseModel):
    sitename: str
    site_url: str
    monitor_created: str
    interval: int

class CreateMonitorRequest(BaseModel):
    user_id: int
    monitor: MonitorRequest

# Create a router with prefix
router = APIRouter(prefix="/monitors", tags=["monitors"])

@router.post("/create")
async def create_monitor(request: CreateMonitorRequest, db: Session = Depends(get_db)):
    """Create a new monitor"""
    try:
        # Create MonitorCreate object with all required fields
        monitor = MonitorCreate(
            monitorid=0,  # This will be set from UptimeRobot API
            userid=request.user_id,
            sitename=request.monitor.sitename,
            site_url=request.monitor.site_url,
            monitor_created=request.monitor.monitor_created,
            interval=request.monitor.interval
        )

        data = UptimeRobotAPI()._create_new_monitor(user_id=request.user_id, monitor=monitor)
        monitor.monitorid = data.get("id", 0)  # Update with ID from UptimeRobot
        
        result = _create_new_monitor(monitor)
        success = result.get("success")
        print(success)
        if success:
            return {"message": "Monitor created successfully", "monitor_id": result.get("monitor_id")}
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to create monitor"))
            
    except Exception as e:
        logger.error(f"Error creating monitor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create monitor: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_monitors(user_id: int, db: Session = Depends(get_db)):
    """Get all monitors for a user"""
    try:
        # Add function to get user monitors from MonitorDB
        return {"monitors": []}
    except Exception as e:
        logger.error(f"Error fetching monitors: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch monitors")

@router.delete("/{monitor_id}")
async def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    """Delete a monitor"""
    try:
        result = _delete_monitor(monitor_id)
        if result:
            return {"message": "Monitor deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Monitor not found")
    except Exception as e:
        logger.error(f"Error deleting monitor: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete monitor")

@router.get("/hi")
async def get_monitor_info():
    """Test endpoint"""
    return {"message": "Monitor routes working!"}

# Function to register routes with main router
def register(main_router):
    main_router.include_router(router)
