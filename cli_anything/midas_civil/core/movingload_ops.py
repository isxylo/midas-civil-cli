"""Moving load operations."""
from .connection import Connection


class MovingLoadOps:
    def __init__(self, conn: Connection):
        self.conn = conn

    # ------------------------------------------------------------------
    # Moving load code
    # ------------------------------------------------------------------
    def add_code(self, code_name: str) -> dict:
        """Add a moving load code (standard)."""
        body = {
            "Assign": {
                code_name: {"CODE_NAME": code_name}
            }
        }
        return self.conn.put("/db/MVCD", body)

    def list_codes(self) -> dict:
        return self.conn.get("/db/MVCD")

    # ------------------------------------------------------------------
    # Lane definition
    # ------------------------------------------------------------------
    def add_lane(self, name: str, elem_list: list[int],
                 ecc: float = 0.0, wheel_space: float = 1.8) -> dict:
        """Add a moving load lane."""
        body = {
            "Assign": {
                name: {
                    "LANE_NAME": name,
                    "ECC": ecc,
                    "WHEEL_SPACE": wheel_space,
                    "ELEM_LIST": elem_list,
                }
            }
        }
        return self.conn.put("/db/LLAN", body)

    def list_lanes(self) -> dict:
        return self.conn.get("/db/LLAN")

    def delete_all_lanes(self) -> dict:
        return self.conn.delete("/db/LLAN/")

    # ------------------------------------------------------------------
    # Moving load case
    # ------------------------------------------------------------------
    def list_cases(self) -> dict:
        return self.conn.get("/db/MVLD")

    def delete_all_cases(self) -> dict:
        return self.conn.delete("/db/MVLD/")
