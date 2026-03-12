"""Unit tests for cli_anything.midas_civil core modules.
No live Civil NX required — all HTTP calls are mocked.
"""
from unittest.mock import MagicMock, patch
import pytest


def _mock_conn():
    from cli_anything.midas_civil.core.connection import Connection
    conn = MagicMock(spec=Connection)
    conn.get.return_value = {"message": ""}
    conn.put.return_value = {}
    conn.post.return_value = {}
    conn.delete.return_value = {}
    return conn


# ===========================================================================
# Session
# ===========================================================================

class TestSession:
    def test_session_defaults(self, tmp_path):
        from cli_anything.midas_civil.core.session import Session, _DEFAULTS
        sess = Session(tmp_path / "sess.json")
        assert sess.mapi_key == ""
        assert sess.base_url == _DEFAULTS["base_url"]
        assert sess.connected is False

    def test_session_save_load(self, tmp_path):
        from cli_anything.midas_civil.core.session import Session
        f = tmp_path / "sess.json"
        sess = Session(f)
        sess.mapi_key = "testkey123"
        sess.base_url = "https://example.com/civil"
        sess.connected = True
        sess.save()
        sess2 = Session(f)
        assert sess2.mapi_key == "testkey123"
        assert sess2.connected is True

    def test_session_clear(self, tmp_path):
        from cli_anything.midas_civil.core.session import Session
        f = tmp_path / "sess.json"
        sess = Session(f)
        sess.mapi_key = "somekey"
        sess.save()
        sess.clear()
        assert sess.mapi_key == ""
        assert not f.exists()

    def test_session_resolve_key_flag(self, monkeypatch):
        from cli_anything.midas_civil.core.session import Session
        monkeypatch.delenv("MIDAS_MAPI_KEY", raising=False)
        assert Session.resolve_key("flag_key") == "flag_key"

    def test_session_resolve_key_env(self, monkeypatch):
        from cli_anything.midas_civil.core.session import Session
        monkeypatch.setenv("MIDAS_MAPI_KEY", "env_key")
        assert Session.resolve_key(None) == "env_key"

    def test_session_resolve_url_default(self, monkeypatch, tmp_path):
        from cli_anything.midas_civil.core.session import Session, _DEFAULTS
        monkeypatch.delenv("MIDAS_BASE_URL", raising=False)
        with patch("cli_anything.midas_civil.core.session.SESSION_FILE", tmp_path / "x.json"):
            result = Session.resolve_url(None)
        assert result == _DEFAULTS["base_url"]


# ===========================================================================
# Connection
# ===========================================================================

