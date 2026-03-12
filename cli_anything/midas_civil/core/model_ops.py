"""Model-level operations: new, open, save, units, info, analyse, export."""
from .connection import Connection


class ModelOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def new(self) -> dict:
        return self.conn.post("/doc/NEW", {"Argument": {}})

    def open(self, path: str) -> dict:
        if not (path.endswith(".mcb") or path.endswith(".mcbz")):
            return {"error": "File must have .mcb or .mcbz extension"}
        return self.conn.post("/doc/OPEN", {"Argument": path})

    def save(self) -> dict:
        return self.conn.post("/doc/SAVE", {"Argument": {}})

    def save_as(self, path: str) -> dict:
        if not (path.endswith(".mcb") or path.endswith(".mcbz")):
            return {"error": "File must have .mcb or .mcbz extension"}
        return self.conn.post("/doc/SAVEAS", {"Argument": path})

    def analyse(self) -> dict:
        return self.conn.post("/doc/ANAL", {"Assign": {}})

    def info(self, project_name: str = "", revision: str = "",
             user: str = "", title: str = "", comment: str = "") -> dict:
        if not any([project_name, revision, user, title, comment]):
            return self.conn.get("/db/PJCF")
        body: dict = {"Assign": {"1": {}}}
        if project_name:
            body["Assign"]["1"]["PROJECT"] = project_name
        if revision:
            body["Assign"]["1"]["REVISION"] = revision
        if user:
            body["Assign"]["1"]["USER"] = user
        if title:
            body["Assign"]["1"]["TITLE"] = title
        if comment:
            body["Assign"]["1"]["COMMENT"] = comment
        return self.conn.put("/db/PJCF", body)

    def units(self, force: str = "KN", length: str = "M",
              heat: str = "BTU", temp: str = "C") -> dict:
        body = {
            "Assign": {
                "1": {
                    "FORCE": force,
                    "DIST": length,
                    "HEAT": heat,
                    "TEMPER": temp,
                }
            }
        }
        return self.conn.put("/db/UNIT", body)

    def get_units(self) -> dict:
        return self.conn.get("/db/UNIT")

    def export_json(self, path: str) -> dict:
        if not path.endswith(".json"):
            return {"error": "File must have .json extension"}
        return self.conn.post("/doc/EXPORT", {"Argument": path})

    def export_mct(self, path: str) -> dict:
        if not path.endswith(".mct"):
            return {"error": "File must have .mct extension"}
        return self.conn.post("/doc/EXPORTMXT", {"Argument": path})

    def import_json(self, path: str) -> dict:
        if not path.endswith(".json"):
            return {"error": "File must have .json extension"}
        return self.conn.post("/doc/IMPORT", {"Argument": path})

    def status(self) -> dict:
        return self.conn.get("/ope/PROJECTSTATUS")

    def max_id(self, db_name: str) -> dict:
        resp = self.conn.get(f"/db/{db_name}")
        if resp == {"message": ""} or db_name not in resp:
            return {"max_id": 0}
        try:
            max_id = max(int(k) for k in resp[db_name].keys())
            return {"max_id": max_id}
        except Exception as exc:
            return {"error": str(exc)}
