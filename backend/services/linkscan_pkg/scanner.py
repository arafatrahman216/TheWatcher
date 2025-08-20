import time
import logging
from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
MAX_PAGES_HARD_LIMIT = 50


class LinkScannerService:
    """
    BFS crawl up to `max_pages` pages on the same domain; check each discovered link.
    Returns a JSON-serializable dict with summary + broken links.
    """

    def __init__(self, user_agent: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or "TheWatcher-LinkScanner/1.0"
        })

    def _normalize_start(self, start_url: str) -> str:
        start_url = (start_url or "").strip()
        if not start_url.startswith(("http://", "https://")):
            start_url = "https://" + start_url
        return start_url

    def _same_domain(self, base: str, url: str) -> bool:
        try:
            return urlparse(base).netloc == urlparse(url).netloc
        except Exception:
            return False

    def _is_http_like(self, href: str) -> bool:
        if not href:
            return False
        href = href.strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            return False
        return True

    def _fetch_html(self, url: str) -> Optional[str]:
        try:
            r = self.session.get(url, timeout=DEFAULT_TIMEOUT, allow_redirects=True)
            ctype = (r.headers.get("Content-Type") or "").lower()
            if "text/html" in ctype:
                return r.text
            return None
        except requests.RequestException as e:
            logger.debug(f"Fetch failed {url}: {e}")
            return None

    def _check_link(self, url: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """Returns (ok, status_code, error). ok=True means not broken."""
        try:
            resp = self.session.head(url, allow_redirects=True, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 405:  # HEAD not allowed
                resp = self.session.get(url, allow_redirects=True, timeout=DEFAULT_TIMEOUT)
            return (200 <= resp.status_code < 400, resp.status_code, None)
        except requests.RequestException as e:
            return (False, None, str(e))

    def scan(self, start_url: str, max_pages: int = 50) -> Dict:
        started_at = time.time()
        start_url = self._normalize_start(start_url)
        max_pages = max(1, min(int(max_pages or 50), MAX_PAGES_HARD_LIMIT))

        visited_pages: Set[str] = set()
        queued: deque[str] = deque([start_url])

        scanned_pages: List[str] = []
        seen_links: Set[str] = set()

        total_links = 0
        ok_count = 0
        broken_count = 0
        skipped_non_http = 0

        broken: List[Dict] = []

        while queued and len(scanned_pages) < max_pages:
            page_url = queued.popleft()
            if page_url in visited_pages:
                continue
            visited_pages.add(page_url)
            scanned_pages.append(page_url)

            html = self._fetch_html(page_url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a"):
                href = a.get("href")
                if not self._is_http_like(href):
                    skipped_non_http += 1
                    continue

                abs_url = urljoin(page_url, href)

                # Enqueue same-domain pages for BFS
                if self._same_domain(start_url, abs_url) and abs_url not in visited_pages:
                    queued.append(abs_url)

                # Only check each unique link once
                if abs_url in seen_links:
                    continue
                seen_links.add(abs_url)

                total_links += 1
                ok, status, err = self._check_link(abs_url)
                if ok:
                    ok_count += 1
                else:
                    broken_count += 1
                    broken.append({
                        "source_page": page_url,
                        "link": abs_url,
                        "status_code": status,
                        "error": err
                    })

        duration_ms = int((time.time() - started_at) * 1000)
        return {
            "start_url": start_url,
            "scanned_pages": scanned_pages,
            "scanned_count": len(scanned_pages),
            "max_pages": max_pages,
            "total_links_checked": total_links,
            "ok_count": ok_count,
            "broken_count": broken_count,
            "skipped_non_http": skipped_non_http,
            "broken": broken,
            "duration_ms": duration_ms
        }
