import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from sqlalchemy.orm import Session
from database.AuthDB import SessionLocal, Website, UptimeCheck

from .api_client import UptimeRobotAPI

logger = logging.getLogger(__name__)

class UptimeService:
    def __init__(self):
        self.uptimerobot_api = UptimeRobotAPI()
        self.website_url = os.getenv("MONITORED_WEBSITE_URL", "https://www.fabricxai.com/")
        self.website_name = os.getenv("MONITORED_WEBSITE_NAME", "FabricX AI")
        self.website_id = 1  # Fixed ID for the monitored website
        self._ensure_website_exists()
        
    def _ensure_website_exists(self):
        """Ensure the monitored website exists in database"""
        db = SessionLocal()
        try:
            website = db.query(Website).filter(Website.id == self.website_id).first()
            if not website:
                website = Website(
                    id=self.website_id,
                    url=self.website_url,
                    name=self.website_name,
                    is_active=True
                )
                db.add(website)
                db.commit()
                logger.info(f"Created website entry for {self.website_url}")
            else:
                website.url = self.website_url
                website.name = self.website_name
                website.is_active = True
                db.commit()
                logger.info(f"Updated website entry for {self.website_url}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error ensuring website exists: {e}")
        finally:
            db.close()
        
    async def check_uptime(self) -> Dict[str, Any]:
        """Check uptime using UptimeRobot API and return results"""
        logger.info(f"Checking uptime for website: {self.website_url}")
        result = self.uptimerobot_api.get_monitor_data()
        logger.info(f"Uptime check completed for {self.website_url}: {'UP' if result['is_up'] else 'DOWN'}")
        return result
    
    def save_check_result(self, db: Session, result: Dict[str, Any]):
        """Save uptime check result to database"""
        try:
            uptime_check = UptimeCheck(
                website_id=self.website_id,
                status_code=result["status_code"],
                response_time=result["response_time"],
                is_up=result["is_up"],
                error_message=result["error_message"]
            )
            db.add(uptime_check)
            db.commit()
            db.refresh(uptime_check)
            logger.info("Saved uptime check result to database")
            return uptime_check
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing uptime check: {e}")
            raise
    
    def check_website_uptime(self) -> Dict[str, Any]:
        """Check uptime for the monitored website and store results (legacy method)"""
        result = self.uptimerobot_api.get_monitor_data()
        db = SessionLocal()
        try:
            self.save_check_result(db, result)
            return result
        finally:
            db.close()
    
    def get_uptime_stats_from_api(self) -> Dict[str, Any]:
        """Get uptime statistics directly from UptimeRobot API"""
        try:
            logger.info("Getting uptime stats from UptimeRobot API")
            if not self.uptimerobot_api.api_key:
                logger.info("No UptimeRobot API key, falling back to database stats")
                return self.get_uptime_stats()
            
            monitor_data = self.uptimerobot_api._get_monitors()
            if not monitor_data or "monitors" not in monitor_data or not monitor_data["monitors"]:
                logger.warning("No monitors found, falling back to database stats")
                return self.get_uptime_stats()
            
            monitor = monitor_data["monitors"][0]
            custom_uptime_ratio = monitor.get("custom_uptime_ratio", "0-0-0")
            uptime_ratios = custom_uptime_ratio.split("-")
            uptime_percentage = float(uptime_ratios[0]) if uptime_ratios else 0
            
            logs = monitor.get("logs", [])
            total_checks = len(logs) if logs else 1
            up_logs = [log for log in logs if log.get("type") == 2]
            successful_checks = len(up_logs)
            failed_checks = total_checks - successful_checks
            
            avg_response = 0
            if up_logs:
                durations = []
                for log in up_logs:
                    duration = log.get("duration")
                    if duration and isinstance(duration, (int, float)):
                        durations.append(float(duration))
                if durations:
                    avg_response = sum(durations) / len(durations)
            
            logger.info(f"UptimeRobot stats: {total_checks} checks, {successful_checks} successful, {uptime_percentage}% uptime")
            return {
                "total_checks": max(total_checks, 1),
                "successful_checks": successful_checks,
                "failed_checks": failed_checks,
                "uptime_percentage": uptime_percentage,
                "average_response_time": avg_response
            }
        except Exception as e:
            logger.error(f"Error getting stats from UptimeRobot API: {e}")
            logger.info("Falling back to database stats")
            return self.get_uptime_stats()
        
    def get_uptime_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get uptime statistics from database for the specified period"""
        db = SessionLocal()
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            checks = db.query(UptimeCheck).filter(
                UptimeCheck.website_id == self.website_id,
                UptimeCheck.timestamp >= start_date
            ).order_by(UptimeCheck.timestamp.desc()).all()
            
            if not checks:
                return {
                    "website_id": self.website_id,
                    "website_url": self.website_url,
                    "website_name": self.website_name,
                    "uptime_percentage": 0.0,
                    "total_checks": 0,
                    "successful_checks": 0,
                    "average_response_time": None,
                    "last_check": None,
                    "incidents": []
                }
            
            total_checks = len(checks)
            successful_checks = len([c for c in checks if c.is_up])
            uptime_percentage = (successful_checks / total_checks) * 100
            
            successful_response_times = [c.response_time for c in checks if c.is_up and c.response_time]
            average_response_time = sum(successful_response_times) / len(successful_response_times) if successful_response_times else None
            
            incidents = [
                {
                    "timestamp": c.timestamp.isoformat(),
                    "status_code": c.status_code,
                    "error_message": c.error_message,
                    "response_time": c.response_time
                }
                for c in checks if not c.is_up
            ][:10]
            
            return {
                "website_id": self.website_id,
                "website_url": self.website_url,
                "website_name": self.website_name,
                "uptime_percentage": round(uptime_percentage, 2),
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "average_response_time": round(average_response_time, 2) if average_response_time else None,
                "last_check": checks[0].timestamp.isoformat() if checks else None,
                "incidents": incidents
            }
        except Exception as e:
            logger.error(f"Error getting uptime stats: {e}")
            raise
        finally:
            db.close()
    
    def get_recent_checks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent uptime checks for the monitored website"""
        db = SessionLocal()
        try:
            checks = db.query(UptimeCheck).filter(
                UptimeCheck.website_id == self.website_id
            ).order_by(UptimeCheck.timestamp.desc()).limit(limit).all()
            return [
                {
                    "id": check.id,
                    "timestamp": check.timestamp.isoformat(),
                    "status_code": check.status_code,
                    "response_time": check.response_time,
                    "is_up": check.is_up,
                    "error_message": check.error_message
                }
                for check in checks
            ]
        except Exception as e:
            logger.error(f"Error getting recent checks: {e}")
            raise
        finally:
            db.close()
    
    def get_ssl_certificate_info(self, domain: str = None):
        """Fetch SSL certificate info from ssl-checker.io API"""
        import requests  # local import to mirror original dependencies
        if not domain:
            domain = self.website_url.replace('https://', '').replace('http://', '').strip('/')
        try:
            url = f"https://ssl-checker.io/api/v1/check/{domain}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            data = data.get("result")
            logger.info(f"SSL Checker API raw response: {data}")
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
