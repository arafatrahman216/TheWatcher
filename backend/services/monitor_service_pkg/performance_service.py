import os
import httpx
from fastapi import HTTPException
from typing import Dict

PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def _get_api_key() -> str:
    """Fetch Google API key from environment."""
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")
    return key

async def fetch_lighthouse_score(url: str, strategy: str = "mobile") -> Dict:
    """
    Fetch Lighthouse performance score for a URL (mobile/desktop).
    Always returns a dict with either 'metrics' + 'performance_score'
    or an 'error' key.
    """
    params = {
        "url": url,
        "key": _get_api_key(),
        "strategy": strategy,
        "category": "performance"
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(PAGESPEED_API, params=params)
            if resp.status_code != 200:
                return {"error": f"Failed to fetch Lighthouse data: HTTP {resp.status_code}"}
            data = resp.json()

        try:
            score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score")
            if score is None:
                return {"error": "Lighthouse result missing performance score"}

            score_percent = round(score * 100, 2)
            audits = data.get("lighthouseResult", {}).get("audits", {})

            metrics = {
                "FCP": audits.get("first-contentful-paint", {}).get("numericValue", None),
                "LCP": audits.get("largest-contentful-paint", {}).get("numericValue", None),
                "TBT": audits.get("total-blocking-time", {}).get("numericValue", None),
                "CLS": audits.get("cumulative-layout-shift", {}).get("numericValue", None),
            }

            return {
                "url": url,
                "strategy": strategy,
                "performance_score": score_percent,
                "metrics": metrics
            }
        except Exception as e:
            return {"error": f"Could not parse Lighthouse result: {e}"}

    except Exception as e:
        return {"error": f"Failed to fetch Lighthouse data: {e}"}
