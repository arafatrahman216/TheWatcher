import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.MonitorDB import _create_new_monitor, MonitorCreate
from database.AuthDB import get_db, UptimeCheck
from database.schemas import UptimeCheckResponse
from services.uptime_service import uptime_service
from services.monitor_service_pkg.api_client import _process_response_time_entry,_process_uptimerobot_log,_find_closest_response_time,_validate_timestamp

logger = logging.getLogger(__name__)





def _get_uptimerobot_checks() -> List[UptimeCheckResponse]:
    """eitake recent acitivity diya replace korbo"""
    monitor_data = uptime_service.uptimerobot_api._get_monitors(801132286)
    
    if not monitor_data or "monitors" not in monitor_data or not monitor_data["monitors"]:
        return []
    
    monitor = monitor_data["monitors"][0]
    logs = monitor.get("logs", [])
    response_times = monitor.get("response_times", [])

    print(logs)
    print("\n\n----------------------")
    print(response_times)

    if not logs:
        return []
    
    # Build response times dictionary for quick lookup
    response_times_dict = {}
    for rt in response_times:
        rt_timestamp = rt.get("datetime")
        if rt_timestamp:
            try:
                response_times_dict[int(rt_timestamp)] = float(rt.get("value", 0))
            except (ValueError, TypeError):
                continue
    
    # Process logs
    checks = []
    sorted_logs = sorted(logs, key=lambda x: x.get("datetime", 0), reverse=True)
    
    for log in sorted_logs:
        check = _process_uptimerobot_log(log, response_times_dict)
        if check:
            checks.append(check)
    

    # Get timestamps from processed logs
    log_timestamps = {int(log.get("datetime", 0)) for log in sorted_logs}
    
    # Process standalone response times
    for rt in response_times:
        check = _process_response_time_entry(rt, log_timestamps)
        if check:
            checks.append(check)
    
    # Sort by timestamp (newest first)
    checks.sort(key=lambda x: x.timestamp, reverse=True)
    print("-----------------------\n\n")
    print(checks)
    
    logger.info(f"Retrieved {len(checks)} checks from UptimeRobot API")
    return checks


def register(router):
    @router.get("/checks")
    async def get_uptime_checks(limit: int = 50, db: Session = Depends(get_db)):
        """Get recent uptime checks"""
        try:
            # Try UptimeRobot API first
            try:
                uptimerobot_checks = _get_uptimerobot_checks()
                if uptimerobot_checks:
                    return uptimerobot_checks[:limit]
            except Exception as api_error:
                logger.warning(f"UptimeRobot API failed, falling back to database: {api_error}")
            
            # Fallback to database checks
            checks = db.query(UptimeCheck)\
                .filter(UptimeCheck.website_id == uptime_service.website_id)\
                .order_by(UptimeCheck.timestamp.desc())\
                .limit(limit)\
                .all()
            
            return [UptimeCheckResponse(
                id=check.id,
                website_id=check.website_id,
                is_up=check.is_up,
                response_time=check.response_time,
                status_code=check.status_code,
                error_message=check.error_message,
                timestamp=check.timestamp
            ) for check in checks]
            
        except Exception as e:
            logger.error(f"Error getting uptime checks: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

  


    @router.get("/recent-activity")
    async def get_recent_activity(db: Session = Depends(get_db)):
        """Get recent activity combining logs and response times"""
        try:
            monitor_data = uptime_service.uptimerobot_api._get_stats_activity(801275358)
            return monitor_data

        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")