class TestConnection:
    def test_connection_headers(self):
        from cli_anything.midas_civil.core.connection import Connection
        conn = Connection(mapi_key="mykey", base_url="https://example.com/civil")
        h = conn._headers()
        assert h["MAPI-Key"] == "mykey"
        assert h["Content-Type"] == "application/json"

    def test_connection_ping_ok(self):
        from cli_anything.midas_civil.core.connection import Connection
        conn = Connection(mapi_key="k", base_url="https://x.com/civil")
        with patch.object(conn, "request",
                          return_value={"VER": {"NAME": "CivilNX", "USER": "u", "COMPANY": "c"}}):
            result = conn.ping()
        assert result["ok"] is True

    def test_connection_ping_fail(self):
        import requests
        from cli_anything.midas_civil.core.connection import Connection
        conn = Connection(mapi_key="k", base_url="https://x.com/civil")
        with patch.object(conn, "request",
                          side_effect=requests.exceptions.ConnectionError("refused")):
            result = conn.ping()
        assert result["ok"] is False

    def test_connection_ping_no_ver(self):
        from cli_anything.midas_civil.core.connection import Connection
        conn = Connection(mapi_key="k", base_url="https://x.com/civil")
        with patch.object(conn, "request", return_value={"message": "not found"}):
            result = conn.ping()
        assert result["ok"] is False

    @patch("cli_anything.midas_civil.core.connection.requests.request")
    def test_connection_get(self, mock_req):
        from cli_anything.midas_civil.core.connection import Connection
        mock_req.return_value.json.return_value = {"NODE": {}}
        conn = Connection(mapi_key="k", base_url="https://x.com/civil")
        result = conn.get("/db/NODE")
        assert result == {"NODE": {}}
        assert mock_req.call_args.kwargs["method"] == "GET"

    @patch("cli_anything.midas_civil.core.connection.requests.request")
    def test_connection_put(self, mock_req):
        from cli_anything.midas_civil.core.connection import Connection
        mock_req.return_value.json.return_value = {}
        conn = Connection(mapi_key="k", base_url="https://x.com/civil")
        conn.put("/db/NODE", {"Assign": {}})
        assert mock_req.call_args.kwargs["method"] == "PUT"
        assert mock_req.call_args.kwargs["json"] == {"Assign": {}}

    @patch("cli_anything.midas_civil.core.connection.requests.request")
    def test_connection_post(self, mock_req):
        from cli_anything.midas_civil.core.connection import Connection
        mock_req.return_value.json.return_value = {}
        conn = Connection(mapi_key="k", base_url="https://x.com/civil")
        conn.post("/doc/NEW", {"Argument": {}})
        assert mock_req.call_args.kwargs["method"] == "POST"

    @patch("cli_anything.midas_civil.core.connection.requests.request")
    def test_connection_delete(self, mock_req):
        from cli_anything.midas_civil.core.connection import Connection
        mock_req.return_value.json.return_value = {}
        conn = Connection(mapi_key="k", base_url="https://x.com/civil")
        conn.delete("/db/NODE/")
        assert mock_req.call_args.kwargs["method"] == "DELETE"


# ===========================================================================
# ModelOps
# ===========================================================================

