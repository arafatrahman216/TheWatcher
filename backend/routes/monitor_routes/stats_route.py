import logging
from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.AuthDB import get_db, Website, UptimeCheck
from database.schemas import UptimeStatsResponse, UptimeCheckResponse
from services.uptime_service import uptime_service
from services.monitor_service_pkg.api_client import UptimeRobotAPI

logger = logging.getLogger(__name__)


def register(router):
    @router.get("/stats")
    async def get_uptime_stats_endpoint(db: Session = Depends(get_db)):
        return await get_uptime_stats(db)

    @router.get("/monitors")
    async def get_uptime_monitors_endpoint(db: Session = Depends(get_db)):
        monitors = UptimeRobotAPI()._get_all_monitors()
        print(monitors)
        return monitors

async def get_uptime_stats(db: Session) -> UptimeStatsResponse:
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
                total_available_checks = len(logs) + len(response_times)
                total_checks = total_available_checks if total_available_checks > 0 else 1
                
                # Calculate successful checks
                if uptime_percentage > 0 and total_checks > 0:
                    successful_checks = int((uptime_percentage / 100) * total_checks)
                else:
                    up_logs = [log for log in logs if log.get("type") == 2]  # Type 2 = Up
                    successful_checks = len(up_logs) + len(response_times)
                
                # Average response time
                avg_response = 0
                if response_times:
                    avg_response_str = monitor.get("average_response_time")
                    if avg_response_str:
                        try:
                            avg_response = float(avg_response_str)
                        except (ValueError, TypeError):
                            values = [float(rt.get("value", 0)) for rt in response_times if rt.get("value")]
                            avg_response = sum(values) / len(values) if values else 0
                    else:
                        values = [float(rt.get("value", 0)) for rt in response_times if rt.get("value")]
                        avg_response = sum(values) / len(values) if values else 0
                
                # Last check (prefer response_times)
                last_check = None
                if response_times:
                    try:
                        latest_rt = max(response_times, key=lambda x: x.get("datetime", 0))
                        rt_ts = int(latest_rt.get("datetime", 0))
                        if rt_ts > 0:
                            temp_datetime = datetime.utcfromtimestamp(rt_ts)
                            current_time = datetime.utcnow()
                            if abs((temp_datetime - current_time).days) <= 365:
                                last_check = temp_datetime
                            else:
                                logger.warning(f"Response time last_check too far from current time: {temp_datetime}")
                    except Exception as e:
                        logger.warning(f"Error parsing response_time timestamp: {e}")
                        last_check = None
                
                if not last_check and logs:
                    try:
                        most_recent_log = max(logs, key=lambda x: x.get("datetime", 0))
                        timestamp = int(most_recent_log.get("datetime", 0))
                        if timestamp > 0:
                            temp_datetime = datetime.utcfromtimestamp(timestamp)
                            current_time = datetime.utcnow()
                            if abs((temp_datetime - current_time).days) <= 365:
                                last_check = temp_datetime
                            else:
                                logger.warning(f"Log last_check too far from current time: {temp_datetime}")
                    except (ValueError, TypeError, OSError) as e:
                        logger.warning(f"Error parsing last check timestamp: {e}")
                        last_check = None
                
                # Incidents
                incidents = []
                down_logs = [log for log in logs if log.get("type") == 1]  # Type 1 = Down
                for log in down_logs[:10]:
                    try:
                        timestamp = int(log.get("datetime", 0))
                        if timestamp > 0:
                            log_datetime = datetime.utcfromtimestamp(timestamp)
                            current_time = datetime.utcnow()
                            if abs((log_datetime - current_time).days) > 365:
                                logger.warning(f"Incident datetime too far from current time: {log_datetime}")
                                continue
                                
                            reason = log.get("reason", {})
                            
                            incidents.append(UptimeCheckResponse(
                                id=int(log.get('id', log.get('datetime', 0))),
                                website_id=uptime_service.website_id,
                                timestamp=log_datetime,
                                status_code=None,
                                response_time=None,
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
            
            successful_response_times = [c.response_time for c in checks if c.is_up and c.response_time is not None]
            average_response_time = sum(successful_response_times) / len(successful_response_times) if successful_response_times else 0
            
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
            ][:10]
            
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
