from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.uptime_service import uptime_service
from database import SessionLocal
import logging
import atexit
import asyncio

logger = logging.getLogger(__name__)

def sync_uptime_check():
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(uptime_service.check_uptime())
        
        db = SessionLocal()
        try:
            uptime_service.save_check_result(db, result)
            logger.info(f"Scheduled uptime check completed: {'UP' if result['is_up'] else 'DOWN'}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in scheduled uptime check: {e}")

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        atexit.register(lambda: self.scheduler.shutdown())
        
    def start_uptime_monitoring(self, interval_minutes: int = 5):
        try:
            try:
                self.scheduler.remove_job('uptime_check')
            except:
                pass                
            self.scheduler.add_job(
                func=sync_uptime_check,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id='uptime_check',
                name='Check website uptime via UptimeRobot API',
                replace_existing=True
            )

            logger.info(f"Uptime monitoring scheduled every {interval_minutes} minutes")
            
        except Exception as e:
            logger.error(f"Error starting uptime monitoring: {e}")
    
    def stop_uptime_monitoring(self):
        try:
            self.scheduler.remove_job('uptime_check')
            logger.info("Uptime monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping uptime monitoring: {e}")
    
    def get_job_status(self):
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]

# Initialize scheduler
task_scheduler = TaskScheduler()
