"""Material definition operations."""
from .connection import Connection


class MaterialOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _next_id(self) -> int:
        existing = self.conn.get("/db/MATL")
        if existing and "MATL" in existing and existing["MATL"]:
            return max(int(k) for k in existing["MATL"].keys()) + 1
        return 1

    def add_steel(self, name: str, standard: str, grade: str,
                  mat_id: int | None = None) -> dict:
        if mat_id is None:
            mat_id = self._next_id()
        body = {
            "Assign": {
                str(mat_id): {
                    "TYPE": "STEEL",
                    "NAME": name,
                    "DAMP_RAT": 0.02,
                    "PARAM": [{
                        "P_TYPE": 1,
                        "STANDARD": standard,
                        "CODE": "",
                        "DB": grade,
                    }]
                }
            }
        }
        resp = self.conn.put("/db/MATL", body)
        resp["mat_id"] = mat_id
        return resp

    def add_concrete(self, name: str, standard: str, grade: str,
                     mat_id: int | None = None) -> dict:
        if mat_id is None:
            mat_id = self._next_id()
        body = {
            "Assign": {
                str(mat_id): {
                    "TYPE": "CONC",
                    "NAME": name,
                    "DAMP_RAT": 0.05,
                    "PARAM": [{
                        "P_TYPE": 1,
                        "STANDARD": standard,
                        "CODE": "",
                        "DB": grade,
                    }]
                }
            }
        }
        resp = self.conn.put("/db/MATL", body)
        resp["mat_id"] = mat_id
        return resp

    def add_user(self, name: str, elasticity: float, poisson: float,
                 density: float, thermal: float = 1.2e-5,
                 mat_id: int | None = None) -> dict:
        """Add a user-defined isotropic material."""
        if mat_id is None:
            mat_id = self._next_id()
        body = {
            "Assign": {
                str(mat_id): {
                    "TYPE": "USER",
                    "NAME": name,
                    "ELAST": elasticity,
                    "POISN": poisson,
                    "DENSE": density,
                    "THERMAL": thermal,
                }
            }
        }
        resp = self.conn.put("/db/MATL", body)
        resp["mat_id"] = mat_id
        return resp

    def list(self) -> dict:
        return self.conn.get("/db/MATL")

    def get(self, mat_id: int) -> dict:
        resp = self.conn.get("/db/MATL")
        if "MATL" in resp and str(mat_id) in resp["MATL"]:
            return {"mat_id": mat_id, "data": resp["MATL"][str(mat_id)]}
        return {"error": f"Material {mat_id} not found"}

    def delete_all(self) -> dict:
        return self.conn.delete("/db/MATL/")
