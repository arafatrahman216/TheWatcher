# This file stays named uptime_service.py so existing imports work
# from services.uptime_service import uptime_service

from .uptime_service_pkg.service_impl import UptimeService
from .uptime_service_pkg.api_client import UptimeRobotAPI

uptime_service = UptimeService()

__all__ = ["uptime_service", "UptimeService", "UptimeRobotAPI"]
