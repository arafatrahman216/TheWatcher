import os
import requests
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

import pytz
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.AuthDB import get_db, Website, get_db_connection
from services.uptime_service import uptime_service
from .stats_route import get_uptime_stats  # reuse the stats function
from services.monitor_service_pkg.api_client import UptimeRobotAPI
from services.auth_mail_pkg.email_service import EmailService

uptime_api = UptimeRobotAPI()
email_service = EmailService()


logger = logging.getLogger(__name__)

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
MAIN_URL = os.getenv("MAIN_URL")


def register(router):
    @router.get("/discord")
    async def send_discord_report(monitorid: int, b: Session = Depends(get_db)):
        try:
            response = await sendDiscordAlert(monitorid=monitorid)
            response.raise_for_status()
            return {"status": "success", "detail": "Maintenance report sent to Discord."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send Discord report: {e}")


    @router.get("/alert")
    async def send_down_alert():
        bgscheduler = BackgroundScheduler()
        bgscheduler.start()
        try:
            bgscheduler.add_job(
                func=check_down_monitors,
                trigger="date",
                id="immediate_uptime_check",
                name="Immediate Uptime Check",
                replace_existing=True,
                next_run_time=datetime.now()
            )
            logger.info("✅ Immediate uptime check job scheduled")
        except Exception as e:
            logger.error(f"Failed to schedule immediate uptime check: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to schedule uptime check: {e}")
        return {"status": "success", "detail": "Uptime check scheduled successfully."}
def send_email(to_email, site_name, site_url):
    """Send email notification that site is down using EmailService."""
    subject = f"[ALERT] Your site {site_name} is down!"
    body = f"""
Hello,

We noticed that your monitored site {site_name} ({site_url}) is currently DOWN.
Please check your website immediately.

Regards,
The Watcher Team
"""
    try:
        email_service.send_mail(recipient_email=to_email, subject=subject, text=body)
        logger.info(f"✅ Email sent to {to_email} for {site_name}")
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")


def check_down_monitors():
    """Fetch monitors from API, check DB, and notify users if DOWN."""
    logger.info(f"[{datetime.now()}] Running uptime check...")
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        all_monitors = uptime_api._get_all_monitors()
        logger.info(f"Fetched {len(all_monitors)} monitors from UptimeRobot API")

        for monitor in all_monitors:
            monitor_id = monitor.get("id")
            status = monitor.get("status")
            site_url = monitor.get("url")
            site_name = monitor.get("friendlyName")

            if status.lower() == "down":
                cursor.execute("SELECT userid FROM monitors WHERE monitorid = %s", (monitor_id,))
                row = cursor.fetchone()
                if row:
                    user_id = row[0]
                    cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
                    user_row = cursor.fetchone()
                    if user_row:
                        email = user_row[0]
                        logger.info(f"🚨 {site_name} ({site_url}) is DOWN. Notifying {email}")
                        send_email(email, site_name, site_url)
                        requests.post(
                            DISCORD_WEBHOOK_URL,
                            json={"content": f"🚨 ALERT: {site_name} ({site_url}) is DOWN!"}
                        )

        logger.info(f"[{datetime.now()}] Completed uptime check")
    except Exception as e:
        logger.error(f"Error during uptime check: {e}")
    finally:
        cursor.close()
        connection.close()



async def sendDiscordAlert (monitorid) :
    if not DISCORD_WEBHOOK_URL:
        raise HTTPException(status_code=404, detail="DISCORD_WEBHOOK_URL not set in .env")
    try:
        stats = await get_uptime_stats(monitorid)
    except Exception:
        stats = None

    # SSL report
    ssl_status = "Unknown"
    ssl_expiry = "Unknown"
    ssl_days_remaining = "N/A"
    ssl_info = uptime_service.get_ssl_certificate_info(stats.get("url") if stats else MAIN_URL)
    print(ssl_info)
    if ssl_info:
        ssl_expiry = ssl_info.get('valid_till') or "Unknown"
        days_left = ssl_info.get('days_left')
        if days_left is not None:
            try:
                days_left_int = int(days_left)
                if days_left_int >= 0:
                    ssl_status = "Valid"
                    ssl_days_remaining = f"{days_left_int} days"
                else:
                    ssl_status = "Expired"
                    ssl_days_remaining = f"Expired {-days_left_int} days ago"
            except Exception:
                ssl_days_remaining = str(days_left)
        else:
            ssl_days_remaining = "N/A"
        if ssl_info.get('cert_exp') is True:
            ssl_status = "Expired"

    website_name = stats.get("name") if stats else "Unknown"
    website_url = stats.get("url") if stats else "Unknown"
    uptime_percentage = stats.get("uptime_percentage", 0)
    total_checks = stats.get("total_checks", 0)
    avg_response = stats.get("average_response_time", 0)

    # Local Dhaka time
    local_tz = pytz.timezone('Asia/Dhaka')
    utc_now = datetime.utcnow()
    local_time = utc_now.replace(tzinfo=pytz.utc).astimezone(local_tz)
    formatted_local_time = local_time.strftime('%Y-%m-%d %I:%M:%S %p GMT+6')

    message = f"""
:bar_chart: **Website Maintenance Report**
Website: {website_name}
URL: {website_url}
Uptime: {uptime_percentage}%
Total Checks: {total_checks}
Avg Response Time: {avg_response} ms
SSL Status: {ssl_status}
SSL Expiry: {ssl_expiry}
SSL Days Left: {ssl_days_remaining}
-----------------------------------
_Automated report generated by **TheWatcher** on {formatted_local_time}_
"""

    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    return response