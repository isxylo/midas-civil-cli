"""Structure group, boundary group, and load group operations."""
from .connection import Connection


class GroupOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    # ------------------------------------------------------------------
    # Structure Groups
    # ------------------------------------------------------------------
    def add_structure_group(self, name: str,
                            node_ids: list[int] | None = None,
                            elem_ids: list[int] | None = None) -> dict:
        """Add or update a structure group."""
        body = {
            "Assign": {
                name: {
                    "NAME": name,
                    "NLIST": node_ids or [],
                    "ELIST": elem_ids or [],
                }
            }
        }
        return self.conn.put("/db/STGR", body)

    def list_structure_groups(self) -> dict:
        return self.conn.get("/db/STGR")

    def delete_structure_group(self, name: str) -> dict:
        return self.conn.delete(f"/db/STGR/{name}")

    def delete_all_structure_groups(self) -> dict:
        return self.conn.delete("/db/STGR/")

    # ------------------------------------------------------------------
    # Boundary Groups
    # ------------------------------------------------------------------
    def add_boundary_group(self, name: str) -> dict:
        """Add a boundary group."""
        body = {
            "Assign": {
                name: {"NAME": name}
            }
        }
        return self.conn.put("/db/BNGR", body)

    def list_boundary_groups(self) -> dict:
        return self.conn.get("/db/BNGR")

    def delete_all_boundary_groups(self) -> dict:
        return self.conn.delete("/db/BNGR/")

    # ------------------------------------------------------------------
    # Load Groups
    # ------------------------------------------------------------------
    def add_load_group(self, name: str) -> dict:
        """Add a load group."""
        body = {
            "Assign": {
                name: {"NAME": name}
            }
        }
        return self.conn.put("/db/LDGR", body)

    def list_load_groups(self) -> dict:
        return self.conn.get("/db/LDGR")

    def delete_all_load_groups(self) -> dict:
        return self.conn.delete("/db/LDGR/")
