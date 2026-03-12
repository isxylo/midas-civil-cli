"""Construction stage operations."""
from .connection import Connection


class ConstructionOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _next_id(self) -> int:
        existing = self.conn.get("/db/STAG")
        if existing and "STAG" in existing and existing["STAG"]:
            return max(int(k) for k in existing["STAG"].keys()) + 1
        return 1

    def add_stage(self, name: str, day: int = 0,
                  stage_id: int | None = None) -> dict:
        """Add a construction stage."""
        if stage_id is None:
            stage_id = self._next_id()
        body = {
            "Assign": {
                str(stage_id): {
                    "NAME": name,
                    "DAY": day,
                }
            }
        }
        resp = self.conn.put("/db/STAG", body)
        resp["stage_id"] = stage_id
        return resp

    def list_stages(self) -> dict:
        return self.conn.get("/db/STAG")

    def get(self, stage_id: int) -> dict:
        resp = self.conn.get("/db/STAG")
        if "STAG" in resp and str(stage_id) in resp["STAG"]:
            return {"stage_id": stage_id, "data": resp["STAG"][str(stage_id)]}
        return {"error": f"Stage {stage_id} not found"}

    def delete_all(self) -> dict:
        return self.conn.delete("/db/STAG/")
