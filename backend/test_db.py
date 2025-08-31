from services.monitor_service_pkg.api_client import UptimeRobotAPI

monitor = {
    "sitename": "My Monitor",
    "site_url": "https://example.com",
    "monitor_created": "2024-10-01T12:00:00Z",
    "interval": 600
}


resp = UptimeRobotAPI()._delete_monitor(user_id=4, monitor_id=801273225)

print(resp)