import os
import httpx
from fastapi import HTTPException, Query, APIRouter
from typing import Dict

PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def _get_api_key() -> str:
    """Fetch Google API key from environment."""
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")
    return key

async def fetch_lighthouse_score(url: str, strategy: str = "mobile") -> Dict:
    """Fetch Lighthouse performance score for a URL (mobile/desktop)."""
    params = {
        "url": url,
        "key": _get_api_key(),
        "strategy": strategy,import os
import httpx
from fastapi import HTTPException, Query, APIRouter
from typing import Dict

PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Read monitored website from environment
DEFAULT_WEBSITE_URL = os.getenv("MONITORED_WEBSITE_URL")

def _get_api_key() -> str:
    """Fetch Google API key from environment."""
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")
    return key

async def fetch_lighthouse_score(url: str, strategy: str = "mobile") -> Dict:
    """Fetch Lighthouse performance score for a URL (mobile/desktop)."""
    params = {
        "url": url,
        "key": _get_api_key(),
        "strategy": strategy,
        "category": "performance"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(PAGESPEED_API, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch Lighthouse data")
        data = resp.json()

    try:
        score = data["lighthouseResult"]["categories"]["performance"]["score"]
        score_percent = round(score * 100, 2)

        audits = data.get("lighthouseResult", {}).get("audits", {})
        metrics = {
            "FCP": audits.get("first-contentful-paint", {}).get("numericValue"),
            "LCP": audits.get("largest-contentful-paint", {}).get("numericValue"),
            "TBT": audits.get("total-blocking-time", {}).get("numericValue"),
            "CLS": audits.get("cumulative-layout-shift", {}).get("numericValue"),
        }

        return {
            "url": url,
            "strategy": strategy,
            "performance_score": score_percent,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not parse Lighthouse result: {e}")

def register(router: APIRouter):
    @router.get("/performance", tags=["performance"])
    async def get_performance(
        url: str = Query(None, description="Website URL to test (include https://)"),
        strategy: str = Query("mobile", regex="^(mobile|desktop)$")
    ):
        # Use default if URL not provided
        target_url = url or DEFAULT_WEBSITE_URL
        if not target_url:
            raise HTTPException(status_code=400, detail="No website URL provided or configured")
        return await fetch_lighthouse_score(target_url, strategy)

        "category": "performance"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(PAGESPEED_API, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch Lighthouse data")
        data = resp.json()

    try:
        score = data["lighthouseResult"]["categories"]["performance"]["score"]
        score_percent = round(score * 100, 2)

        audits = data.get("lighthouseResult", {}).get("audits", {})
        metrics = {
            "FCP": audits.get("first-contentful-paint", {}).get("numericValue"),
            "LCP": audits.get("largest-contentful-paint", {}).get("numericValue"),
            "TBT": audits.get("total-blocking-time", {}).get("numericValue"),
            "CLS": audits.get("cumulative-layout-shift", {}).get("numericValue"),
        }

        return {
            "url": url,
            "strategy": strategy,
            "performance_score": score_percent,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not parse Lighthouse result: {e}")

def register(router: APIRouter):
    @router.get("/performance", tags=["performance"])
    async def get_performance(
        url: str = Query(..., description="Website URL to test (include https://)"),
        strategy: str = Query("mobile", regex="^(mobile|desktop)$")
    ):
        return await fetch_lighthouse_score(url, strategy)
