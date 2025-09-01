import os
import httpx
from fastapi import HTTPException, Query
from services.monitor_service_pkg.performance_service import fetch_lighthouse_score



def register(router):
    @router.get("/performance", tags=["performance"])
    async def get_performance(
        url: str = Query(..., description="Website URL to test (include https://)"),
        strategy: str = Query("mobile", regex="^(mobile|desktop)$")
    ):
        return await fetch_lighthouse_score(url, strategy)
