
import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.AuthDB import  Website, UptimeCheck, get_db
from database.MonitorDB import get_monitor_info
from database.schemas import UptimeStatsResponse, UptimeCheckResponse
from services.uptime_service import uptime_service
from services.monitor_service_pkg.api_client import _process_response_time_entry,_process_uptimerobot_log,_find_closest_response_time,_validate_timestamp

logger = logging.getLogger(__name__)




# Constants for UptimeRobot log types
from fastapi import HTTPException


UPTIMEROBOT_LOG_DOWN = 1
UPTIMEROBOT_LOG_UP = 2
MAX_DAYS_THRESHOLD = 365
MAX_INCIDENTS = 10


async def get_uptime_stats(monitorid : int ,db: Session = Depends(get_db) ) -> UptimeStatsResponse:
    """Get uptime statistics for the monitored website"""
    try:
       
        try:
            monitor_data = uptime_service.uptimerobot_api._get_monitors(monitorid)
            # print(monitor_data)
            monitor_data= monitor_data.get("monitors", [])[0]       
            uptime_ratio = monitor_data.get("custom_uptime_ratio", "0-0-0")
            uptime_ratio = float(uptime_ratio.split("-")[0]) 
            response_times = monitor_data.get("response_times", [])
            logs = monitor_data.get("logs", [])
            checks = makeCheck(logs, response_times)

            if monitor_data :
                data = {
                    "uptime_percentage" : uptime_ratio,
                    "total_checks" : monitor_data.get("responsetime_length") if monitor_data.get("responsetime_length") else 0,
                    "average_response_time" : monitor_data.get("average_response_time") if monitor_data.get("average_response_time") else 0,
                    "checks" : checks,
                    "name" : monitor_data.get("friendly_name") if monitor_data.get("friendly_name") else "Unknown",
                    "url" : monitor_data.get("url") if monitor_data.get("url") else "Unknown"

                }
                return data
            else:
                raise Exception("No monitor data received from UptimeRobot API")
                
        except Exception as api_error:
            logger.warning(f"UptimeRobot API failed, Return None***: {api_error}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting uptime stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



def makeCheck(logs: list , response_times: list ) :
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
    return checks
