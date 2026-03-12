"""Connection helpers: configure MAPI credentials and verify connectivity."""
import requests
from .session import Session


class Connection:
    """Manages MAPI_KEY and MAPI_BASEURL without importing midas_civil
    (avoids Windows registry calls and sys.exit on import)."""

    def __init__(self, mapi_key: str = "", base_url: str = ""):
        self.mapi_key = mapi_key or Session.resolve_key()
        self.base_url = base_url or Session.resolve_url()

    # ------------------------------------------------------------------
    # Low-level HTTP
    # ------------------------------------------------------------------
    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "MAPI-Key": self.mapi_key,
        }

    def request(self, method: str, endpoint: str, body: dict | None = None) -> dict:
        """Send an authenticated MAPI request and return the parsed JSON."""
        url = self.base_url.rstrip("/") + endpoint
        kwargs: dict = {
            "method": method.upper(),
            "url": url,
            "headers": self._headers(),
            "timeout": 30,
        }
        if method.upper() not in ("GET", "DELETE"):
            kwargs["json"] = body or {}
        resp = requests.request(**kwargs)
        try:
            return resp.json()
        except Exception:
            return {"status_code": resp.status_code, "text": resp.text}

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    def ping(self) -> dict:
        """Return project info from Civil NX or an error dict."""
        try:
            resp = self.request("GET", "/db/PJCF")
            if "PJCF" in resp:
                return {"ok": True, "data": resp["PJCF"]}
            return {"ok": False, "error": resp}
        except requests.exceptions.ConnectionError as exc:
            return {"ok": False, "error": str(exc)}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------
    def get(self, endpoint: str) -> dict:
        return self.request("GET", endpoint)

    def put(self, endpoint: str, body: dict) -> dict:
        return self.request("PUT", endpoint, body)

    def post(self, endpoint: str, body: dict) -> dict:
        return self.request("POST", endpoint, body)

    def delete(self, endpoint: str) -> dict:
        return self.request("DELETE", endpoint)

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass
