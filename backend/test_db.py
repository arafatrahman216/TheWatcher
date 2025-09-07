import asyncio
from services.monitor_service_pkg.stats_service import get_uptime_stats
from services.monitor_service_pkg.api_client import UptimeRobotAPI


a = UptimeRobotAPI()._get_monitors(801275358)
print(a)


# async def main():
#     resp = await get_uptime_stats("801275358")
#     print(resp)

# if __name__ == "__main__":
#     asyncio.run(main())