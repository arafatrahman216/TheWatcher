import logging
from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, UptimeCheck
from schemas import UptimeCheckResponse
from services.uptime_service import uptime_service

logger = logging.getLogger(__name__)


def register(router):
    @router.get("/checks")
    async def get_uptime_checks(limit: int = 50, db: Session = Depends(get_db)):
        """Get recent uptime checks"""
        try:
            # Try to get recent checks from UptimeRobot API first
            try:
                monitor_data = uptime_service.uptimerobot_api._get_monitors()
                
                if monitor_data and "monitors" in monitor_data and monitor_data["monitors"]:
                    monitor = monitor_data["monitors"][0]
                    logs = monitor.get("logs", [])
                    
                    if logs:
                        uptimerobot_checks = []
                        sorted_logs = sorted(logs, key=lambda x: x.get("datetime", 0), reverse=True)
                        
                        response_times = monitor.get("response_times", [])
                        response_times_dict = {}
                        for rt in response_times:
                            rt_timestamp = rt.get("datetime")
                            if rt_timestamp:
                                response_times_dict[int(rt_timestamp)] = float(rt.get("value", 0))
                        
                        for log in sorted_logs:
                            try:
                                timestamp = int(log.get("datetime", 0))
                                if timestamp <= 0:
                                    logger.warning(f"Invalid log timestamp: {log.get('datetime')}")
                                    continue
                                    
                                log_datetime = datetime.utcfromtimestamp(timestamp)
                                current_time = datetime.utcnow()
                                if abs((log_datetime - current_time).days) > 365:
                                    logger.warning(f"Log datetime too far from current time: {log_datetime}")
                                    continue
                                    
                                log_timestamp = timestamp
                                log_type = log.get("type", 0)
                                is_up = log_type == 2
                                
                                reason = log.get("reason", {})
                                status_code = None
                                error_message = None
                                
                                if is_up:
                                    status_code = int(reason.get("code", 200)) if reason.get("code") else 200
                                else:
                                    error_message = reason.get("detail", "Monitor was down")
                                    if reason.get("code"):
                                        try:
                                            status_code = int(reason.get("code"))
                                        except (ValueError, TypeError):
                                            status_code = None
                                
                                response_time = None
                                if is_up:
                                    closest_response_time = None
                                    min_time_diff = float('inf')
                                    
                                    for rt_timestamp, rt_value in response_times_dict.items():
                                        time_diff = abs(rt_timestamp - log_timestamp)
                                        if time_diff < min_time_diff:
                                            min_time_diff = time_diff
                                            closest_response_time = rt_value
                                    
                                    if closest_response_time and min_time_diff <= 3600:
                                        response_time = closest_response_time
                                elif log_type == 98:
                                    response_time = None
                                
                                uptimerobot_checks.append(UptimeCheckResponse(
                                    id=int(log.get('id', log.get('datetime', 0))),
                                    website_id=uptime_service.website_id,
                                    is_up=is_up,
                                    response_time=response_time,
                                    status_code=status_code,
                                    error_message=error_message,
                                    timestamp=log_datetime
                                ))
                            except (ValueError, TypeError, OSError) as e:
                                logger.warning(f"Error parsing check timestamp: {e}")
                                continue

                        # Also add response_times as individual successful checks
                        for rt in response_times:
                            try:
                                rt_timestamp = int(rt.get("datetime", 0))
                                if rt_timestamp <= 0:
                                    logger.warning(f"Invalid response time timestamp: {rt.get('datetime')}")
                                    continue
                                    
                                rt_datetime = datetime.utcfromtimestamp(rt_timestamp)
                                current_time = datetime.utcnow()
                                if abs((rt_datetime - current_time).days) > 365:
                                    logger.warning(f"Response time datetime too far from current time: {rt_datetime}")
                                    continue
                                    
                                rt_value = float(rt.get("value", 0))
                                if rt_value < 0:
                                    logger.warning(f"Invalid response time value: {rt_value}")
                                    continue
                                
                                has_log_entry = any(
                                    abs(int(log.get("datetime", 0)) - rt_timestamp) <= 300 
                                    for log in sorted_logs
                                )
                                
                                if not has_log_entry:
                                    uptimerobot_checks.append(UptimeCheckResponse(
                                        id=rt_timestamp,
                                        website_id=uptime_service.website_id,
                                        is_up=True,
                                        response_time=rt_value,
                                        status_code=200,
                                        error_message=None,
                                        timestamp=rt_datetime
                                    ))
                            except (ValueError, TypeError, OSError) as e:
                                logger.warning(f"Error parsing response time entry: {e}")
                                continue
                        
                        uptimerobot_checks.sort(key=lambda x: x.timestamp, reverse=True)
                        uptimerobot_checks = uptimerobot_checks
                        
                        if uptimerobot_checks:
                            logger.info(f"Retrieved {len(uptimerobot_checks)} checks from UptimeRobot API")
                            return uptimerobot_checks
            
            except Exception as api_error:
                logger.warning(f"UptimeRobot API failed for checks, falling back to database: {api_error}")
            
            # Fallback to database checks
            checks = db.query(UptimeCheck)\
                .filter(UptimeCheck.website_id == uptime_service.website_id)\
                .order_by(UptimeCheck.timestamp.desc())\
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
