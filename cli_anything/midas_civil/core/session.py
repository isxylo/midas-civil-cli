"""Session state management for the MIDAS Civil NX CLI harness."""
import json
import os
from datetime import datetime
from pathlib import Path

SESSION_FILE = Path.home() / ".midas_civil_session.json"

_DEFAULTS = {
    "mapi_key": "",
    "base_url": "https://moa-engineers.midasit.com:443/civil",
    "connected": False,
    "last_command": "",
}


class Session:
    """Persists connection state between CLI invocations."""

    def __init__(self, session_file: Path = SESSION_FILE):
        self._file = session_file
        self._data = self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load(self) -> dict:
        if self._file.exists():
            try:
                with open(self._file) as f:
                    data = json.load(f)
                # Backfill any missing keys from defaults
                for k, v in _DEFAULTS.items():
                    data.setdefault(k, v)
                return data
            except (json.JSONDecodeError, OSError):
                pass
        return dict(_DEFAULTS)

    def save(self) -> None:
        self._data["last_command"] = datetime.utcnow().isoformat()
        try:
            with open(self._file, "w") as f:
                json.dump(self._data, f, indent=2)
        except OSError:
            pass

    def clear(self) -> None:
        self._data = dict(_DEFAULTS)
        if self._file.exists():
            self._file.unlink()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def mapi_key(self) -> str:
        return self._data.get("mapi_key", "")

    @mapi_key.setter
    def mapi_key(self, value: str) -> None:
        self._data["mapi_key"] = value

    @property
    def base_url(self) -> str:
        return self._data.get("base_url", _DEFAULTS["base_url"])

    @base_url.setter
    def base_url(self, value: str) -> None:
        self._data["base_url"] = value

    @property
    def connected(self) -> bool:
        return self._data.get("connected", False)

    @connected.setter
    def connected(self, value: bool) -> None:
        self._data["connected"] = value

    # ------------------------------------------------------------------
    # Resolve credentials: CLI flag > env var > session file
    # ------------------------------------------------------------------
    @staticmethod
    def resolve_key(flag_value: str | None = None) -> str:
        if flag_value:
            return flag_value
        env = os.environ.get("MIDAS_MAPI_KEY", "")
        if env:
            return env
        s = Session()
        return s.mapi_key

    @staticmethod
    def resolve_url(flag_value: str | None = None) -> str:
        if flag_value:
            return flag_value
        env = os.environ.get("MIDAS_BASE_URL", "")
        if env:
            return env
        s = Session()
        return s.base_url or _DEFAULTS["base_url"]

    def to_dict(self) -> dict:
        return dict(self._data)
