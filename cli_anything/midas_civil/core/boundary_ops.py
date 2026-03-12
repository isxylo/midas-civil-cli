"""Boundary condition operations: supports, elastic links, rigid links."""
from .connection import Connection

_CONSTRAINT_MAP = {
    "fix":  {"DX": True,  "DY": True,  "DZ": True,  "RX": True,  "RY": True,  "RZ": True},
    "pin":  {"DX": True,  "DY": True,  "DZ": True,  "RX": False, "RY": False, "RZ": False},
    "roller": {"DX": False, "DY": True,  "DZ": True,  "RX": False, "RY": False, "RZ": False},
}


class BoundaryOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _next_sup_id(self) -> int:
        existing = self.conn.get("/db/SPRI")
        if existing and "SPRI" in existing and existing["SPRI"]:
            return max(int(k) for k in existing["SPRI"].keys()) + 1
        return 1

    def add_support(self, node_ids: list[int], constraint: str = "fix",
                    group: str = "") -> dict:
        """Apply support to nodes. constraint = 'fix', 'pin', 'roller',
        or a 6-char string like 'TTTTFF' (T=restrained, F=free)."""
        if constraint in _CONSTRAINT_MAP:
            cond = _CONSTRAINT_MAP[constraint]
        else:
            # Parse 6-char string TTTTFF
            keys = ["DX", "DY", "DZ", "RX", "RY", "RZ"]
            if len(constraint) == 6:
                cond = {k: (c.upper() == "T") for k, c in zip(keys, constraint)}
            else:
                return {"error": f"Unknown constraint: {constraint}"}

        assign: dict = {}
        sup_id = self._next_sup_id()
        for nid in node_ids:
            entry = {"NODE": nid, "GROUP_NAME": group}
            entry.update(cond)
            assign[str(sup_id)] = entry
            sup_id += 1

        return self.conn.put("/db/SPRI", {"Assign": assign})

    def list_supports(self) -> dict:
        return self.conn.get("/db/SPRI")

    def delete_supports(self) -> dict:
        return self.conn.delete("/db/SPRI/")

    def add_elastic_link(self, i_node: int, j_node: int,
                         link_type: str = "GEN",
                         sdx: float = 0, sdy: float = 0, sdz: float = 0,
                         srx: float = 0, sry: float = 0, srz: float = 0,
                         group: str = "") -> dict:
        existing = self.conn.get("/db/ELNK")
        if existing and "ELNK" in existing and existing["ELNK"]:
            link_id = max(int(k) for k in existing["ELNK"].keys()) + 1
        else:
            link_id = 1
        body = {
            "Assign": {
                str(link_id): {
                    "I_NODE": i_node,
                    "J_NODE": j_node,
                    "GROUP_NAME": group,
                    "LINK_TYPE": link_type,
                    "ANGLE": 0,
                    "SDx": sdx, "SDy": sdy, "SDz": sdz,
                    "SRx": srx, "SRy": sry, "SRz": srz,
                }
            }
        }
        return self.conn.put("/db/ELNK", body)

    def list_elastic_links(self) -> dict:
        return self.conn.get("/db/ELNK")

    def delete_elastic_links(self) -> dict:
        return self.conn.delete("/db/ELNK/")

    def add_rigid_link(self, master_node: int, slave_nodes: list[int],
                       dof: str = "123456", group: str = "") -> dict:
        existing = self.conn.get("/db/RIGD")
        if existing and "RIGD" in existing and existing["RIGD"]:
            link_id = max(int(k) for k in existing["RIGD"].keys()) + 1
        else:
            link_id = 1
        body = {
            "Assign": {
                str(link_id): {
                    "M_NODE": master_node,
                    "S_NODE": slave_nodes,
                    "GROUP_NAME": group,
                    "DOF": dof,
                }
            }
        }
        return self.conn.put("/db/RIGD", body)

    def list_rigid_links(self) -> dict:
        return self.conn.get("/db/RIGD")

    def delete_rigid_links(self) -> dict:
        return self.conn.delete("/db/RIGD/")

    # ------------------------------------------------------------------
    # Point springs
    # ------------------------------------------------------------------
    def add_point_spring(self, node_id: int,
                         sdx: float = 0, sdy: float = 0, sdz: float = 0,
                         srx: float = 0, sry: float = 0, srz: float = 0,
                         group: str = "", spring_id: int | None = None) -> dict:
        """Add a linear point spring support."""
        existing = self.conn.get("/db/NSPR")
        if spring_id is None:
            if existing and "NSPR" in existing and existing["NSPR"]:
                spring_id = max(int(k) for k in existing["NSPR"].keys()) + 1
            else:
                spring_id = 1
        body = {
            "Assign": {
                str(spring_id): {
                    "NODE": node_id,
                    "GROUP_NAME": group,
                    "SPRING_TYPE": "LINEAR",
                    "SDx": sdx, "SDy": sdy, "SDz": sdz,
                    "SRx": srx, "SRy": sry, "SRz": srz,
                }
            }
        }
        resp = self.conn.put("/db/NSPR", body)
        resp["spring_id"] = spring_id
        return resp

    def list_point_springs(self) -> dict:
        return self.conn.get("/db/NSPR")

    def delete_point_springs(self) -> dict:
        return self.conn.delete("/db/NSPR/")

    # ------------------------------------------------------------------
    # Multi-linear force-deformation function
    # ------------------------------------------------------------------
    def add_mlfc(self, name: str, func_type: str = "FORCE",
                 symm: bool = True,
                 data: list[list[float]] | None = None,
                 func_id: int | None = None) -> dict:
        """Add a multi-linear force-deformation function."""
        existing = self.conn.get("/db/MLFC")
        if func_id is None:
            if existing and "MLFC" in existing and existing["MLFC"]:
                func_id = max(int(k) for k in existing["MLFC"].keys()) + 1
            else:
                func_id = 1
        body = {
            "Assign": {
                str(func_id): {
                    "NAME": name,
                    "TYPE": func_type,
                    "SYMM": symm,
                    "DATA": data or [[0, 0], [1, 1]],
                }
            }
        }
        resp = self.conn.put("/db/MLFC", body)
        resp["func_id"] = func_id
        return resp

    def list_mlfc(self) -> dict:
        return self.conn.get("/db/MLFC")

    def delete_mlfc(self) -> dict:
        return self.conn.delete("/db/MLFC/")
