"""Node CRUD operations."""
from .connection import Connection


class NodeOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def add(self, x: float, y: float, z: float, node_id: int | None = None) -> dict:
        """Add or replace a single node."""
        # Determine ID: use provided or get max+1
        if node_id is None:
            existing = self.conn.get("/db/NODE")
            if existing and "NODE" in existing and existing["NODE"]:
                node_id = max(int(k) for k in existing["NODE"].keys()) + 1
            else:
                node_id = 1
        body = {"Assign": {str(node_id): {"X": x, "Y": y, "Z": z}}}
        resp = self.conn.put("/db/NODE", body)
        resp["node_id"] = node_id
        return resp

    def add_many(self, nodes: list[dict]) -> dict:
        """Add multiple nodes at once.
        nodes: list of {x, y, z} or {id, x, y, z} dicts.
        """
        existing = self.conn.get("/db/NODE")
        if existing and "NODE" in existing and existing["NODE"]:
            next_id = max(int(k) for k in existing["NODE"].keys()) + 1
        else:
            next_id = 1

        assign: dict = {}
        for n in nodes:
            nid = n.get("id") or next_id
            assign[str(nid)] = {"X": float(n["x"]), "Y": float(n["y"]), "Z": float(n["z"])}
            if not n.get("id"):
                next_id += 1
        return self.conn.put("/db/NODE", {"Assign": assign})

    def list(self) -> dict:
        """Return all nodes from Civil NX."""
        return self.conn.get("/db/NODE")

    def get(self, node_id: int) -> dict:
        """Return a single node by ID."""
        resp = self.conn.get("/db/NODE")
        if "NODE" in resp and str(node_id) in resp["NODE"]:
            return {"node_id": node_id, "data": resp["NODE"][str(node_id)]}
        return {"error": f"Node {node_id} not found"}

    def delete_all(self) -> dict:
        return self.conn.delete("/db/NODE/")

    def sync(self) -> dict:
        """Return a summary of all nodes."""
        resp = self.list()
        if "NODE" in resp:
            count = len(resp["NODE"])
            return {"count": count, "nodes": resp["NODE"]}
        return {"count": 0, "nodes": {}}
