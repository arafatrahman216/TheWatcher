from services.monitor_service_pkg.api_client import UptimeRobotAPI

monitor = {
    "sitename": "My Monitor",
    "site_url": "https://example.com",
    "monitor_created": "2024-10-01T12:00:00Z",
    "interval": 600
}


# resp = UptimeRobotAPI()._get_monitors(801275358)
# resp1= UptimeRobotAPI()._get_stats_activity(801275358)

resp1= UptimeRobotAPI()._get_monitors(801275358)
print(resp1)

# print(resp.get("monitors")[0].get("response_times"))
print("---------------------")
# print(resp1)