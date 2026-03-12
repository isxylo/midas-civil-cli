"""Load combination operations."""
from .connection import Connection


class LoadCombOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _next_id(self) -> int:
        existing = self.conn.get("/db/LCOMB")
        if existing and "LCOMB" in existing and existing["LCOMB"]:
            return max(int(k) for k in existing["LCOMB"].keys()) + 1
        return 1

    def add(self, name: str, active: str = "ACTIVE", typ: str = "Add",
            cases: list[dict] | None = None,
            comb_id: int | None = None) -> dict:
        """
        Add a load combination.
        cases: list of {"name": "LC1", "factor": 1.0, "type": "ST"}
        """
        if comb_id is None:
            comb_id = self._next_id()
        load_items = []
        for c in (cases or []):
            load_items.append({
                "LCNAME": c.get("name", ""),
                "FACTOR": c.get("factor", 1.0),
                "TYPE": c.get("type", "ST"),
            })
        body = {
            "Assign": {
                str(comb_id): {
                    "NAME": name,
                    "ACTIVE": active,
                    "iTYPE": typ,
                    "LDCOMB": load_items,
                }
            }
        }
        resp = self.conn.put("/db/LCOMB", body)
        resp["comb_id"] = comb_id
        return resp

    def list(self) -> dict:
        return self.conn.get("/db/LCOMB")

    def get(self, comb_id: int) -> dict:
        resp = self.conn.get("/db/LCOMB")
        if "LCOMB" in resp and str(comb_id) in resp["LCOMB"]:
            return {"comb_id": comb_id, "data": resp["LCOMB"][str(comb_id)]}
        return {"error": f"Load combination {comb_id} not found"}

    def delete_all(self) -> dict:
        return self.conn.delete("/db/LCOMB/")
