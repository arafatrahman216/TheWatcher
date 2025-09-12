import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
import logging
from typing import List, Dict, Optional, Any
from collections import defaultdict
from jinja2 import Template

from database.AuthDB import get_db_connection
from services.monitor_service_pkg.api_client import UptimeRobotAPI
from services.monitor_service_pkg.performance_service import fetch_lighthouse_score
from services.monitor_service_pkg.ssl_check import SSL_Check
from services.linkscan_pkg.scanner import LinkScannerService
from services.auth_mail_pkg.email_service import EmailService

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import BackgroundTasks

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report", tags=["report"])

uptime_api = UptimeRobotAPI()
email_service = EmailService()
scanner = LinkScannerService()
ssl_checker = SSL_Check()


def build_html_report(user_email: str, reports: List[Dict[str, Any]]) -> str:
    """Generate a pretty HTML report for a user using Jinja2 Template."""
    template = Template("""
    <html>
    <head>
      <style>
        body { font-family: Arial, sans-serif; }
        h2 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .error { color: red; }
      </style>
    </head>
    <body>
      <h2>Website Monitoring Report for {{ user_email }}</h2>
      {% for r in reports %}
        <h3>{{ r.friendly_name }} ({{ r.url }})</h3>

        <h4>Uptime Status</h4>
        <ul>
          <li>Status: {{ r.get('status', 'N/A') }}</li>
          <li>Average Response Time: {{ r.get('average_response_time', 'N/A') }} ms</li>
          <li>Custom Uptime Ratios: {{ r.get('custom_uptime_ratios', 'N/A') }}</li>
          <li>Total Logs: {{ r.get('total_logs', 0) }}</li>
          <li>Total Errors: {{ r.get('total_errors', 0) }}</li>
        </ul>

        <h4>SSL Certificate</h4>
        {% if r.ssl.get('error') %}
          <p class="error">Error: {{ r.ssl['error'] }}</p>
        {% else %}
          <ul>
            <li>Valid From: {{ r.ssl.get('valid_from', 'N/A') }}</li>
            <li>Valid Till: {{ r.ssl.get('valid_till', 'N/A') }}</li>
            <li>Days Left: {{ r.ssl.get('days_left', 'N/A') }}</li>
            <li>Certificate Expired: {{ r.ssl.get('cert_exp', 'N/A') }}</li>
          </ul>
        {% endif %}

        <h4>Performance (Lighthouse)</h4>
        {% if r.lighthouse.get('error') %}
          <p class="error">Error: {{ r.lighthouse['error'] }}</p>
        {% else %}
          <p>Performance Score: <b>{{ r.lighthouse.get('performance_score', 'N/A') }}%</b></p>
          <ul>
            <li>FCP: {{ r.lighthouse.get('metrics', {}).get('FCP', 'N/A') }} ms</li>
            <li>LCP: {{ r.lighthouse.get('metrics', {}).get('LCP', 'N/A') }} ms</li>
            <li>TBT: {{ r.lighthouse.get('metrics', {}).get('TBT', 'N/A') }} ms</li>
            <li>CLS: {{ r.lighthouse.get('metrics', {}).get('CLS', 'N/A') }}</li>
          </ul>
        {% endif %}

        <h4>Link Scanner</h4>
        {% if r.link_scan.get('error') %}
          <p class="error">Error: {{ r.link_scan['error'] }}</p>
        {% else %}
          <p>Checked {{ r.link_scan.get('total_links_checked', 0) }} links, 
             Broken: {{ r.link_scan.get('broken_count', 0) }}, 
             OK: {{ r.link_scan.get('ok_count', 0) }}</p>
        {% endif %}
        <hr/>
      {% endfor %}
    </body>
    </html>
    """)
    return template.render(user_email=user_email, reports=reports)


