import logging
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.AuthDB import get_db, Website
from database.schemas import WebsiteResponse
from database.MonitorDB import get_monitor_info
from services.uptime_service import uptime_service

logger = logging.getLogger(__name__)


def register(router):
    @router.get("/ssl-cert")
    async def get_ssl_cert():
        """Get SSL certificate info for monitored website"""
        cert_info = uptime_service.get_ssl_certificate_info()
        if cert_info.get("error"):
            raise HTTPException(status_code=502, detail=cert_info["error"])
        return cert_info
    

    @router.get("/website")
    async def get_website_info(monitorid: str):
        """Get website info for monitored website"""
        website_info = get_monitor_info(monitorid).get("data")
        print(website_info)
        website_info = {
            "id": website_info.get("monitorid", ""),
            "url": website_info.get("site_url",  ""),
            "name": website_info.get("sitename", ""),
            "monitor_created": website_info.get("monitor_created", ""),
        }
        if website_info.get("error"):
            raise HTTPException(status_code=502, detail=website_info["message"])
        return website_info
