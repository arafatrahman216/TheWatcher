import requests
import time
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, Website, UptimeCheck
from typing import Dict, Any, List, Optional
import logging

# Try to import dotenv, fall back to os.environ if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available, using environment variables directly")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UptimeRobotAPI:
    """UptimeRobot API client for monitoring website uptime"""
    
    def __init__(self):
        self.api_key = os.getenv("UPTIMEROBOT_API_KEY")
        self.base_url = "https://api.uptimerobot.com/v2"
        
        logger.info(f"Initializing UptimeRobot API. API Key available: {bool(self.api_key)}")
        if not self.api_key:
            logger.warning("UptimeRobot API key not found. Will use direct HTTP checks as fallback.")
    
    def get_monitor_data(self, monitor_id: Optional[str] = None) -> Dict[str, Any]:
        """Get monitor data from UptimeRobot API"""
        if not self.api_key:
            logger.info("No UptimeRobot API key, using direct HTTP check")
            return self._direct_http_check()
        
        try:
            logger.info("Attempting to fetch data from UptimeRobot API")
            # Get monitor data from UptimeRobot (directly gets our specific monitor)
            monitors_data = self._get_monitors()
            
            if not monitors_data:
                logger.error("Failed to get monitors data from UptimeRobot")
                return self._direct_http_check()
                
            if "monitors" not in monitors_data or not monitors_data["monitors"]:
                logger.error(f"No monitors found in UptimeRobot response: {monitors_data}")
                return self._direct_http_check()
            
            # Get the first (and only) monitor since we query a specific one
            monitor = monitors_data["monitors"][0]
            
            logger.info(f"Found monitor: {monitor.get('friendly_name', 'Unknown')} (ID: {monitor.get('id')})")
            
            return self._format_monitor_data(monitor)
            
        except Exception as e:
            logger.error(f"Error fetching from UptimeRobot API: {e}")
            logger.info("Falling back to direct HTTP check")
            return self._direct_http_check()
    
    def _get_monitors(self) -> Dict[str, Any]:
        """Get all monitors from UptimeRobot"""
        try:
            url = f"{self.base_url}/getMonitors"
            
            data = {
                "api_key": self.api_key,
                "format": "json",
                "monitors": "801132286",  # Specific monitor ID for FabricX AI
                "logs": "1",
                "response_times": "1",
                # "response_times_limit": "50", 
                "response_times_average": "0",
                "custom_uptime_ratios": "30-7-1"
            }
            
            logger.debug(f"Making request to {url}")
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"UptimeRobot response: {result}")
            
            if result.get("stat") == "ok":
                return result
            else:
                logger.error(f"UptimeRobot API error: {result}")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error when getting monitors: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error when getting monitors: {e}")
            return {}
    
    def _get_monitor_details(self, monitor_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific monitor"""
        # Since we're already getting detailed info in _get_monitors, just return the same data
        return self._get_monitors()
    
    def _find_monitor_by_url(self, monitors: List[Dict], target_url: str) -> Optional[Dict]:
        """Find monitor that matches the target URL"""
        # Since we're directly querying our specific monitor, just return the first one
        return monitors[0] if monitors else None
    
    def _format_monitor_data(self, monitor: Dict[str, Any]) -> Dict[str, Any]:
        """Format UptimeRobot monitor data to our standard format"""
        # Get the latest response time from response_times array
        response_times = monitor.get("response_times", [])
        latest_response_time = None
        
        if response_times:
            # Sort by datetime and get the most recent
            sorted_response_times = sorted(response_times, key=lambda x: x.get("datetime", 0), reverse=True)
            latest_response_time = float(sorted_response_times[0].get("value", 0))
        
        # Get status information from logs
        logs = monitor.get("logs", [])
        status_code = None
        error_message = None
        
        if logs:
            # Sort logs by datetime (most recent first)
            sorted_logs = sorted(logs, key=lambda x: x.get("datetime", 0), reverse=True)
            latest_log = sorted_logs[0]
            
            log_type = latest_log.get("type", 0)
            if log_type == 2:  # Up
                reason = latest_log.get("reason", {})
                status_code = int(reason.get("code", 200)) if reason.get("code") else 200
            elif log_type == 1:  # Down
                reason = latest_log.get("reason", {})
                error_message = reason.get("detail", "Monitor is down")
                status_code = int(reason.get("code")) if reason.get("code") and reason.get("code").isdigit() else None
        
        # Determine current status
        status = monitor.get("status", 0)
        is_up = status == 2  # 2 = Up in UptimeRobot
        
        # Parse custom uptime ratio (format: "30days-7days-1day")
        custom_uptime_ratio = monitor.get("custom_uptime_ratio", "0-0-0")
        uptime_ratios = custom_uptime_ratio.split("-")
        # Use 30-day uptime ratio
        uptime_ratio = float(uptime_ratios[0]) if uptime_ratios else 0
        
        return {
            "url": monitor.get("url", ""),
            "status_code": status_code,
            "response_time": latest_response_time,
            "is_up": is_up,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            "monitor_id": monitor.get("id"),
            "monitor_name": monitor.get("friendly_name", ""),
            "uptime_ratio": uptime_ratio
        }
    
    def _direct_http_check(self) -> Dict[str, Any]:
        """Fallback to direct HTTP check if UptimeRobot API is not available"""
        url = os.getenv("MONITORED_WEBSITE_URL", "https://www.fabricxai.com/")
        try:
            start_time = time.time()
            response = requests.get(url, timeout=30)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "url": url,
                "status_code": response.status_code,
                "response_time": response_time,
                "is_up": response.status_code == 200,
                "error_message": None if response.status_code == 200 else f"HTTP {response.status_code}",
                "timestamp": datetime.utcnow().isoformat()
            }
        except requests.exceptions.RequestException as e:
            return {
                "url": url,
                "status_code": None,
                "response_time": None,
                "is_up": False,
                "error_message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

class UptimeService:
    def __init__(self):
        self.uptimerobot_api = UptimeRobotAPI()
        self.website_url = os.getenv("MONITORED_WEBSITE_URL", "https://www.fabricxai.com/")
        self.website_name = os.getenv("MONITORED_WEBSITE_NAME", "FabricX AI")
        self.website_id = 1  # Fixed ID for the monitored website
        
        # Initialize the website in database
        self._ensure_website_exists()
        
    def _ensure_website_exists(self):
        """Ensure the monitored website exists in database"""
        db = SessionLocal()
        try:
            website = db.query(Website).filter(Website.id == self.website_id).first()
            if not website:
                website = Website(
                    id=self.website_id,
                    url=self.website_url,
                    name=self.website_name,
                    is_active=True
                )
                db.add(website)
                db.commit()
                logger.info(f"Created website entry for {self.website_url}")
            else:
                # Update URL and name if they changed
                website.url = self.website_url
                website.name = self.website_name
                website.is_active = True
                db.commit()
                logger.info(f"Updated website entry for {self.website_url}")
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error ensuring website exists: {e}")
        finally:
            db.close()
        
    async def check_uptime(self) -> Dict[str, Any]:
        """Check uptime using UptimeRobot API and return results"""
        logger.info(f"Checking uptime for website: {self.website_url}")
        
        # Use the UptimeRobot API to get monitor data
        result = self.uptimerobot_api.get_monitor_data()
        
        logger.info(f"Uptime check completed for {self.website_url}: {'UP' if result['is_up'] else 'DOWN'}")
        return result
    
    def save_check_result(self, db: Session, result: Dict[str, Any]):
        """Save uptime check result to database"""
        try:
            uptime_check = UptimeCheck(
                website_id=self.website_id,
                status_code=result["status_code"],
                response_time=result["response_time"],
                is_up=result["is_up"],
                error_message=result["error_message"]
            )
            db.add(uptime_check)
            db.commit()
            db.refresh(uptime_check)
            
            logger.info(f"Saved uptime check result to database")
            return uptime_check
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing uptime check: {e}")
            raise
    
    def check_website_uptime(self) -> Dict[str, Any]:
        """Check uptime for the monitored website and store results (legacy method)"""
        result = self.uptimerobot_api.get_monitor_data()
        
        # Store result in database
        db = SessionLocal()
        try:
            self.save_check_result(db, result)
            return result
        finally:
            db.close()
    
    def get_uptime_stats_from_api(self) -> Dict[str, Any]:
        """Get uptime statistics directly from UptimeRobot API"""
        try:
            logger.info("Getting uptime stats from UptimeRobot API")
            
            # Get monitor data from UptimeRobot
            if not self.uptimerobot_api.api_key:
                logger.info("No UptimeRobot API key, falling back to database stats")
                return self.get_uptime_stats()
            
            monitor_data = self.uptimerobot_api._get_monitors()
            
            if not monitor_data or "monitors" not in monitor_data or not monitor_data["monitors"]:
                logger.warning("No monitors found, falling back to database stats")
                return self.get_uptime_stats()
            
            # Get our specific monitor
            monitor = monitor_data["monitors"][0]
            
            # Extract statistics from the actual API response structure
            # Parse custom uptime ratio (format: "30days-7days-1day")
            custom_uptime_ratio = monitor.get("custom_uptime_ratio", "0-0-0")
            uptime_ratios = custom_uptime_ratio.split("-")
            uptime_percentage = float(uptime_ratios[0]) if uptime_ratios else 0  # 30-day ratio
            
            # Analyze logs for statistics
            logs = monitor.get("logs", [])
            
            # Calculate stats from logs
            total_checks = len(logs) if logs else 1
            up_logs = [log for log in logs if log.get("type") == 2]  # Type 2 = Up
            successful_checks = len(up_logs)
            failed_checks = total_checks - successful_checks
            
            # Calculate average response time from log durations (for "up" logs)
            avg_response = 0
            if up_logs:
                durations = []
                for log in up_logs:
                    duration = log.get("duration")
                    if duration and isinstance(duration, (int, float)):
                        durations.append(float(duration))
                
                if durations:
                    avg_response = sum(durations) / len(durations)
            
            logger.info(f"UptimeRobot stats: {total_checks} checks, {successful_checks} successful, {uptime_percentage}% uptime")
            
            return {
                "total_checks": max(total_checks, 1),  # Ensure at least 1
                "successful_checks": successful_checks,
                "failed_checks": failed_checks,
                "uptime_percentage": uptime_percentage,
                "average_response_time": avg_response
            }
            
        except Exception as e:
            logger.error(f"Error getting stats from UptimeRobot API: {e}")
            logger.info("Falling back to database stats")
            # Fallback to database stats
            return self.get_uptime_stats()
        
    def get_uptime_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get uptime statistics from database for the specified period"""
        db = SessionLocal()
        try:
            # Get checks from the last N days
            start_date = datetime.utcnow() - timedelta(days=days)
            
            checks = db.query(UptimeCheck).filter(
                UptimeCheck.website_id == self.website_id,
                UptimeCheck.timestamp >= start_date
            ).order_by(UptimeCheck.timestamp.desc()).all()
            
            if not checks:
                return {
                    "website_id": self.website_id,
                    "website_url": self.website_url,
                    "website_name": self.website_name,
                    "uptime_percentage": 0.0,
                    "total_checks": 0,
                    "successful_checks": 0,
                    "average_response_time": None,
                    "last_check": None,
                    "incidents": []
                }
            
            total_checks = len(checks)
            successful_checks = len([c for c in checks if c.is_up])
            uptime_percentage = (successful_checks / total_checks) * 100
            
            # Calculate average response time for successful checks
            successful_response_times = [c.response_time for c in checks if c.is_up and c.response_time]
            average_response_time = sum(successful_response_times) / len(successful_response_times) if successful_response_times else None
            
            # Get recent incidents (failed checks)
            incidents = [
                {
                    "timestamp": c.timestamp.isoformat(),
                    "status_code": c.status_code,
                    "error_message": c.error_message,
                    "response_time": c.response_time
                }
                for c in checks if not c.is_up
            ][:10]  # Last 10 incidents
            
            return {
                "website_id": self.website_id,
                "website_url": self.website_url,
                "website_name": self.website_name,
                "uptime_percentage": round(uptime_percentage, 2),
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "average_response_time": round(average_response_time, 2) if average_response_time else None,
                "last_check": checks[0].timestamp.isoformat() if checks else None,
                "incidents": incidents
            }
            
        except Exception as e:
            logger.error(f"Error getting uptime stats: {e}")
            raise
        finally:
            db.close()
    
    def get_recent_checks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent uptime checks for the monitored website"""
        db = SessionLocal()
        try:
            checks = db.query(UptimeCheck).filter(
                UptimeCheck.website_id == self.website_id
            ).order_by(UptimeCheck.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "id": check.id,
                    "timestamp": check.timestamp.isoformat(),
                    "status_code": check.status_code,
                    "response_time": check.response_time,
                    "is_up": check.is_up,
                    "error_message": check.error_message
                }
                for check in checks
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent checks: {e}")
            raise
        finally:
            db.close()
    
    def get_ssl_certificate_info(self, domain: str = None) -> Dict[str, Any]:
        """Fetch SSL certificate info from ssl-checker.io API"""
        if not domain:
            domain = self.website_url.replace('https://', '').replace('http://', '').strip('/')
        try:
            url = f"https://ssl-checker.io/api/v1/check/{domain}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            data = data.get("result")
            logger.info(f"SSL Checker API raw response: {data}")
            cert_info = {
                "valid_from": data.get("valid_from"),
                "valid_till": data.get("valid_till"),
                "days_left": data.get("days_left"),
                "cert_exp": data.get("cert_exp")
            }
            return cert_info
        except Exception as e:
            logger.error(f"Error fetching SSL certificate info: {e}")
            return {
                "valid_from": None,
                "valid_till": None,
                "days_left": None,
                "cert_exp": None,
                "error": str(e)
            }

# Initialize the service
uptime_service = UptimeService()