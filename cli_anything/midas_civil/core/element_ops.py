"""Element CRUD operations."""
from .connection import Connection


class ElementOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _next_id(self) -> int:
        existing = self.conn.get("/db/ELEM")
        if existing and "ELEM" in existing and existing["ELEM"]:
            return max(int(k) for k in existing["ELEM"].keys()) + 1
        return 1

    def add_beam(self, i_node: int, j_node: int,
                 mat_id: int = 1, sect_id: int = 1,
                 elem_id: int | None = None, angle: float = 0.0) -> dict:
        """Add a beam element between two nodes."""
        if elem_id is None:
            elem_id = self._next_id()
        body = {
            "Assign": {
                str(elem_id): {
                    "TYPE": "BEAM",
                    "MATL": mat_id,
                    "SECT": sect_id,
                    "NODE": [i_node, j_node],
                    "ANGLE": angle,
                    "STYPE": 0,
                }
            }
        }
        resp = self.conn.put("/db/ELEM", body)
        resp["elem_id"] = elem_id
        return resp

    def add_truss(self, i_node: int, j_node: int,
                  mat_id: int = 1, sect_id: int = 1,
                  elem_id: int | None = None) -> dict:
        if elem_id is None:
            elem_id = self._next_id()
        body = {
            "Assign": {
                str(elem_id): {
                    "TYPE": "TRUSS",
                    "MATL": mat_id,
                    "SECT": sect_id,
                    "NODE": [i_node, j_node],
                    "ANGLE": 0,
                    "STYPE": 0,
                }
            }
        }
        resp = self.conn.put("/db/ELEM", body)
        resp["elem_id"] = elem_id
        return resp

    def add_plate(self, nodes: list[int],
                  mat_id: int = 1, thick_id: int = 1,
                  elem_id: int | None = None) -> dict:
        """Add a plate element (3 or 4 nodes)."""
        if len(nodes) not in (3, 4):
            return {"error": "Plate requires 3 or 4 nodes"}
        if elem_id is None:
            elem_id = self._next_id()
        body = {
            "Assign": {
                str(elem_id): {
                    "TYPE": "PLATE",
                    "MATL": mat_id,
                    "SECT": thick_id,
                    "NODE": nodes,
                    "ANGLE": 0,
                    "STYPE": 1,
                }
            }
        }
        resp = self.conn.put("/db/ELEM", body)
        resp["elem_id"] = elem_id
        return resp

    def list(self) -> dict:
        return self.conn.get("/db/ELEM")

    def get(self, elem_id: int) -> dict:
        resp = self.conn.get("/db/ELEM")
        if "ELEM" in resp and str(elem_id) in resp["ELEM"]:
            return {"elem_id": elem_id, "data": resp["ELEM"][str(elem_id)]}
        return {"error": f"Element {elem_id} not found"}

    def delete_all(self) -> dict:
        return self.conn.delete("/db/ELEM/")

    def sync(self) -> dict:
        resp = self.list()
        if "ELEM" in resp:
            count = len(resp["ELEM"])
            return {"count": count, "elements": resp["ELEM"]}
        return {"count": 0, "elements": {}}
