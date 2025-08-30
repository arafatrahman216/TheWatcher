import logging
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.AuthDB import get_db, Website
from database.schemas import WebsiteResponse
from services.uptime_service import uptime_service

logger = logging.getLogger(__name__)


def register(router):
    @router.get("/website")
    async def get_monitored_website(db: Session = Depends(get_db)):
        """Get the monitored website information"""
        try:
            website = db.query(Website).filter(Website.id == uptime_service.website_id).first()
            if not website:
                raise HTTPException(status_code=404, detail="Monitored website not found")
            
            return WebsiteResponse(
                id=website.id,
                url=website.url,
                name=website.name,
                created_at=website.created_at,
                is_active=website.is_active
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting monitored website: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
