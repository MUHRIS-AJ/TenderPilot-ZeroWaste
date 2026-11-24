"""Source-allowlisted public API adapter; standard library only."""
from __future__ import annotations
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ALLOWED_HOSTS = frozenset({
    "api.crossref.org", "api.openalex.org",
    "eonet.gsfc.nasa.gov", "earthquake.usgs.gov",
    "api.ted.europa.eu", "api.grants.gov",
    "overpass-api.de", "overpass.private.coffee",
    "api.fda.gov", "www.saferproducts.gov",
    "api.worldbank.org"
})

class SourceError(Exception):
    """Public source is unavailable, invalid, or over quota."""

def request_json(url: str, params: dict | None = None, payload: dict | None = None):
    if not isinstance(url, str) or urlparse(url).scheme != "https" or urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("Only allowlisted official HTTPS API hosts are permitted.")
    if params:
        url += ("&" if "?" in url else "?") + urlencode(params)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"User-Agent": "MUHRIS-AJ-Agent-Lab/0.1 (public educational research)", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    for attempt in range(2):
        try:
            with urlopen(request, timeout=12) as response:
                raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise SourceError("API response exceeded the 2 MB safety limit.")
            return json.loads(raw)
        except HTTPError as exc:
            if exc.code in (429, 502, 503) and attempt == 0:
                time.sleep(0.4)
                continue
            raise SourceError("Source returned HTTP " + str(exc.code)) from None
        except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            raise SourceError("Source unavailable or returned invalid JSON: " + type(exc).__name__) from None
    raise SourceError("Source unavailable.")
