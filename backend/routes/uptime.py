from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Website, UptimeCheck
from schemas import WebsiteResponse, UptimeStatsResponse, UptimeCheckResponse
from services.uptime_service import uptime_service
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/website")
async def get_monitored_website(db: Session = Depends(get_db)):
    """Get the monitored website information"""
    try:
        website = db.query(Website).filter(Website.id == uptime_service.website_id).first()
        if not website:
            raise HTTPException(status_code=404, detail="Monitored website not found")
        
        return WebsiteResponse(
            id=website.id,
            url=website.url,
            name=website.name,
            created_at=website.created_at,
            is_active=website.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitored website: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats")
async def get_uptime_stats(db: Session = Depends(get_db)):
    """Get uptime statistics for the monitored website"""
    try:
        # Try to get stats from UptimeRobot API first
        try:
            # Get fresh monitor data from UptimeRobot API
            monitor_data = uptime_service.uptimerobot_api._get_monitors()
            
            if monitor_data and "monitors" in monitor_data and monitor_data["monitors"]:
                monitor = monitor_data["monitors"][0]  # Our specific monitor
                
                # Get website info for the response
                website = db.query(Website).filter(Website.id == uptime_service.website_id).first()
                
                # Parse custom uptime ratio (format: "30days-7days-1day")
                custom_uptime_ratio = monitor.get("custom_uptime_ratio", "0-0-0")
                uptime_ratios = custom_uptime_ratio.split("-")
                uptime_percentage = float(uptime_ratios[0]) if uptime_ratios else 0  # 30-day ratio
                
                # Analyze logs for statistics and recent activity
                logs = monitor.get("logs", [])
                response_times = monitor.get("response_times", [])
                
                # Calculate total checks to match what /checks endpoint returns
                # Count both logs and response_times (excluding duplicates)
                total_available_checks = len(logs) + len(response_times)
                
                # Use the actual available data count for consistency
                total_checks = total_available_checks if total_available_checks > 0 else 1
                
                # Calculate successful checks from uptime percentage and total count
                if uptime_percentage > 0 and total_checks > 0:
                    successful_checks = int((uptime_percentage / 100) * total_checks)
                else:
                    # Fallback: count successful logs + response_times (response_times are always successful)
                    up_logs = [log for log in logs if log.get("type") == 2]  # Type 2 = Up
                    successful_checks = len(up_logs) + len(response_times)
                
                # Calculate average response time from actual response_times array
                avg_response = 0
                if response_times:
                    # Use the pre-calculated average if available
                    avg_response_str = monitor.get("average_response_time")
                    if avg_response_str:
                        try:
                            avg_response = float(avg_response_str)
                        except (ValueError, TypeError):
                            # Fallback to manual calculation
                            values = [float(rt.get("value", 0)) for rt in response_times if rt.get("value")]
                            avg_response = sum(values) / len(values) if values else 0
                    else:
                        # Manual calculation from response_times array
                        values = [float(rt.get("value", 0)) for rt in response_times if rt.get("value")]
                        avg_response = sum(values) / len(values) if values else 0
                # Note: Don't use log durations as response times - they represent state duration, not response time
                
                # Get last check time from most recent log or response_time
                last_check = None
                # Try response_times first (more recent data)
                if response_times:
                    try:
                        latest_rt = max(response_times, key=lambda x: x.get("datetime", 0))
                        rt_ts = int(latest_rt.get("datetime", 0))
                        if rt_ts > 0:
                            temp_datetime = datetime.utcfromtimestamp(rt_ts)
                            # Validate datetime is reasonable
                            current_time = datetime.utcnow()
                            if abs((temp_datetime - current_time).days) <= 365:
                                last_check = temp_datetime
                            else:
                                logger.warning(f"Response time last_check too far from current time: {temp_datetime}")
                    except Exception as e:
                        logger.warning(f"Error parsing response_time timestamp: {e}")
                        last_check = None
                
                # Fallback to logs if no valid response_time found
                if not last_check and logs:
                    try:
                        most_recent_log = max(logs, key=lambda x: x.get("datetime", 0))
                        timestamp = int(most_recent_log.get("datetime", 0))
                        if timestamp > 0:
                            temp_datetime = datetime.utcfromtimestamp(timestamp)
                            # Validate datetime is reasonable
                            current_time = datetime.utcnow()
                            if abs((temp_datetime - current_time).days) <= 365:
                                last_check = temp_datetime
                            else:
                                logger.warning(f"Log last_check too far from current time: {temp_datetime}")
                    except (ValueError, TypeError, OSError) as e:
                        logger.warning(f"Error parsing last check timestamp: {e}")
                        last_check = None
                
                # Get recent incidents (down events)
                incidents = []
                down_logs = [log for log in logs if log.get("type") == 1]  # Type 1 = Down
                for log in down_logs[:10]:  # Last 10 incidents
                    try:
                        timestamp = int(log.get("datetime", 0))
                        if timestamp > 0:
                            log_datetime = datetime.utcfromtimestamp(timestamp)
                            # Validate datetime is reasonable
                            current_time = datetime.utcnow()
                            if abs((log_datetime - current_time).days) > 365:
                                logger.warning(f"Incident datetime too far from current time: {log_datetime}")
                                continue
                                
                            reason = log.get("reason", {})
                            
                            incidents.append(UptimeCheckResponse(
                                id=int(log.get('id', log.get('datetime', 0))),  # Use actual UptimeRobot log ID
                                website_id=uptime_service.website_id,
                                timestamp=log_datetime,
                                status_code=None,  # Down logs don't have status codes
                                response_time=None,  # Down events don't have response times
                                is_up=False,
                                error_message=reason.get("detail", "Monitor was down")
                            ))
                    except (ValueError, TypeError, OSError) as e:
                        logger.warning(f"Error parsing incident timestamp: {e}")
                        continue
                
                logger.info(f"Retrieved UptimeRobot stats: {total_checks} checks, {successful_checks} successful, {uptime_percentage}% uptime")
                
                return UptimeStatsResponse(
                    website_id=uptime_service.website_id,
                    website_url=website.url if website else uptime_service.website_url,
                    website_name=website.name if website else uptime_service.website_name,
                    total_checks=max(total_checks, 1),
                    successful_checks=successful_checks,
                    uptime_percentage=round(uptime_percentage, 2),
                    average_response_time=round(avg_response, 2) if avg_response > 0 else None,
                    last_check=last_check,
                    incidents=incidents
                )
            
            else:
                raise Exception("No monitor data received from UptimeRobot API")
                
        except Exception as api_error:
            logger.warning(f"UptimeRobot API failed, falling back to database: {api_error}")
            
            # Fallback to database stats
            checks = db.query(UptimeCheck).filter(UptimeCheck.website_id == uptime_service.website_id).all()
            website = db.query(Website).filter(Website.id == uptime_service.website_id).first()
            
            if not checks:
                return UptimeStatsResponse(
                    website_id=uptime_service.website_id,
                    website_url=website.url if website else uptime_service.website_url,
                    website_name=website.name if website else uptime_service.website_name,
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
            successful_response_times = [c.response_time for c in checks if c.is_up and c.response_time is not None]
            average_response_time = sum(successful_response_times) / len(successful_response_times) if successful_response_times else 0
            
            # Get recent incidents
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
            ][:10]  # Last 10 incidents
            
            return UptimeStatsResponse(
                website_id=uptime_service.website_id,
                website_url=website.url if website else uptime_service.website_url,
                website_name=website.name if website else uptime_service.website_name,
                total_checks=total_checks,
                successful_checks=successful_checks,
                uptime_percentage=round(uptime_percentage, 2),
                average_response_time=round(average_response_time, 2),
                last_check=checks[0].timestamp if checks else None,
                incidents=incidents
            )
            
    except Exception as e:
        logger.error(f"Error getting uptime stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/checks")
async def get_uptime_checks(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent uptime checks"""
    try:
        # Try to get recent checks from UptimeRobot API first
        try:
            # Get monitor data from UptimeRobot (this gets our specific monitor with logs)
            monitor_data = uptime_service.uptimerobot_api._get_monitors()
            
            if monitor_data and "monitors" in monitor_data and monitor_data["monitors"]:
                monitor = monitor_data["monitors"][0]  # Our specific monitor
                logs = monitor.get("logs", [])
                
                if logs:
                    # Convert UptimeRobot logs to our format
                    uptimerobot_checks = []
                    
                    # Sort logs by datetime (most recent first) and limit
                    sorted_logs = sorted(logs, key=lambda x: x.get("datetime", 0), reverse=True)[:limit]
                    
                    # Get response_times for correlation
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
                            # Validate the datetime is reasonable (not too far in future/past)
                            current_time = datetime.utcnow()
                            if abs((log_datetime - current_time).days) > 365:
                                logger.warning(f"Log datetime too far from current time: {log_datetime}")
                                continue
                                
                            log_timestamp = timestamp
                            log_type = log.get("type", 0)
                            is_up = log_type == 2  # Type 2 = Up
                            
                            # Get reason details
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
                            
                            # Get response time based on log type and available data
                            response_time = None
                            if is_up:
                                # For "up" logs, try to find closest response time measurement
                                closest_response_time = None
                                min_time_diff = float('inf')
                                
                                for rt_timestamp, rt_value in response_times_dict.items():
                                    time_diff = abs(rt_timestamp - log_timestamp)
                                    if time_diff < min_time_diff:
                                        min_time_diff = time_diff
                                        closest_response_time = rt_value
                                
                                # Use closest response time if within reasonable range (1 hour)
                                if closest_response_time and min_time_diff <= 3600:
                                    response_time = closest_response_time
                                # Note: Don't use log duration as response time - it's state duration, not response time
                            elif log_type == 98:  # Monitor started
                                # For monitor start events, don't use duration as response time
                                # Duration here is likely startup time, not website response time
                                response_time = None
                            
                            uptimerobot_checks.append(UptimeCheckResponse(
                                id=int(log.get('id', log.get('datetime', 0))),  # Use actual UptimeRobot log ID
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
                    # These represent regular monitoring measurements
                    for rt in response_times:
                        try:
                            rt_timestamp = int(rt.get("datetime", 0))
                            if rt_timestamp <= 0:
                                logger.warning(f"Invalid response time timestamp: {rt.get('datetime')}")
                                continue
                                
                            rt_datetime = datetime.utcfromtimestamp(rt_timestamp)
                            # Validate the datetime is reasonable
                            current_time = datetime.utcnow()
                            if abs((rt_datetime - current_time).days) > 365:
                                logger.warning(f"Response time datetime too far from current time: {rt_datetime}")
                                continue
                                
                            rt_value = float(rt.get("value", 0))
                            if rt_value < 0:
                                logger.warning(f"Invalid response time value: {rt_value}")
                                continue
                            
                            # Check if we already have a log entry for this time period
                            has_log_entry = any(
                                abs(int(log.get("datetime", 0)) - rt_timestamp) <= 300 
                                for log in sorted_logs
                            )
                            
                            # Only add if we don't have a close log entry (avoid duplicates)
                            if not has_log_entry:
                                uptimerobot_checks.append(UptimeCheckResponse(
                                    id=rt_timestamp,  # Use timestamp as ID for response time entries
                                    website_id=uptime_service.website_id,
                                    is_up=True,  # Response times indicate successful checks
                                    response_time=rt_value,
                                    status_code=200,  # Assume 200 for successful response time measurements
                                    error_message=None,
                                    timestamp=rt_datetime
                                ))
                        except (ValueError, TypeError, OSError) as e:
                            logger.warning(f"Error parsing response time entry: {e}")
                            continue
                    
                    # Sort all checks by timestamp (most recent first) and limit
                    uptimerobot_checks.sort(key=lambda x: x.timestamp, reverse=True)
                    uptimerobot_checks = uptimerobot_checks[:limit]
                    
                    if uptimerobot_checks:
                        logger.info(f"Retrieved {len(uptimerobot_checks)} checks from UptimeRobot API")
                        return uptimerobot_checks
        
        except Exception as api_error:
            logger.warning(f"UptimeRobot API failed for checks, falling back to database: {api_error}")
        
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


