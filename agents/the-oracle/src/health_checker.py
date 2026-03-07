"""Test endpoint reachability and measure latency."""
import time
import httpx
from typing import Optional


def check_endpoint(url: str, timeout: float = 5.0) -> dict:
    """Check if an endpoint is reachable and measure latency."""
    blocked = ("localhost", "127.0.0.1", "0.0.0.0", "::1", ".internal", "169.254.", "10.", "192.168.")
    if not url or any(b in url.lower() for b in blocked):
        return {"reachable": False, "reason": "private_address", "latency_ms": None}

    # Normalize: some endpoints are just paths like "/api/run"
    if not url.startswith("http"):
        return {"reachable": False, "reason": "invalid_url", "latency_ms": None}

    try:
        # Try health endpoint first, then root
        for path in ["/health", ""]:
            try:
                test_url = url.rstrip("/") + path
                start = time.time()
                resp = httpx.head(test_url, timeout=timeout, follow_redirects=True)
                # Some servers reject HEAD, fall back to GET
                if resp.status_code == 405:
                    start = time.time()
                    resp = httpx.get(test_url, timeout=timeout, follow_redirects=True)
                latency = (time.time() - start) * 1000
                return {
                    "reachable": True,
                    "status_code": resp.status_code,
                    "latency_ms": round(latency, 1),
                }
            except (httpx.ConnectError, httpx.TimeoutException):
                continue

        return {"reachable": False, "reason": "connection_failed", "latency_ms": None}
    except Exception as e:
        return {"reachable": False, "reason": str(e)[:100], "latency_ms": None}