@router.get("/")
async def get_full_report(
    urls: Optional[List[str]] = Query(None, description="Specific URLs to scan"),
    max_pages: int = Query(10, description="Max pages for link scanner BFS crawl")
):
    try:
        # Fetch all monitors with uptime stats
        all_monitors_summary = uptime_api.get_all_monitor_stats()

        connection = get_db_connection()
        cursor = connection.cursor()
        user_reports: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        monitor_targets = (
            all_monitors_summary
            if not urls
            else [{"id": None, "url": u, "friendlyName": u} for u in urls]
        )

        for monitor in monitor_targets:
            monitor_id = monitor.get("id")
            site_url = monitor.get("url")
            site_name = monitor.get("friendlyName", site_url)

            # User email
            user_email = "admin@example.com"
            if monitor_id:
                cursor.execute("SELECT userid FROM monitors WHERE monitorid = %s", (monitor_id,))
                row = cursor.fetchone()
                if row:
                    user_id = row[0]
                    cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
                    user_row = cursor.fetchone()
                    if user_row:
                        user_email = user_row[0]

            # SSL Info
            ssl_data = ssl_checker.get_ssl_certificate_info(site_url)

            # Lighthouse
            try:
                lighthouse_data = await fetch_lighthouse_score(site_url, strategy="mobile")
            except Exception as e:
                logger.error(f"Lighthouse failed for {site_url}: {e}")
                lighthouse_data = {"error": str(e)}

            # Link Scan
            try:
                link_scan_data = scanner.scan(site_url, max_pages=max_pages)
            except Exception as e:
                logger.error(f"Link scan failed for {site_url}: {e}")
                link_scan_data = {"error": str(e)}

            # Merge all data
            report = {
                **monitor,  # uptime stats
                "ssl": ssl_data,
                "lighthouse": lighthouse_data,
                "link_scan": link_scan_data,
            }

            user_reports[user_email].append(report)

        # Send email per user
        for user_email, reports in user_reports.items():
            try:
                html_body = build_html_report(user_email, reports)
                email_service.send_mail(
                    recipient_email=user_email,
                    subject="📊 Your Website Monitoring Report",
                    html=html_body,
                    text="Please view this report in an HTML-compatible client."
                )
                logger.info(f"📧 Report sent to {user_email}")
            except Exception as e:
                logger.error(f"❌ Failed to send report to {user_email}: {e}")

        cursor.close()
        connection.close()

        return {"monitors": all_monitors_summary, "user_reports": user_reports}

    except Exception as e:
        logger.error(f"Error in report generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch detailed report")
    



@router.get("/send") 
async def trigger_report_sending(background_tasks: BackgroundTasks):
    """Endpoint to manually trigger report sending."""
    try:
        print("before get report")
        background_tasks.add_task(get_report)  # runs after response is sent
        logger.info("✅ Immediate report sending job scheduled")
        print("after get report")
        return {"status": "success", "detail": "Report sending triggered."}
    except Exception as e:
        logger.error(f"Failed to trigger report sending: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger report sending: {e}")



def register(main_router):
    main_router.include_router(router)




async def get_report(max_pages=15):
  try:
      # Fetch all monitors with uptime stats
      all_monitors_summary = uptime_api.get_all_monitor_stats()

      connection = get_db_connection()
      cursor = connection.cursor()
      user_reports: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
      urls = []

      monitor_targets = (
          all_monitors_summary
      )

      for monitor in monitor_targets:
          print("monitor:", monitor)
          monitor_id = monitor.get("id")
          site_url = monitor.get("url")
          site_name = monitor.get("friendlyName", site_url)

          # User email
          user_email = "admin@example.com"
          if monitor_id:
              cursor.execute("SELECT userid FROM monitors WHERE monitorid = %s", (monitor_id,))
              row = cursor.fetchone()
              if row:
                  user_id = row[0]
                  cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
                  user_row = cursor.fetchone()
                  if user_row:
                      user_email = user_row[0]

          # SSL Info
          ssl_data = ssl_checker.get_ssl_certificate_info(site_url)

          # Lighthouse
          try:
              lighthouse_data = await fetch_lighthouse_score(site_url, strategy="mobile")
          except Exception as e:
              logger.error(f"Lighthouse failed for {site_url}: {e}")
              lighthouse_data = {"error": str(e)}

          # Link Scan
          try:
              link_scan_data = scanner.scan(site_url, max_pages=max_pages)
          except Exception as e:
              logger.error(f"Link scan failed for {site_url}: {e}")
              link_scan_data = {"error": str(e)}

          # Merge all data
          report = {
              **monitor,  # uptime stats
              "ssl": ssl_data,
              "lighthouse": lighthouse_data,
              "link_scan": link_scan_data,
          }

          user_reports[user_email].append(report)

      # Send email per user
      for user_email, reports in user_reports.items():
          try:
              html_body = build_html_report(user_email, reports)
              email_service.send_mail(
                  recipient_email=user_email,
                  subject="📊 Your Website Monitoring Report",
                  html=html_body,
                  text="Please view this report in an HTML-compatible client."
              )
              logger.info(f"📧 Report sent to {user_email}")
          except Exception as e:
              logger.error(f"❌ Failed to send report to {user_email}: {e}")

      cursor.close()
      connection.close()
  except Exception as e:
      logger.error(f"Error in report generation: {e}")
      