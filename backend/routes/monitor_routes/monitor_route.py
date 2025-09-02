import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi import Depends, HTTPException, APIRouter, Request
from sqlalchemy.orm import Session

from database.AuthDB import get_db
from database.MonitorDB import MonitorCreate, _create_new_monitor, _delete_monitor, get_monitor_by_user
from services.monitor_service_pkg.api_client import UptimeRobotAPI, filter_by_user_id

logger = logging.getLogger(__name__)

# Create a nested model for the request body
class MonitorRequest(BaseModel):
    sitename: str
    site_url: str
    monitor_created: Optional[str] = None
    interval: int

class CreateMonitorRequest(BaseModel):
    user_id: int
    monitor: MonitorRequest

class DeleteRequest(BaseModel):
    user_id : int
    monitor_id : int


# Create a router with prefix
router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.post("")
async def get_monitor_by_id(request : DeleteRequest, db: Session = Depends(get_db)):
    try :
        user_id = request.user_id
        # print(user_id)
        all_monitors = UptimeRobotAPI()._get_all_monitors()
        # print(all_monitors)
        user_monitors = get_monitor_by_user(user_id).get("data", [])
        filtered_monitors = filter_by_user_id(all_monitors, user_monitors)
        # print(user_monitors.get("data", []))
        print(filtered_monitors)


        return {
            "monitors": filtered_monitors
        }
    except Exception as e:
        logger.error(f"Error fetching monitor by ID: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch monitor by ID")


@router.post("/debug")
async def debug_request(request: Request):
    """Debug endpoint to see raw request data"""
    body = await request.body()
    try:
        import json
        json_data = json.loads(body)
        logger.info(f"Raw request body: {json_data}")
        return {"received": json_data}
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {"error": str(e), "raw_body": body.decode()}

@router.post("/create")
async def create_monitor(request: CreateMonitorRequest, db: Session = Depends(get_db)):
    """Create a new monitor"""
    try:
        # Create MonitorCreate object with all required fields
        monitor = {
            "monitorid": 0,  # This will be set from UptimeRobot API
            "userid": request.user_id,
            "sitename": request.monitor.sitename,
            "site_url": request.monitor.site_url,
            "monitor_created": request.monitor.monitor_created or datetime.now().isoformat(),
            "interval": request.monitor.interval
        }

        success= False
        data = UptimeRobotAPI()._create_new_monitor(user_id=request.user_id, monitor=monitor)
        monitor["monitorid"] = data.get("id", 0)  # Update with ID from UptimeRobot
        result={}
        if data.get("success"):
            success = True
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

@router.post("/delete")
async def delete_monitor(request : DeleteRequest, db: Session = Depends(get_db)):
    """Delete a monitor"""
    try:
        
        result = _delete_monitor(request.monitor_id)
        if result.get("success"):
            result= UptimeRobotAPI()._delete_monitor(request.monitor_id)
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
