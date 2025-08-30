from typing import Optional

from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.database import get_db
from services.uptime_service import uptime_service  # reuse configured site url
from services.linkscan_pkg.scanner import LinkScannerService


def register(router):
    @router.get("/linkscan", tags=["linkscan"])
    async def run_link_scan(
        max_pages: int = Query(50, ge=1, le=50),
        start_url: Optional[str] = None,
        db: Session = Depends(get_db),
    ):
        """
        Scan for broken links starting from the monitored website (or a provided URL).
        Crawls same-domain pages up to `max_pages` (hard-capped at 50).
        """
        try:
            service = LinkScannerService()
            root = start_url or uptime_service.website_url
            result = service.scan(start_url=root, max_pages=max_pages)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Link scan failed: {e}")
