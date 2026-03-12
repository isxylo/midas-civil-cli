"""Thickness definition operations."""
from .connection import Connection


class ThicknessOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _next_id(self) -> int:
        existing = self.conn.get("/db/THIK")
        if existing and "THIK" in existing and existing["THIK"]:
            return max(int(k) for k in existing["THIK"].keys()) + 1
        return 1

    def add(self, name: str, thick: float, thick_out: float = -1,
            offset: float = 0, thick_id: int | None = None) -> dict:
        """Add a plate thickness definition."""
        if thick_id is None:
            thick_id = self._next_id()
        bINOUT = thick_out != -1
        t_out = thick if thick_out == -1 else thick_out
        off_type = 0 if offset == 0 else 1
        body = {
            "Assign": {
                str(thick_id): {
                    "NAME": name,
                    "TYPE": "VALUE",
                    "bINOUT": bINOUT,
                    "T_IN": thick,
                    "T_OUT": t_out,
                    "OFFSET": off_type,
                    "O_VALUE": offset,
                }
            }
        }
        resp = self.conn.put("/db/THIK", body)
        resp["thick_id"] = thick_id
        return resp

    def list(self) -> dict:
        return self.conn.get("/db/THIK")

    def get(self, thick_id: int) -> dict:
        resp = self.conn.get("/db/THIK")
        if "THIK" in resp and str(thick_id) in resp["THIK"]:
            return {"thick_id": thick_id, "data": resp["THIK"][str(thick_id)]}
        return {"error": f"Thickness {thick_id} not found"}

    def delete_all(self) -> dict:
        return self.conn.delete("/db/THIK/")
