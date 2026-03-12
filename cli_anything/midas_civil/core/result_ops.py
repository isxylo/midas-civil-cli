"""Result extraction operations."""
from .connection import Connection


class ResultOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    def _ss_table(self, body: dict) -> dict:
        """POST to /post/TABLE and return parsed result."""
        return self.conn.post("/post/TABLE", body)

    # ------------------------------------------------------------------
    # Reactions
    # ------------------------------------------------------------------
    def reaction(self, load_case: str, result_type: str = "Global") -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "REACTIONG" if result_type == "Global" else "REACTIONL",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    # ------------------------------------------------------------------
    # Displacements
    # ------------------------------------------------------------------
    def displacement(self, load_case: str, result_type: str = "Global") -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "DISPLACEMENTG" if result_type == "Global" else "DISPLACEMENTL",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    # ------------------------------------------------------------------
    # Beam forces
    # ------------------------------------------------------------------
    def beam_force(self, load_case: str) -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "BEAMFORCE",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    def beam_stress(self, load_case: str) -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "BEAMSTRESS",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    # ------------------------------------------------------------------
    # Truss forces
    # ------------------------------------------------------------------
    def truss_force(self, load_case: str) -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "TRUSSFORCE",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    # ------------------------------------------------------------------
    # Plate forces
    # ------------------------------------------------------------------
    def plate_force(self, load_case: str, result_type: str = "Global") -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "PLATEFORCE" if result_type == "Global" else "PLATEFORCL",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    def truss_stress(self, load_case: str) -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "TRUSSSTRESS",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    def beam_force_vbm(self, load_case: str) -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "BEAMFORCE_VBM",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    def beam_stress_psc(self, load_case: str) -> dict:
        body = {
            "Argument": {
                "TABLE_TYPE": "BEAMSTRESS_PSC",
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        return self._ss_table(body)

    # ------------------------------------------------------------------
    # Generic raw table query
    # ------------------------------------------------------------------
    def raw_table(self, table_type: str, load_case: str, extra: dict | None = None) -> dict:
        body: dict = {
            "Argument": {
                "TABLE_TYPE": table_type,
                "LOAD_CASE": load_case,
                "OPT_CS": 0,
            }
        }
        if extra:
            body["Argument"].update(extra)
        return self._ss_table(body)

    def list_load_cases(self) -> dict:
        """Return available load cases (post-analysis)."""
        return self.conn.get("/db/STLD")
