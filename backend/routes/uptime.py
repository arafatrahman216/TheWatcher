
from fastapi import APIRouter

router = APIRouter()

# Import sub-route registrars from monitor_routes folder
from .monitor_routes.discord_route import register as register_discord
from .monitor_routes.website_route import register as register_website
from .monitor_routes.stats_route import register as register_stats
from .linkscan_routes.scan_route import register as register_linkscan
from .monitor_routes.performance_route import register as register_performance
from .monitor_routes.monitor_route import register as register_monitor
from .monitor_routes.website_route import register as register_website
from .monitor_routes.report_route import register as register_report



# Attach endpoints to this router
register_discord(router)
register_website(router)
register_stats(router)
register_linkscan(router)
register_performance(router)   # ← add this line
register_monitor(router)
register_website(router)
register_report(router)

