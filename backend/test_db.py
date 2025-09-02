import asyncio
from services.monitor_service_pkg.stats_service import get_uptime_stats

monitor = {
    "sitename": "My Monitor",
    "site_url": "https://example.com",
    "monitor_created": "2024-10-01T12:00:00Z",
    "interval": 600
}

async def main():
    resp = await get_uptime_stats(801275358)
    # resp1= UptimeRobotAPI()._get_stats_activity(801275358)

    # print(resp.get("monitors")[0].get("average_response_time"))
    print("---------------------")
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())