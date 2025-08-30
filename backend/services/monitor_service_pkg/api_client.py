import requests
import time
import os
from datetime import datetime
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
        self.updates_url = "https://api.uptimerobot.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

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
            monitors_data = self._get_monitors()
            
            if not monitors_data:
                logger.error("Failed to get monitors data from UptimeRobot")
                return self._direct_http_check()
                
            if "monitors" not in monitors_data or not monitors_data["monitors"]:
                logger.error(f"No monitors found in UptimeRobot response: {monitors_data}")
                return self._direct_http_check()
            
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
                # "monitors": "801132286",  # Specific monitor ID for FabricX AI
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
        return self._get_monitors()
    
    def _find_monitor_by_url(self, monitors: List[Dict], target_url: str) -> Optional[Dict]:
        """Find monitor that matches the target URL"""
        return monitors[0] if monitors else None
    
    def _format_monitor_data(self, monitor: Dict[str, Any]) -> Dict[str, Any]:
        """Format UptimeRobot monitor data to our standard format"""
        response_times = monitor.get("response_times", [])
        latest_response_time = None
        if response_times:
            sorted_response_times = sorted(response_times, key=lambda x: x.get("datetime", 0), reverse=True)
            latest_response_time = float(sorted_response_times[0].get("value", 0))
        
        logs = monitor.get("logs", [])
        status_code = None
        error_message = None
        if logs:
            sorted_logs = sorted(logs, key=lambda x: x.get("datetime", 0), reverse=True)
            latest_log = sorted_logs[0]
            log_type = latest_log.get("type", 0)
            if log_type == 2:  # Up
                reason = latest_log.get("reason", {})
                status_code = int(reason.get("code", 200)) if reason.get("code") else 200
            elif log_type == 1:  # Down
                reason = latest_log.get("reason", {})
                error_message = reason.get("detail", "Monitor is down")
                status_code = int(reason.get("code")) if reason.get("code") and str(reason.get("code")).isdigit() else None
        
        status = monitor.get("status", 0)
        is_up = status == 2  # 2 = Up in UptimeRobot
        
        custom_uptime_ratio = monitor.get("custom_uptime_ratio", "0-0-0")
        uptime_ratios = custom_uptime_ratio.split("-")
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
            response_time = (end_time - start_time) * 1000  # ms
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

    def _get_all_monitors(self) -> List[Dict[str, Any]]:
        """Get all monitors from UptimeRobot API"""
        try:
            url = f"{self.updates_url}/monitors"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            monitors_arr = data.get("data", [])
            # Select only specific fields from each monitor
            monitors = [
                {
                    "id": monitor.get("id"),
                    "interval": monitor.get("interval"),
                    "friendlyName": monitor.get("friendlyName"),
                    "url": monitor.get("url"),
                    "status": monitor.get("status"),
                    "createDateTime": monitor.get("createDateTime")
                }
                for monitor in monitors_arr
            ]
            return monitors
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching monitors: {e}")
            return []

    def _get_monitor_by_id(self, monitor_id: str) -> Dict[str, Any]:
        """Get a specific monitor by ID from UptimeRobot API"""
        try:
            url = f"{self.updates_url}/monitors/{monitor_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return {
                "id": data.get("id"),
                "friendlyName": data.get("friendlyName"),
                "url": data.get("url"),
                "status": data.get("status"),
                "createDateTime": data.get("createDateTime")
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching monitor {monitor_id}: {e}")
            return {}

