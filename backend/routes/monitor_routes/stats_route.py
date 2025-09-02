import logging

from fastapi import Depends
from sqlalchemy.orm import Session

from database.AuthDB import get_db
from services.uptime_service import uptime_service
from services.monitor_service_pkg.api_client import UptimeRobotAPI
from services.monitor_service_pkg.stats_service import get_uptime_stats
logger = logging.getLogger(__name__)


def register(router):
    @router.get("/stats")
    async def get_uptime_stats_endpoint( monitorid : str,db: Session = Depends(get_db)):
        print(monitorid)
        return await get_uptime_stats(monitorid=monitorid)
    

    @router.get("/monitors")
    async def get_uptime_monitors_endpoint(db: Session = Depends(get_db)):
        monitors = UptimeRobotAPI()._get_all_monitors()
        print(monitors)
        return monitors
