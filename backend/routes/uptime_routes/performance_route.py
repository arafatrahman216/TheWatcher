import os
import httpx
from fastapi import HTTPException, Query

API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
API_KEY = os.getenv("GOOGLE_API_KEY")


async def fetch_lighthouse_score(url: str, strategy: str = "mobile"):
    if not API_KEY:
        raise HTTPException(status_code=400, detail="GOOGLE_API_KEY not set")

    params = {
        "url": url,
        "key": API_KEY,
        "strategy": strategy,
        "category": "performance"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(API_URL, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch Lighthouse data")

        data = resp.json()

    try:
        score = data["lighthouseResult"]["categories"]["performance"]["score"]
        score_percent = round(score * 100, 2)
        audits = data["lighthouseResult"]["audits"]
        metrics = {
            "FCP": audits.get("first-contentful-paint", {}).get("numericValue"),
            "LCP": audits.get("largest-contentful-paint", {}).get("numericValue"),
            "TBT": audits.get("total-blocking-time", {}).get("numericValue"),
            "CLS": audits.get("cumulative-layout-shift", {}).get("numericValue"),
        }
        return {"url": url, "strategy": strategy, "performance_score": score_percent, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not parse Lighthouse result: {e}")


def register(router):
    @router.get("/performance", tags=["performance"])
    async def get_performance(
        url: str = Query(..., description="Website URL to test (include https://)"),
        strategy: str = Query("mobile", regex="^(mobile|desktop)$")
    ):
        return await fetch_lighthouse_score(url, strategy)
