"""Tendon (prestress) operations."""
from .connection import Connection


class TendonOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _next_prop_id(self) -> int:
        existing = self.conn.get("/db/TDNT")
        if existing and "TDNT" in existing and existing["TDNT"]:
            return max(int(k) for k in existing["TDNT"].keys()) + 1
        return 1

    def _next_profile_id(self) -> int:
        existing = self.conn.get("/db/TDNA")
        if existing and "TDNA" in existing and existing["TDNA"]:
            return max(int(k) for k in existing["TDNA"].keys()) + 1
        return 1

    def _next_prestress_id(self) -> int:
        existing = self.conn.get("/db/TDPL")
        if existing and "TDPL" in existing and existing["TDPL"]:
            return max(int(k) for k in existing["TDPL"].keys()) + 1
        return 1

    # ------------------------------------------------------------------
    # Tendon property
    # ------------------------------------------------------------------
    def add_property(self, name: str, rho: float, ult_st: float,
                     yield_st: float, curv_fric: float = 0.0,
                     wob_fric: float = 0.0, prop_id: int | None = None) -> dict:
        """Add a tendon material property."""
        if prop_id is None:
            prop_id = self._next_prop_id()
        body = {
            "Assign": {
                str(prop_id): {
                    "NAME": name,
                    "RHO": rho,
                    "ULT_ST": ult_st,
                    "YIELD_ST": yield_st,
                    "CURV_FRIC_FAC": curv_fric,
                    "WOB_FRIC_FAC": wob_fric,
                }
            }
        }
        resp = self.conn.put("/db/TDNT", body)
        resp["prop_id"] = prop_id
        return resp

    def list_properties(self) -> dict:
        return self.conn.get("/db/TDNT")

    def delete_all_properties(self) -> dict:
        return self.conn.delete("/db/TDNT/")

    # ------------------------------------------------------------------
    # Tendon profile
    # ------------------------------------------------------------------
    def add_profile(self, name: str, prop_id: int, elem_list: list[int],
                    profile_id: int | None = None) -> dict:
        """Add a tendon profile (geometry along elements)."""
        if profile_id is None:
            profile_id = self._next_profile_id()
        body = {
            "Assign": {
                str(profile_id): {
                    "NAME": name,
                    "PROP_ID": prop_id,
                    "ELEM": elem_list,
                }
            }
        }
        resp = self.conn.put("/db/TDNA", body)
        resp["profile_id"] = profile_id
        return resp

    def list_profiles(self) -> dict:
        return self.conn.get("/db/TDNA")

    def delete_all_profiles(self) -> dict:
        return self.conn.delete("/db/TDNA/")

    # ------------------------------------------------------------------
    # Prestress
    # ------------------------------------------------------------------
    def add_prestress(self, profile_name: str, force: float,
                      tension_type: str = "BOTH",
                      prestress_id: int | None = None) -> dict:
        """Add prestress application to a tendon profile."""
        if prestress_id is None:
            prestress_id = self._next_prestress_id()
        body = {
            "Assign": {
                str(prestress_id): {
                    "TDNAME": profile_name,
                    "FORCE": force,
                    "TENS_TYPE": tension_type,
                }
            }
        }
        resp = self.conn.put("/db/TDPL", body)
        resp["prestress_id"] = prestress_id
        return resp

    def list_prestress(self) -> dict:
        return self.conn.get("/db/TDPL")

    def delete_all_prestress(self) -> dict:
        return self.conn.delete("/db/TDPL/")
