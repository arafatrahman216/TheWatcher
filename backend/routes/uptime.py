
from fastapi import APIRouter

router = APIRouter()

# Import sub-route registrars from uptime_routes folder
from .uptime_routes.discord_route import register as register_discord
from .uptime_routes.website_route import register as register_website
from .uptime_routes.stats_route import register as register_stats
from .uptime_routes.check_route import register as register_checks
from .linkscan_routes.scan_route import register as register_linkscan
from .uptime_routes.performance_route import register as register_performance



# Attach endpoints to this router
register_discord(router)
register_website(router)
register_stats(router)
register_checks(router)
register_linkscan(router)
register_performance(router)   # ← add this line

