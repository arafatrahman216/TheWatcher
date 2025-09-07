import requests
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from database.schemas import UptimeCheckResponse

from sqlalchemy import false

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
    

    def _get_monitors(self, monitor_id: int) -> Dict[str, Any]:
        """Get all monitors from UptimeRobot"""
        try:
            url = f"{self.base_url}/getMonitors"
            data = {
                "api_key": self.api_key,
                "format": "json",
                "monitors": monitor_id,
                "logs": "1",
                "response_times": "1",
                # "response_times_limit": "1000",
                "response_times_average": "1",
                "custom_uptime_ratios": "30-7-1"
            }
            # logger.debug(f"Making request to {url}")
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            # logger.debug(f"UptimeRobot response: {result}")
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


# for report
    def get_all_monitor_stats(self) -> List[Dict[str, Any]]:
        """
        Get summarized info for all monitors:
        - Latest status
        - Average response time
        - Custom uptime ratios
        - Total number of logs and errors
        """
        try:
            url = f"{self.base_url}/getMonitors"
            data = {
                "api_key": self.api_key,
                "format": "json",
                "logs": "1",  # Include logs to count them
                "response_times": "0",  # skip detailed response times
                "response_times_average": "1",
                "custom_uptime_ratios": "30-7-1",
            }
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            if result.get("stat") != "ok":
                logger.error(f"UptimeRobot API error: {result}")
                return []

            summary_list = []
            for monitor in result.get("monitors", []):
                logs = monitor.get("logs", [])
                errors_count = sum(1 for log in logs if log.get("type") == 1)  # type 1 = error
                summary_list.append({
                    "id": monitor.get("id"),
                    "friendlyName": monitor.get("friendly_name"),
                    "url": monitor.get("url"),
                    "status": monitor.get("status"),
                    "interval": monitor.get("interval"),
                    "average_response_time": monitor.get("average_response_time"),
                    "custom_uptime_ratios": monitor.get("custom_uptime_ratios"),
                    "total_logs": len(logs),
                    "total_errors": errors_count,
                    "last_log": logs[-1] if logs else None,
                    "createDateTime": monitor.get("create_datetime"),
                })

            return summary_list

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error when fetching summarized monitor stats: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error when fetching summarized monitor stats: {e}")
            return []


    def _get_monitor_by_monitor_id(self, monitor_id: str) -> Dict[str, Any]:
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

    def _create_new_monitor(self, user_id: str, monitor: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Use UptimeRobot API v2 which is more stable
            url = f"{self.base_url}/newMonitor"

            siteurl = monitor["site_url"]
            sitename = monitor["sitename"]
            interval = monitor["interval"]

            # Use form data format for v2 API
            data = {
                "api_key": self.api_key,
                "format": "json",
                "type": "1",  # HTTP(s)
                "url": siteurl,
                "friendly_name": sitename,
                "interval": str(interval)
            }
            
            print(f"Creating monitor with data: {data}")
            response = requests.post(url, data=data)
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            print(f"API Response: {result}")
            
            if result.get("stat") == "ok":
                return {
                    "success": True,
                    "id": result.get("monitor", {}).get("id"),
                    "monitor_id": result.get("monitor", {}).get("id"),
                    "message": "Monitor created successfully"
                }
            else:
                return {
                    "success": False,
                    "message": result.get("error", {}).get("message", "Failed to create monitor")
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"\nError creating monitor {monitor}: {e}")
            # Return mock success for development
            return {
                "success": False,
                "id": 0,
                "monitor_id": 0,
                "message": "Monitor created failed"
            }


    def _delete_monitor(self, monitor_id: str):
        try :
            url = f"{self.updates_url}/monitors/{monitor_id}"
            response =  requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            # Check if response has content before parsing JSON
            if response.text.strip():
                data = response.json()
                print(data)
                return data
            else:
                # Empty response indicates successful deletion
                return {"success": True, "message": "Monitor deleted successfully"}

        except requests.exceptions.RequestException as e:
            logger.error(f"\nError deleting monitor {monitor_id}: {e}")
            return {}
        

        

def _process_uptimerobot_log(log: Dict[str, Any], response_times_dict: Dict[int, float]) -> Optional[UptimeCheckResponse]:
    """Process a single UptimeRobot log entry"""
    timestamp = log.get("datetime", 0)
    log_datetime = _validate_timestamp(timestamp)
    if not log_datetime:
        return None
    
    log_type = log.get("type", 0)
    is_up = log_type == 2
    reason = log.get("reason", {})
    
    # Determine status code and error message
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
    
    # Get response time for successful checks
    response_time = None
    if is_up:
        response_time = _find_closest_response_time(int(timestamp), response_times_dict)
    
    return UptimeCheckResponse(
        id=int(log.get('id', timestamp)),
        website_id=0,
        is_up=is_up,
        response_time=response_time,
        status_code=status_code,
        error_message=error_message,
        timestamp=log_datetime
    )



def _process_response_time_entry(rt: Dict[str, Any], existing_log_timestamps: set) -> Optional[UptimeCheckResponse]:
    """Process a response time entry that doesn't have a corresponding log"""
    timestamp = rt.get("datetime", 0)
    rt_datetime = _validate_timestamp(timestamp)
    if not rt_datetime:
        return None
    
    try:
        rt_value = float(rt.get("value", 0))
        if rt_value < 0:
            return None
    except (ValueError, TypeError):
        return None
    
    # Check if this response time already has a log entry (within 5 minutes)
    timestamp_int = int(timestamp)
    has_log_entry = any(
        abs(log_ts - timestamp_int) <= 300 
        for log_ts in existing_log_timestamps
    )
    
    if has_log_entry:
        return None
        
    return UptimeCheckResponse(
        id=timestamp_int,
        website_id=0,
        is_up=True,
        response_time=rt_value,
        status_code=200,
        error_message=None,
        timestamp=rt_datetime
    )


def _validate_timestamp(timestamp: Any) -> Optional[datetime]:
    """Validate and convert timestamp to datetime object"""
    try:
        timestamp_int = int(timestamp)
        if timestamp_int <= 0:
            return None
            
        dt = datetime.utcfromtimestamp(timestamp_int)
        current_time = datetime.utcnow()
        
        # Skip timestamps more than 1 year away
        if abs((dt - current_time).days) > 365:
            return None
            
        return dt
    except (ValueError, TypeError, OSError):
        return None


def _find_closest_response_time(target_timestamp: int, response_times_dict: Dict[int, float], max_diff: int = 3600) -> Optional[float]:
    """Find the closest response time within max_diff seconds"""
    closest_time = None
    min_diff = float('inf')
    
    for rt_timestamp, rt_value in response_times_dict.items():
        time_diff = abs(rt_timestamp - target_timestamp)
        if time_diff < min_diff and time_diff <= max_diff:
            min_diff = time_diff
            closest_time = rt_value
            
    return closest_time


def filter_by_user_id(Allmonitors: List[Dict[str, Any]], userMonitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter monitors by user ID"""
    # Create a set of monitor IDs that belong to the user
    # print(userMonitors)
    user_monitor_ids = {monitor.get('monitorid') for monitor in userMonitors}
    
    # Filter all monitors to only include those belonging to the user
    filtered_monitors = []
    for monitor in Allmonitors:
        print(monitor)
        if monitor.get('id') in user_monitor_ids:
            # Find corresponding user monitor data
            user_monitor = next((um for um in userMonitors if um.get('monitorid') == monitor.get('id')), None)
            
            # Merge data, prioritizing Allmonitors data but adding user-specific fields
            merged_monitor = monitor.copy()
            if user_monitor:
                merged_monitor['userid'] = user_monitor.get('userid')
                merged_monitor['monitor_created'] = user_monitor.get('monitor_created')
                # Keep the accurate sitename from Allmonitors as friendlyName
                # but add user's sitename as a separate field if different
                if user_monitor.get('sitename') != monitor.get('friendlyName'):
                    merged_monitor['user_sitename'] = user_monitor.get('sitename')
            
            filtered_monitors.append(merged_monitor)
    
    return filtered_monitors