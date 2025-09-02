
import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.AuthDB import  Website, UptimeCheck, get_db
from database.MonitorDB import get_monitor_info
from database.schemas import UptimeStatsResponse, UptimeCheckResponse
from services.uptime_service import uptime_service

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
            checks = monitor_data.get("response_times", [])
            if monitor_data :
                data = {
                    "uptime_percentage" : uptime_ratio,
                    "total_checks" : monitor_data.get("responsetime_length") if monitor_data.get("responsetime_length") else 0,
                    "average_response_time" : monitor_data.get("average_response_time") if monitor_data.get("average_response_time") else 0,
                }
                return data
            else:
                raise Exception("No monitor data received from UptimeRobot API")
                
        except Exception as api_error:
            logger.warning(f"UptimeRobot API failed, falling back to database: {api_error}")
            
            # Fallback to database
            checks = db.query(UptimeCheck)\
                .filter(UptimeCheck.website_id == uptime_service.website_id)\
                .all()
            
            return _build_stats_from_database(checks, website)
            
    except Exception as e:
        logger.error(f"Error getting uptime stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")




def _parse_timestamp(timestamp_value) -> Optional[datetime]:
    """Parse and validate timestamp with proper bounds checking"""
    try:
        timestamp_int = int(timestamp_value)
        if timestamp_int <= 0:
            return None
            
        parsed_datetime = datetime.utcfromtimestamp(timestamp_int)
        current_time = datetime.utcnow()
        
        # Skip timestamps more than 1 year away
        if abs((parsed_datetime - current_time).days) > MAX_DAYS_THRESHOLD:
            logger.warning(f"Timestamp too far from current time: {parsed_datetime}")
            return None
            
        return parsed_datetime
    except (ValueError, TypeError, OSError) as e:
        logger.warning(f"Error parsing timestamp {timestamp_value}: {e}")
        return None


def _calculate_average_response_time(monitor: dict, response_times: list) -> float:
    """Calculate average response time from monitor data or response times list"""
    # Try to get pre-calculated average from monitor
    avg_response_str = monitor.get("average_response_time")
    if avg_response_str:
        try:
            return float(avg_response_str)
        except (ValueError, TypeError):
            pass
    
    # Calculate from response times list
    if not response_times:
        return 0.0
        
    values = []
    for rt in response_times:
        try:
            value = float(rt.get("value", 0))
            if value > 0:
                values.append(value)
        except (ValueError, TypeError):
            continue
            
    return sum(values) / len(values) if values else 0.0


def _find_latest_check_time(response_times: list, logs: list) -> Optional[datetime]:
    """Find the most recent check time from response times or logs"""
    latest_time = None
    
    # Prefer response times (more frequent)
    if response_times:
        try:
            latest_rt = max(response_times, key=lambda x: x.get("datetime", 0))
            latest_time = _parse_timestamp(latest_rt.get("datetime", 0))
        except (ValueError, TypeError):
            pass
    
    # Fallback to logs if no valid response time
    if not latest_time and logs:
        try:
            most_recent_log = max(logs, key=lambda x: x.get("datetime", 0))
            latest_time = _parse_timestamp(most_recent_log.get("datetime", 0))
        except (ValueError, TypeError):
            pass
    
    return latest_time


def _create_incidents_from_logs(logs: list) -> list:
    """Create incident list from down logs"""
    incidents = []
    down_logs = [log for log in logs if log.get("type") == UPTIMEROBOT_LOG_DOWN]
    
    for log in down_logs[:MAX_INCIDENTS]:
        log_datetime = _parse_timestamp(log.get("datetime", 0))
        if not log_datetime:
            continue
            
        reason = log.get("reason", {})
        incident = UptimeCheckResponse(
            id=int(log.get('id', log.get('datetime', 0))),
            website_id=uptime_service.website_id,
            timestamp=log_datetime,
            status_code=None,
            response_time=None,
            is_up=False,
            error_message=reason.get("detail", "Monitor was down")
        )
        incidents.append(incident)
    
    return incidents


def _build_stats_from_uptimerobot(monitor: dict, website: Website) -> UptimeStatsResponse:
    """Build stats response from UptimeRobot monitor data"""
    # Parse uptime percentage
    custom_uptime_ratio = monitor.get("custom_uptime_ratio", "0-0-0")
    uptime_ratios = custom_uptime_ratio.split("-")
    uptime_percentage = float(uptime_ratios[0]) if uptime_ratios else 0.0
    
    # Get logs and response times
    logs = monitor.get("logs", [])
    response_times = monitor.get("response_times", [])
    
    # Calculate totals
    total_checks = max(len(logs) + len(response_times), 1)
    
    # Calculate successful checks
    if uptime_percentage > 0:
        successful_checks = int((uptime_percentage / 100) * total_checks)
    else:
        up_logs = [log for log in logs if log.get("type") == UPTIMEROBOT_LOG_UP]
        successful_checks = len(up_logs) + len(response_times)
    
    # Calculate metrics
    average_response_time = _calculate_average_response_time(monitor, response_times)
    last_check = _find_latest_check_time(response_times, logs)
    incidents = _create_incidents_from_logs(logs)
    
    logger.info(f"UptimeRobot stats: {total_checks} checks, {successful_checks} successful, {uptime_percentage}% uptime")
    
    return UptimeStatsResponse(
        total_checks=total_checks,
        successful_checks=successful_checks,
        uptime_percentage=round(uptime_percentage, 2),
        average_response_time=round(average_response_time, 2) if average_response_time > 0 else None,
        last_check=last_check,
        incidents=incidents
    )


def _build_stats_from_database(checks: list, website: Website) -> UptimeStatsResponse:
    """Build stats response from database checks"""
    if not checks:
        return UptimeStatsResponse(
            total_checks=0,
            successful_checks=0,
            uptime_percentage=0.0,
            average_response_time=0.0,
            last_check=None,
            incidents=[]
        )
    
    total_checks = len(checks)
    successful_checks = len([c for c in checks if c.is_up])
    uptime_percentage = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
    
    # Calculate average response time for successful checks
    successful_response_times = [
        c.response_time for c in checks 
        if c.is_up and c.response_time is not None
    ]
    average_response_time = (
        sum(successful_response_times) / len(successful_response_times) 
        if successful_response_times else 0
    )
    
    # Get incidents (failed checks)
    incidents = [
        UptimeCheckResponse(
            id=check.id,
            website_id=check.website_id,
            timestamp=check.timestamp,
            status_code=check.status_code,
            response_time=check.response_time,
            is_up=check.is_up,
            error_message=check.error_message
        )
        for check in checks if not check.is_up
    ][:MAX_INCIDENTS]
    
    return UptimeStatsResponse(
        total_checks=total_checks,
        successful_checks=successful_checks,
        uptime_percentage=round(uptime_percentage, 2),
        average_response_time=round(average_response_time, 2),
        last_check=checks[0].timestamp if checks else None,
        incidents=incidents
    )

