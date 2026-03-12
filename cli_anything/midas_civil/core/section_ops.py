"""Section definition operations."""
from .connection import Connection


class SectionOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _next_id(self) -> int:
        existing = self.conn.get("/db/SECT")
        if existing and "SECT" in existing and existing["SECT"]:
            return max(int(k) for k in existing["SECT"].keys()) + 1
        return 1

    def add_db(self, name: str, shape: str, standard: str, db_name: str,
               sect_id: int | None = None) -> dict:
        """Add a database section (e.g. AISC W-shapes)."""
        if sect_id is None:
            sect_id = self._next_id()
        body = {
            "Assign": {
                str(sect_id): {
                    "TYPE": "DB",
                    "NAME": name,
                    "SHAPE": shape,
                    "STANDARD": standard,
                    "DBNAME": db_name,
                }
            }
        }
        resp = self.conn.put("/db/SECT", body)
        resp["sect_id"] = sect_id
        return resp

    def add_value(self, name: str, shape: str, dimensions: list[float],
                  sect_id: int | None = None) -> dict:
        """Add a parametric section by explicit dimensions."""
        if sect_id is None:
            sect_id = self._next_id()
        body = {
            "Assign": {
                str(sect_id): {
                    "TYPE": "VALUE",
                    "NAME": name,
                    "SHAPE": shape,
                    "SECT_COND": dimensions,
                }
            }
        }
        resp = self.conn.put("/db/SECT", body)
        resp["sect_id"] = sect_id
        return resp

    def list(self) -> dict:
        return self.conn.get("/db/SECT")

    def get(self, sect_id: int) -> dict:
        resp = self.conn.get("/db/SECT")
        if "SECT" in resp and str(sect_id) in resp["SECT"]:
            return {"sect_id": sect_id, "data": resp["SECT"][str(sect_id)]}
        return {"error": f"Section {sect_id} not found"}

    def add_psc(self, name: str, symm: bool = True, joint=None, sect_id=None) -> dict:
        """Add a PSC (prestressed concrete) box section."""
        if sect_id is None:
            sect_id = self._next_id()
        body = {
            "Assign": {
                str(sect_id): {
                    "TYPE": "VALUE",
                    "NAME": name,
                    "SHAPE": "PSC",
                    "SYMM": symm,
                    "SECT_COND": joint or [],
                }
            }
        }
        resp = self.conn.put("/db/SECT", body)
        resp["sect_id"] = sect_id
        return resp

    def add_i_shape(self, name: str, symm: bool = True, dims=None, sect_id=None) -> dict:
        """Add a parametric I-shape section. dims: [H, B1, tw, tf1, B2, tf2]"""
        if sect_id is None:
            sect_id = self._next_id()
        body = {
            "Assign": {
                str(sect_id): {
                    "TYPE": "VALUE",
                    "NAME": name,
                    "SHAPE": "I",
                    "SYMM": symm,
                    "SECT_COND": dims or [],
                }
            }
        }
        resp = self.conn.put("/db/SECT", body)
        resp["sect_id"] = sect_id
        return resp

    def add_tapered(self, name: str, sect_i_id: int, sect_j_id: int, sect_id=None) -> dict:
        """Add a tapered section referencing I-end and J-end section IDs."""
        if sect_id is None:
            sect_id = self._next_id()
        body = {
            "Assign": {
                str(sect_id): {
                    "TYPE": "TAPERED",
                    "NAME": name,
                    "SECT_I": sect_i_id,
                    "SECT_J": sect_j_id,
                }
            }
        }
        resp = self.conn.put("/db/SECT", body)
        resp["sect_id"] = sect_id
        return resp

    def sync(self) -> dict:
        resp = self.conn.get("/db/SECT")
        if "SECT" in resp:
            return {"count": len(resp["SECT"]), "sections": resp["SECT"]}
        return {"count": 0, "sections": {}}

    def delete_all(self) -> dict:
        return self.conn.delete("/db/SECT/")
