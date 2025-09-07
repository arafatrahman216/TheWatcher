# backend/scheduler.py
import atexit
import logging
from datetime import datetime
import time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from database.AuthDB import get_db_connection
from services.monitor_service_pkg.api_client import UptimeRobotAPI
from services.auth_mail_pkg.email_service import EmailService

# ----------------- Logging -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- Services -----------------
uptime_api = UptimeRobotAPI()
email_service = EmailService()


# ----------------- Email function -----------------
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
        # Use your existing send_mail method
        email_service.send_mail(recipient_email=to_email, subject=subject, text=body)
        logger.info(f"✅ Email sent to {to_email} for {site_name}")
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")


# ----------------- Scheduler task -----------------
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

        logger.info(f"[{datetime.now()}] Completed uptime check")
    except Exception as e:
        logger.error(f"Error during uptime check: {e}")
    finally:
        cursor.close()
        connection.close()


# ----------------- Task Scheduler Class -----------------
class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        atexit.register(lambda: self.scheduler.shutdown())

    def start(self, interval_minutes: int = 5):
        try:
            try:
                self.scheduler.remove_job("uptime_check")
            except:
                pass

            self.scheduler.add_job(
                func=check_down_monitors,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id="uptime_check",
                name="Check website uptime",
                replace_existing=True,
            )
            logger.info(f"✅ Scheduler started: checking every {interval_minutes} minutes")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")


# ----------------- Run directly (for local testing) -----------------
if __name__ == "__main__":
    task_scheduler = TaskScheduler()
    task_scheduler.start(interval_minutes=1)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped manually")
