import asyncio
from services.monitor_service_pkg.stats_service import get_uptime_stats
from routes.monitor_routes.website_route import get_website_info


async def main():
    resp = await get_website_info("801275358")
    print(resp)

if __name__ == "__main__":
    asyncio.run(main())