class TestModelOps:
    def test_model_new(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        ModelOps(conn).new()
        conn.post.assert_called_once_with("/doc/NEW", {"Argument": {}})

    def test_model_analyse(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        ModelOps(conn).analyse()
        conn.post.assert_called_once_with("/doc/ANAL", {"Assign": {}})

    def test_model_units(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        ModelOps(conn).units("KN", "M", "BTU", "C")
        body = conn.put.call_args[0][1]
        assert body["Assign"]["1"]["FORCE"] == "KN"
        assert body["Assign"]["1"]["DIST"] == "M"

    def test_model_info_get(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        ModelOps(conn).info()
        conn.get.assert_called_once_with("/db/PJCF")

    def test_model_info_set(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        ModelOps(conn).info(project_name="MyBridge", user="Eng")
        body = conn.put.call_args[0][1]
        assert body["Assign"]["1"]["PROJECT"] == "MyBridge"
        assert body["Assign"]["1"]["USER"] == "Eng"

    def test_model_export_json_valid(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        ModelOps(conn).export_json("C:\\model.json")
        conn.post.assert_called_once_with("/doc/EXPORT", {"Argument": "C:\\model.json"})

    def test_model_export_json_invalid_ext(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        result = ModelOps(conn).export_json("model.txt")
        assert "error" in result
        conn.post.assert_not_called()

    def test_model_max_id(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        conn.get.return_value = {"NODE": {"1": {}, "5": {}, "3": {}}}
        result = ModelOps(conn).max_id("NODE")
        assert result["max_id"] == 5

    def test_model_max_id_empty(self):
        from cli_anything.midas_civil.core.model_ops import ModelOps
        conn = _mock_conn()
        result = ModelOps(conn).max_id("NODE")
        assert result["max_id"] == 0


# ===========================================================================
# NodeOps
# ===========================================================================

class TestNodeOps:
    def test_node_add_auto_id(self):
        from cli_anything.midas_civil.core.node_ops import NodeOps
        conn = _mock_conn()
        conn.get.return_value = {"NODE": {"1": {}, "3": {}}}
        conn.put.return_value = {}
        result = NodeOps(conn).add(5.0, 0.0, 0.0)
        assert result["node_id"] == 4

    def test_node_add_explicit_id(self):
        from cli_anything.midas_civil.core.node_ops import NodeOps
        conn = _mock_conn()
        conn.get.return_value = {"NODE": {}}
        conn.put.return_value = {}
        result = NodeOps(conn).add(1.0, 2.0, 3.0, node_id=99)
        assert result["node_id"] == 99
        body = conn.put.call_args[0][1]
        assert body["Assign"]["99"] == {"X": 1.0, "Y": 2.0, "Z": 3.0}

    def test_node_add_empty_model(self):
        from cli_anything.midas_civil.core.node_ops import NodeOps
        conn = _mock_conn()
        conn.put.return_value = {}
        result = NodeOps(conn).add(0.0, 0.0, 0.0)
        assert result["node_id"] == 1

    def test_node_list(self):
        from cli_anything.midas_civil.core.node_ops import NodeOps
        conn = _mock_conn()
        conn.get.return_value = {"NODE": {"1": {"X": 0, "Y": 0, "Z": 0}}}
        result = NodeOps(conn).list()
        assert "NODE" in result

    def test_node_get_found(self):
        from cli_anything.midas_civil.core.node_ops import NodeOps
        conn = _mock_conn()
        conn.get.return_value = {"NODE": {"7": {"X": 1.0, "Y": 2.0, "Z": 3.0}}}
        result = NodeOps(conn).get(7)
        assert result["node_id"] == 7
        assert result["data"]["X"] == 1.0

    def test_node_get_not_found(self):
        from cli_anything.midas_civil.core.node_ops import NodeOps
        conn = _mock_conn()
        conn.get.return_value = {"NODE": {}}
        result = NodeOps(conn).get(99)
        assert "error" in result

    def test_node_sync_count(self):
        from cli_anything.midas_civil.core.node_ops import NodeOps
        conn = _mock_conn()
        conn.get.return_value = {"NODE": {"1": {}, "2": {}, "3": {}}}
        result = NodeOps(conn).sync()
        assert result["count"] == 3

    def test_node_add_many(self):
        from cli_anything.midas_civil.core.node_ops import NodeOps
        conn = _mock_conn()
        conn.put.return_value = {}
        nodes = [{"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 0, "z": 0}]
        NodeOps(conn).add_many(nodes)
        body = conn.put.call_args[0][1]
        assert len(body["Assign"]) == 2


# ===========================================================================
# ElementOps
# ===========================================================================

class TestElementOps:
    def _ce(self):
        conn = _mock_conn()
        conn.put.return_value = {}
        return conn

    def test_element_beam_auto_id(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = _mock_conn()
        conn.get.return_value = {"ELEM": {"2": {}, "5": {}}}
        conn.put.return_value = {}
        result = ElementOps(conn).add_beam(1, 2)
        assert result["elem_id"] == 6

    def test_element_beam_body_structure(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = self._ce()
        ElementOps(conn).add_beam(1, 2, mat_id=2, sect_id=3, elem_id=10)
        body = conn.put.call_args[0][1]
        elem = body["Assign"]["10"]
        assert elem["TYPE"] == "BEAM"
        assert elem["MATL"] == 2
        assert elem["SECT"] == 3
        assert elem["NODE"] == [1, 2]

    def test_element_truss_body(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = self._ce()
        ElementOps(conn).add_truss(1, 2, elem_id=1)
        body = conn.put.call_args[0][1]
        assert body["Assign"]["1"]["TYPE"] == "TRUSS"

    def test_element_plate_three_nodes(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = self._ce()
        result = ElementOps(conn).add_plate([1, 2, 3], elem_id=1)
        assert "error" not in result

    def test_element_plate_four_nodes(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = self._ce()
        ElementOps(conn).add_plate([1, 2, 3, 4], elem_id=1)
        body = conn.put.call_args[0][1]
        assert body["Assign"]["1"]["TYPE"] == "PLATE"

    def test_element_plate_invalid_nodes(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = self._ce()
        result = ElementOps(conn).add_plate([1, 2])
        assert "error" in result
        conn.put.assert_not_called()

    def test_element_list(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = _mock_conn()
        conn.get.return_value = {"ELEM": {"1": {"TYPE": "BEAM"}}}
        result = ElementOps(conn).list()
        assert "ELEM" in result

    def test_element_get_found(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = _mock_conn()
        conn.get.return_value = {"ELEM": {"3": {"TYPE": "BEAM", "NODE": [1, 2]}}}
        result = ElementOps(conn).get(3)
        assert result["elem_id"] == 3

    def test_element_get_not_found(self):
        from cli_anything.midas_civil.core.element_ops import ElementOps
        conn = _mock_conn()
        conn.get.return_value = {"ELEM": {}}
        result = ElementOps(conn).get(99)
        assert "error" in result


# ===========================================================================
# MaterialOps
# ===========================================================================

class TestMaterialOps:
    def _ce(self):
        conn = _mock_conn()
        conn.put.return_value = {}
        return conn

    def test_material_steel_body(self):
        from cli_anything.midas_civil.core.material_ops import MaterialOps
        conn = self._ce()
        result = MaterialOps(conn).add_steel("A36", "ASTM(S)", "A36", mat_id=1)
        body = conn.put.call_args[0][1]
        assert body["Assign"]["1"]["TYPE"] == "STEEL"
        assert result["mat_id"] == 1

    def test_material_concrete_body(self):
        from cli_anything.midas_civil.core.material_ops import MaterialOps
        conn = self._ce()
        MaterialOps(conn).add_concrete("C30", "ACI", "C30", mat_id=1)
        body = conn.put.call_args[0][1]
        assert body["Assign"]["1"]["TYPE"] == "CONC"

    def test_material_user_body(self):
        from cli_anything.midas_civil.core.material_ops import MaterialOps
        conn = self._ce()
        MaterialOps(conn).add_user("MyMat", 200e6, 0.3, 7850.0, mat_id=1)
        body = conn.put.call_args[0][1]
        assert body["Assign"]["1"]["TYPE"] == "USER"
        assert body["Assign"]["1"]["ELAST"] == 200e6

    def test_material_list(self):
        from cli_anything.midas_civil.core.material_ops import MaterialOps
        conn = _mock_conn()
        conn.get.return_value = {"MATL": {"1": {"TYPE": "STEEL"}}}
        result = MaterialOps(conn).list()
        assert "MATL" in result

    def test_material_get_found(self):
        from cli_anything.midas_civil.core.material_ops import MaterialOps
        conn = _mock_conn()
        conn.get.return_value = {"MATL": {"1": {"TYPE": "STEEL", "NAME": "A36"}}}
        result = MaterialOps(conn).get(1)
        assert result["mat_id"] == 1
        assert result["data"]["NAME"] == "A36"

    def test_material_get_not_found(self):
        from cli_anything.midas_civil.core.material_ops import MaterialOps
        conn = _mock_conn()
        conn.get.return_value = {"MATL": {}}
        result = MaterialOps(conn).get(99)
        assert "error" in result


# ===========================================================================
# SectionOps
# ===========================================================================

class TestSectionOps:
    def _conn_empty(self):
        conn = _mock_conn()
        conn.get.return_value = {"message": ""}
        conn.put.return_value = {}
        return conn

    def test_section_db_body(self):
        from cli_anything.midas_civil.core.section_ops import SectionOps
        conn = self._conn_empty()
        result = SectionOps(conn).add_db("W8x35", "H", "AISC", "W8x35", sect_id=1)
        body = conn.put.call_args[0][1]
        assert body["Assign"]["1"]["TYPE"] == "DB"
        assert body["Assign"]["1"]["DBNAME"] == "W8x35"
        assert result["sect_id"] == 1

    def test_section_value_body(self):
        from cli_anything.midas_civil.core.section_ops import SectionOps
        conn = self._conn_empty()
        SectionOps(conn).add_value("Box", "BOX", [0.3, 0.5, 0.02, 0.02], sect_id=2)
        body = conn.put.call_args[0][1]
        assert body["Assign"]["2"]["TYPE"] == "VALUE"
        assert body["Assign"]["2"]["SECT_COND"] == [0.3, 0.5, 0.02, 0.02]

    def test_section_list(self):
        from cli_anything.midas_civil.core.section_ops import SectionOps
        conn = _mock_conn()
        conn.get.return_value = {"SECT": {"1": {"TYPE": "DB"}}}
        result = SectionOps(conn).list()
        assert "SECT" in result

    def test_section_get_found(self):
        from cli_anything.midas_civil.core.section_ops import SectionOps
        conn = _mock_conn()
        conn.get.return_value = {"SECT": {"1": {"TYPE": "DB", "NAME": "W8x35"}}}
        result = SectionOps(conn).get(1)
        assert result["sect_id"] == 1


# ===========================================================================
# BoundaryOps
# ===========================================================================

class TestBoundaryOps:
    def _conn_empty(self):
        conn = _mock_conn()
        conn.get.return_value = {"message": ""}
        conn.put.return_value = {}
        return conn

    def test_boundary_support_fix(self):
        from cli_anything.midas_civil.core.boundary_ops import BoundaryOps
        conn = self._conn_empty()
        BoundaryOps(conn).add_support([1], "fix")
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["DX"] is True
        assert entry["RZ"] is True

    def test_boundary_support_pin(self):
        from cli_anything.midas_civil.core.boundary_ops import BoundaryOps
        conn = self._conn_empty()
        BoundaryOps(conn).add_support([1], "pin")
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["DX"] is True
        assert entry["RX"] is False

    def test_boundary_support_roller(self):
        from cli_anything.midas_civil.core.boundary_ops import BoundaryOps
        conn = self._conn_empty()
        BoundaryOps(conn).add_support([1], "roller")
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["DX"] is False
        assert entry["DY"] is True

    def test_boundary_support_custom_string(self):
        from cli_anything.midas_civil.core.boundary_ops import BoundaryOps
        conn = self._conn_empty()
        BoundaryOps(conn).add_support([1], "TTTTFF")
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["DX"] is True
        assert entry["RY"] is False
        assert entry["RZ"] is False

    def test_boundary_support_invalid(self):
        from cli_anything.midas_civil.core.boundary_ops import BoundaryOps
        conn = self._conn_empty()
        result = BoundaryOps(conn).add_support([1], "badstring")
        assert "error" in result
        conn.put.assert_not_called()

    def test_boundary_support_multiple_nodes(self):
        from cli_anything.midas_civil.core.boundary_ops import BoundaryOps
        conn = self._conn_empty()
        BoundaryOps(conn).add_support([1, 2, 3], "fix")
        body = conn.put.call_args[0][1]
        assert len(body["Assign"]) == 3

    def test_boundary_elastic_link_body(self):
        from cli_anything.midas_civil.core.boundary_ops import BoundaryOps
        conn = self._conn_empty()
        BoundaryOps(conn).add_elastic_link(1, 2, sdx=1000.0, sdy=2000.0)
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["I_NODE"] == 1
        assert entry["J_NODE"] == 2
        assert entry["SDx"] == 1000.0

    def test_boundary_rigid_link_body(self):
        from cli_anything.midas_civil.core.boundary_ops import BoundaryOps
        conn = self._conn_empty()
        BoundaryOps(conn).add_rigid_link(1, [2, 3, 4], dof="123456")
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["M_NODE"] == 1
        assert entry["S_NODE"] == [2, 3, 4]
        assert entry["DOF"] == "123456"


# ===========================================================================
# LoadOps
# ===========================================================================

class TestLoadOps:
    def _conn_empty(self):
        conn = _mock_conn()
        conn.get.return_value = {"message": ""}
        conn.put.return_value = {}
        return conn

    def test_load_case_body(self):
        from cli_anything.midas_civil.core.load_ops import LoadOps
        conn = self._conn_empty()
        LoadOps(conn).add_load_case("SW", "D")
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["NAME"] == "SW"
        assert entry["TYPE"] == "D"

    def test_load_self_weight_body(self):
        from cli_anything.midas_civil.core.load_ops import LoadOps
        conn = self._conn_empty()
        LoadOps(conn).add_self_weight("SW", "Z", -1.0)
        body = conn.put.call_args[0][1]
        entry = body["Assign"]["1"]
        assert entry["LCNAME"] == "SW"
        assert entry["DIR"] == "Z"
        assert entry["FACT"] == -1.0

    def test_load_nodal_body(self):
        from cli_anything.midas_civil.core.load_ops import LoadOps
        conn = self._conn_empty()
        LoadOps(conn).add_nodal_load([5], "Wind", fx=100.0)
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["NODE"] == 5
        assert entry["FX"] == 100.0
        assert entry["LCNAME"] == "Wind"

    def test_load_nodal_multiple_nodes(self):
        from cli_anything.midas_civil.core.load_ops import LoadOps
        conn = self._conn_empty()
        LoadOps(conn).add_nodal_load([1, 2, 3], "Wind", fz=-50.0)
        body = conn.put.call_args[0][1]
        assert len(body["Assign"]) == 3

    def test_load_beam_body(self):
        from cli_anything.midas_civil.core.load_ops import LoadOps
        conn = self._conn_empty()
        LoadOps(conn).add_beam_load([10], "Floor", value=-5.0, direction="GZ")
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["ELEMENT"] == 10
        assert entry["DIRECTION"] == "GZ"
        assert entry["P"] == [-5.0, -5.0]

    def test_load_pressure_body(self):
        from cli_anything.midas_civil.core.load_ops import LoadOps
        conn = self._conn_empty()
        LoadOps(conn).add_pressure_load([7], "Hydro", pressure=10.0, direction="GZ")
        body = conn.put.call_args[0][1]
        entry = list(body["Assign"].values())[0]
        assert entry["ELEM"] == 7
        assert entry["PRES"] == 10.0
        assert entry["bPROJ"] is False


# ===========================================================================
# ResultOps
# ===========================================================================

class TestResultOps:
    def _conn(self):
        conn = _mock_conn()
        conn.post.return_value = {"SS_Table": {"HEAD": [], "DATA": []}}
        return conn

    def test_result_reaction_global(self):
        from cli_anything.midas_civil.core.result_ops import ResultOps
        conn = self._conn()
        ResultOps(conn).reaction("SW", "Global")
        body = conn.post.call_args[0][1]
        assert body["Argument"]["TABLE_TYPE"] == "REACTIONG"
        assert body["Argument"]["LOAD_CASE"] == "SW"

    def test_result_reaction_local(self):
        from cli_anything.midas_civil.core.result_ops import ResultOps
        conn = self._conn()
        ResultOps(conn).reaction("SW", "Local")
        body = conn.post.call_args[0][1]
        assert body["Argument"]["TABLE_TYPE"] == "REACTIONL"

    def test_result_displacement_global(self):
        from cli_anything.midas_civil.core.result_ops import ResultOps
        conn = self._conn()
        ResultOps(conn).displacement("SW")
        body = conn.post.call_args[0][1]
        assert body["Argument"]["TABLE_TYPE"] == "DISPLACEMENTG"

    def test_result_beam_force(self):
        from cli_anything.midas_civil.core.result_ops import ResultOps
        conn = self._conn()
        ResultOps(conn).beam_force("LC1")
        body = conn.post.call_args[0][1]
        assert body["Argument"]["TABLE_TYPE"] == "BEAMFORCE"

    def test_result_beam_stress(self):
        from cli_anything.midas_civil.core.result_ops import ResultOps
        conn = self._conn()
        ResultOps(conn).beam_stress("LC1")
        body = conn.post.call_args[0][1]
        assert body["Argument"]["TABLE_TYPE"] == "BEAMSTRESS"

    def test_result_truss_force(self):
        from cli_anything.midas_civil.core.result_ops import ResultOps
        conn = self._conn()
        ResultOps(conn).truss_force("LC1")
        body = conn.post.call_args[0][1]
        assert body["Argument"]["TABLE_TYPE"] == "TRUSSFORCE"

    def test_result_raw_table(self):
        from cli_anything.midas_civil.core.result_ops import ResultOps
        conn = self._conn()
        ResultOps(conn).raw_table("PLATEFORCE", "Wind")
        body = conn.post.call_args[0][1]
        assert body["Argument"]["TABLE_TYPE"] == "PLATEFORCE"
        assert body["Argument"]["LOAD_CASE"] == "Wind"
