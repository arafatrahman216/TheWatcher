import logging
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.AuthDB import get_db, Website
from database.schemas import WebsiteResponse
from services.uptime_service import uptime_service

logger = logging.getLogger(__name__)


def register(router):
    @router.get("/api/v1/ssl-cert")
    async def get_ssl_cert():
        """Get SSL certificate info for monitored website"""
        cert_info = uptime_service.get_ssl_certificate_info()
        if cert_info.get("error"):
            raise HTTPException(status_code=502, detail=cert_info["error"])
        return cert_info