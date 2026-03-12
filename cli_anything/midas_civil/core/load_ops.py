"""Load case and load application operations."""
from .connection import Connection


class LoadOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    # ------------------------------------------------------------------
    # Load cases
    # ------------------------------------------------------------------
    def add_load_case(self, name: str, lc_type: str = "USER") -> dict:
        existing = self.conn.get("/db/STLD")
        if existing and "STLD" in existing and existing["STLD"]:
            lc_id = max(int(k) for k in existing["STLD"].keys()) + 1
        else:
            lc_id = 1
        body = {
            "Assign": {
                str(lc_id): {
                    "NAME": name,
                    "TYPE": lc_type,
                }
            }
        }
        return self.conn.put("/db/STLD", body)

    def list_load_cases(self) -> dict:
        return self.conn.get("/db/STLD")

    # ------------------------------------------------------------------
    # Self weight
    # ------------------------------------------------------------------
    def add_self_weight(self, load_case_name: str,
                        direction: str = "Z", factor: float = -1.0) -> dict:
        """Add self-weight load to a load case."""
        body = {
            "Assign": {
                "1": {
                    "LCNAME": load_case_name,
                    "DIR": direction,
                    "FACT": factor,
                }
            }
        }
        return self.conn.put("/db/SELFWEIGHT", body)

    # ------------------------------------------------------------------
    # Nodal loads
    # ------------------------------------------------------------------
    def add_nodal_load(self, node_ids: list[int], load_case_name: str,
                       group: str = "",
                       fx: float = 0, fy: float = 0, fz: float = 0,
                       mx: float = 0, my: float = 0, mz: float = 0) -> dict:
        existing = self.conn.get("/db/CONLOAD")
        if existing and "CONLOAD" in existing and existing["CONLOAD"]:
            load_id = max(int(k) for k in existing["CONLOAD"].keys()) + 1
        else:
            load_id = 1
        assign: dict = {}
        for nid in node_ids:
            assign[str(load_id)] = {
                "LCNAME": load_case_name,
                "LDGR": group,
                "NODE": nid,
                "FX": fx, "FY": fy, "FZ": fz,
                "MX": mx, "MY": my, "MZ": mz,
            }
            load_id += 1
        return self.conn.put("/db/CONLOAD", {"Assign": assign})

    # ------------------------------------------------------------------
    # Beam loads
    # ------------------------------------------------------------------
    def add_beam_load(self, elem_ids: list[int], load_case_name: str,
                      group: str = "", value: float = 0.0,
                      direction: str = "GZ",
                      d: list[float] | None = None,
                      p: list[float] | None = None) -> dict:
        """
        Add distributed beam load.
        d: distance ratios [0, 0.5, 1.0], p: load values at each point.
        """
        if d is None:
            d = [0.0, 1.0]
        if p is None:
            p = [value, value]
        existing = self.conn.get("/db/BEAMLOAD")
        if existing and "BEAMLOAD" in existing and existing["BEAMLOAD"]:
            load_id = max(int(k) for k in existing["BEAMLOAD"].keys()) + 1
        else:
            load_id = 1
        assign: dict = {}
        for eid in elem_ids:
            assign[str(load_id)] = {
                "LCNAME": load_case_name,
                "LDGR": group,
                "ELEMENT": eid,
                "DIRECTION": direction,
                "D": d,
                "P": p,
                "TYPE": "UNILOAD",
                "USE_PROJECTION": False,
            }
            load_id += 1
        return self.conn.put("/db/BEAMLOAD", {"Assign": assign})

    # ------------------------------------------------------------------
    # Pressure loads (plate elements)
    # ------------------------------------------------------------------
    def add_pressure_load(self, elem_ids: list[int], load_case_name: str,
                          group: str = "", pressure: float = 0.0,
                          direction: str = "GZ") -> dict:
        existing = self.conn.get("/db/PRESSLOAD")
        if existing and "PRESSLOAD" in existing and existing["PRESSLOAD"]:
            load_id = max(int(k) for k in existing["PRESSLOAD"].keys()) + 1
        else:
            load_id = 1
        assign: dict = {}
        for eid in elem_ids:
            assign[str(load_id)] = {
                "LCNAME": load_case_name,
                "LDGR": group,
                "ELEM": eid,
                "DIR": direction,
                "PRES": pressure,
                "bPROJ": False,
            }
            load_id += 1
        return self.conn.put("/db/PRESSLOAD", {"Assign": assign})

    def add_beam_load_trapezoidal(self, elem_ids: list[int], load_case_name: str,
                                   d: list[float], p: list[float],
                                   direction: str = "GZ",
                                   group: str = "") -> dict:
        """Add a trapezoidal (non-uniform) beam distributed load."""
        existing = self.conn.get("/db/BEAMLOAD")
        if existing and "BEAMLOAD" in existing and existing["BEAMLOAD"]:
            load_id = max(int(k) for k in existing["BEAMLOAD"].keys()) + 1
        else:
            load_id = 1
        assign: dict = {}
        for eid in elem_ids:
            assign[str(load_id)] = {
                "LCNAME": load_case_name,
                "LDGR": group,
                "ELEMENT": eid,
                "DIRECTION": direction,
                "D": d,
                "P": p,
                "TYPE": "UNILOAD",
                "USE_PROJECTION": False,
            }
            load_id += 1
        return self.conn.put("/db/BEAMLOAD", {"Assign": assign})

    def add_load_to_mass(self, direction: str,
                         load_cases: list[str],
                         factors: list[float] | None = None) -> dict:
        """Convert static loads to masses."""
        if factors is None:
            factors = [1.0] * len(load_cases)
        items = [
            {"LCNAME": lc, "FACTOR": f}
            for lc, f in zip(load_cases, factors)
        ]
        body = {
            "Assign": {
                "1": {
                    "DIR": direction,
                    "ITEMS": items,
                }
            }
        }
        return self.conn.put("/db/LTOM", body)

    def delete_load_case(self, name: str) -> dict:
        """Delete a specific load case by name."""
        resp = self.conn.get("/db/STLD")
        if "STLD" not in resp:
            return {"error": "No load cases found"}
        for k, v in resp["STLD"].items():
            if v.get("NAME") == name:
                return self.conn.delete(f"/db/STLD/{k}")
        return {"error": f"Load case '{name}' not found"}

    def list_nodal_loads(self) -> dict:
        return self.conn.get("/db/CONLOAD")

    def list_beam_loads(self) -> dict:
        return self.conn.get("/db/BEAMLOAD")

    def list_pressure_loads(self) -> dict:
        return self.conn.get("/db/PRESSLOAD")
