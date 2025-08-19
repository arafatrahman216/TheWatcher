
from fastapi import APIRouter

router = APIRouter()

# Import sub-route registrars from uptime_routes folder
from .uptime_routes.discord_route import register as register_discord
from .uptime_routes.website_route import register as register_website
from .uptime_routes.stats_route import register as register_stats
from .uptime_routes.check_route import register as register_checks

# Attach endpoints to this router
register_discord(router)
register_website(router)
register_stats(router)
register_checks(router)

