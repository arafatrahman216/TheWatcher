import logging
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi import Depends, HTTPException, APIRouter, Request
from sqlalchemy.orm import Session

from database.AuthDB import get_db
from database.MonitorDB import MonitorCreate, _create_new_monitor, _delete_monitor, get_monitor_by_user, _edit_monitor as db_edit_monitor
from services.monitor_service_pkg.api_client import UptimeRobotAPI, filter_by_user_id

logger = logging.getLogger(__name__)

# Nested models for request bodies
class MonitorRequest(BaseModel):
    sitename: str
    site_url: str
    monitor_created: Optional[str] = None
    interval: int

class CreateMonitorRequest(BaseModel):
    user_id: int
    monitor: MonitorRequest

class DeleteRequest(BaseModel):
    user_id: int
    monitor_id: int

class EditMonitorRequest(BaseModel):
    monitor_id: int
    sitename: Optional[str] = None
    site_url: Optional[str] = None
    interval: Optional[int] = None

# Router
router = APIRouter(prefix="/monitors", tags=["monitors"])

@router.post("")
async def get_monitor_by_id(request: DeleteRequest, db: Session = Depends(get_db)):
    try:
        user_id = request.user_id
        all_monitors = UptimeRobotAPI()._get_all_monitors()
        user_monitors = get_monitor_by_user(user_id).get("data", [])
        filtered_monitors = filter_by_user_id(all_monitors, user_monitors)
        return {"monitors": filtered_monitors}
    except Exception as e:
        logger.error(f"Error fetching monitor by ID: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch monitor by ID")

@router.post("/create")
async def create_monitor(request: CreateMonitorRequest, db: Session = Depends(get_db)):
    """Create a new monitor"""
    try:
        monitor = {
            "monitorid": 0,
            "userid": request.user_id,
            "sitename": request.monitor.sitename,
            "site_url": request.monitor.site_url,
            "monitor_created": request.monitor.monitor_created or datetime.now().isoformat(),
            "interval": request.monitor.interval
        }

        data = UptimeRobotAPI()._create_new_monitor(user_id=request.user_id, monitor=monitor)
        monitor["monitorid"] = data.get("id", 0)

        result = {}
        if data.get("success"):
            result = _create_new_monitor(monitor)

        if result.get("success"):
            return {"message": "Monitor created successfully", "monitor_id": result.get("monitor_id")}
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to create monitor"))
    except Exception as e:
        logger.error(f"Error creating monitor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create monitor: {str(e)}")

@router.post("/delete")
async def delete_monitor(request: DeleteRequest, db: Session = Depends(get_db)):
    """Delete a monitor"""
    try:
        result = _delete_monitor(request.monitor_id)
        if result.get("success"):
            UptimeRobotAPI()._delete_monitor(request.monitor_id)
            return {"message": "Monitor deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Monitor not found")
    except Exception as e:
        logger.error(f"Error deleting monitor: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete monitor")


@router.patch("/edit")
async def edit_monitor(request: EditMonitorRequest, db: Session = Depends(get_db)):
    """
    Edit an existing monitor
    """
    try:
        if not request.monitor_id:
            raise HTTPException(status_code=400, detail="monitor_id is required")

        # Split updates
        api_update_data: Dict[str, any] = {}
        db_update_data: Dict[str, any] = {}

        if request.sitename is not None:
            api_update_data["friendlyName"] = request.sitename
            db_update_data["sitename"] = request.sitename

        if request.site_url is not None:
            api_update_data["url"] = request.site_url
            db_update_data["site_url"] = request.site_url

        if request.interval is not None:
            api_update_data["interval"] = request.interval
            # Do NOT add to db_update_data

        if not api_update_data:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        logger.info(f"Updating monitor {request.monitor_id} via API with: {api_update_data}")

        # Call UptimeRobot API
        api = UptimeRobotAPI()
        api_response = api.edit_monitor(request.monitor_id, api_update_data)

        if not api_response.get("success", False):
            message = api_response.get("message") or "Failed to update monitor via UptimeRobot"
            logger.error(f"UptimeRobot API error: {message}")
            raise HTTPException(status_code=400, detail=message)

        # Update database only if there are fields for DB
        if db_update_data:
            logger.info(f"Updating monitor {request.monitor_id} in DB with: {db_update_data}")
            db_response = db_edit_monitor(request.monitor_id, db_update_data)
            if not db_response.get("success", False):
                message = db_response.get("message") or "Failed to update monitor in local database"
                logger.error(f"DB update error: {message}")
                raise HTTPException(status_code=400, detail=message)

        return {"message": "Monitor updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error editing monitor {request.monitor_id}")
        raise HTTPException(status_code=500, detail=f"Failed to edit monitor: {repr(e)}")

# Function to register routes with main router
def register(main_router):
    main_router.include_router(router)
