import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from sqlalchemy.orm import Session
from database.AuthDB import SessionLocal, Website, UptimeCheck

from .api_client import UptimeRobotAPI

logger = logging.getLogger(__name__)

class SSL_Check:
    def __init__(self):
        self.uptimerobot_api = UptimeRobotAPI()
        self.website_url = os.getenv("MONITORED_WEBSITE_URL", "https://www.fabricxai.com/")
        
    def get_ssl_certificate_info(self, domain: str = None):
        """Fetch SSL certificate info from ssl-checker.io API"""
        import requests  # local import to mirror original dependencies
        if not domain:
            domain = self.website_url.replace('https://', '').replace('http://', '').strip('/')
        else :
            domain = domain.replace('https://', '').replace('http://', '').strip('/')
        try:
            url = f"https://ssl-checker.io/api/v1/check/{domain}"
            # print(url)
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            data = data.get("result")
            # logger.info(f"SSL Checker API raw response: {data}")
            cert_info = {
                "valid_from": data.get("valid_from"),
                "valid_till": data.get("valid_till"),
                "days_left": data.get("days_left"),
                "cert_exp": data.get("cert_exp")
            }
            return cert_info
        except Exception as e:
            logger.error(f"Error fetching SSL certificate info: {e}")
            return {
                "valid_from": None,
                "valid_till": None,
                "days_left": None,
                "cert_exp": None,
                "error": str(e)
            }
