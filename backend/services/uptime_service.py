# This file stays named uptime_service.py so existing imports work
# from services.uptime_service import uptime_service

from .monitor_service_pkg.ssl_check import SSL_Check
from .monitor_service_pkg.api_client import UptimeRobotAPI

uptime_service = SSL_Check()

__all__ = [ "SSL_Check", "UptimeRobotAPI"]
