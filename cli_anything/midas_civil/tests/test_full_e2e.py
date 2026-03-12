"""E2E tests for cli-anything-midas-civil.

Uses a lightweight mock HTTP server to simulate the MIDAS MAPI,
so no live Civil NX installation is required.

Subprocess tests verify the installed CLI binary via _resolve_cli().
Set CLI_ANYTHING_FORCE_INSTALLED=1 to run subprocess tests against
the installed binary even in a dev environment.
"""
import json
import os
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from cli_anything.midas_civil.midas_civil_cli import cli


# ---------------------------------------------------------------------------
# Mock MAPI server
# ---------------------------------------------------------------------------

MOCK_RESPONSES: dict = {}


class MockMAPIHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that returns pre-configured JSON responses."""

    def log_message(self, *args):
        pass  # suppress output

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _route(self, method: str):
        path = self.path.split("?")[0]
        key = f"{method}:{path}"
        if key in MOCK_RESPONSES:
            self._send_json(MOCK_RESPONSES[key])
        elif path in MOCK_RESPONSES:
            self._send_json(MOCK_RESPONSES[path])
        else:
            # Also try without method prefix
            if path in MOCK_RESPONSES:
                self._send_json(MOCK_RESPONSES[path])
            else:
                self._send_json({"message": ""})

    def do_GET(self):   self._route("GET")
    def do_PUT(self):   self._consume_body(); self._route("PUT")
    def do_POST(self):  self._consume_body(); self._route("POST")
    def do_DELETE(self): self._route("DELETE")

    def _consume_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            self.rfile.read(length)


@pytest.fixture(scope="module")
def mock_server():
    """Start a mock MAPI server for the module and yield its base URL."""
    server = HTTPServer(("127.0.0.1", 0), MockMAPIHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    MOCK_RESPONSES["/civil/config/ver"] = {
        "VER": {"NAME": "Civil NX Test", "USER": "testuser", "COMPANY": "TestCo"}
    }
    MOCK_RESPONSES["GET:/civil/db/NODE"] = {"message": ""}
    MOCK_RESPONSES["PUT:/civil/db/NODE"] = {}
    MOCK_RESPONSES["GET:/civil/db/ELEM"] = {"message": ""}
    MOCK_RESPONSES["PUT:/civil/db/ELEM"] = {}
    MOCK_RESPONSES["GET:/civil/db/MATL"] = {"message": ""}
    MOCK_RESPONSES["PUT:/civil/db/MATL"] = {}
    MOCK_RESPONSES["GET:/civil/db/SECT"] = {"message": ""}
    MOCK_RESPONSES["PUT:/civil/db/SECT"] = {}
    MOCK_RESPONSES["GET:/civil/db/SPRI"] = {"message": ""}
    MOCK_RESPONSES["PUT:/civil/db/SPRI"] = {}
    MOCK_RESPONSES["GET:/civil/db/STLD"] = {"message": ""}
    MOCK_RESPONSES["PUT:/civil/db/STLD"] = {}
    MOCK_RESPONSES["PUT:/civil/db/SELFWEIGHT"] = {}
    MOCK_RESPONSES["PUT:/civil/db/UNIT"] = {}
    MOCK_RESPONSES["POST:/civil/doc/NEW"] = {}
    MOCK_RESPONSES["POST:/civil/doc/ANAL"] = {}
    MOCK_RESPONSES["POST:/civil/post/TABLE"] = {"SS_Table": {"HEAD": ["Node", "FX"], "DATA": [[1, 0.5]]}}
    MOCK_RESPONSES["GET:/civil/ope/PROJECTSTATUS"] = {"PROJECTSTATUS": {"DATA": [], "DATA_LOAD": []}}

    yield f"http://127.0.0.1:{port}/civil"
    server.shutdown()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _invoke(args: list, base_url: str, json_mode: bool = False) -> object:
    runner = CliRunner()
    full_args = ["--key", "testkey", "--url", base_url]
    if json_mode:
        full_args = ["--json"] + full_args
    full_args += args
    return runner.invoke(cli, full_args, catch_exceptions=False)


def _resolve_cli(name: str) -> str:
    """Return path to installed CLI binary, or skip if not found."""
    if os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"):
        path = shutil.which(name)
        if path is None:
            pytest.fail(f"CLI binary '{name}' not found in PATH")
        return path
    path = shutil.which(name)
    if path is None:
        pytest.skip(f"'{name}' not installed; set CLI_ANYTHING_FORCE_INSTALLED=1 to fail")
    return path


# ---------------------------------------------------------------------------
# TestCLIHelp — no server needed
# ---------------------------------------------------------------------------

class TestCLIHelp:
    def _run(self, args):
        return CliRunner().invoke(cli, args, catch_exceptions=False)

    def test_root_help(self):
        result = self._run(["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.output

    def test_model_help(self):
        result = self._run(["model", "--help"])
        assert result.exit_code == 0
        assert "new" in result.output
        assert "analyse" in result.output

    def test_node_help(self):
        result = self._run(["node", "--help"])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "list" in result.output

    def test_result_help(self):
        result = self._run(["result", "--help"])
        assert result.exit_code == 0
        assert "reaction" in result.output

    def test_json_flag_in_help(self):
        result = self._run(["--help"])
        assert "--json" in result.output

    def test_boundary_help(self):
        result = self._run(["boundary", "--help"])
        assert result.exit_code == 0
        assert "support" in result.output

    def test_load_help(self):
        result = self._run(["load", "--help"])
        assert result.exit_code == 0
        assert "case" in result.output

    def test_api_help(self):
        result = self._run(["api", "--help"])
        assert result.exit_code == 0
        assert "get" in result.output


# ---------------------------------------------------------------------------
# TestCLIWithMockServer
# ---------------------------------------------------------------------------

class TestCLIWithMockServer:
    def test_status_ok(self, mock_server):
        result = _invoke(["status"], mock_server)
        assert result.exit_code == 0
        assert "ok" in result.output.lower() or "True" in result.output

    def test_status_json_output(self, mock_server):
        result = _invoke(["status"], mock_server, json_mode=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "ok" in data
        assert data["ok"] is True

    def test_model_new(self, mock_server):
        result = _invoke(["model", "new"], mock_server)
        assert result.exit_code == 0

    def test_model_new_json(self, mock_server):
        result = _invoke(["model", "new"], mock_server, json_mode=True)
        assert result.exit_code == 0
        json.loads(result.output)  # must be valid JSON

    def test_model_units(self, mock_server):
        result = _invoke(["model", "units", "--force", "KN", "--length", "M"], mock_server)
        assert result.exit_code == 0

    def test_model_analyse(self, mock_server):
        result = _invoke(["model", "analyse"], mock_server)
        assert result.exit_code == 0

    def test_node_add(self, mock_server):
        result = _invoke(["node", "add", "--x", "0", "--y", "0", "--z", "0"], mock_server)
        assert result.exit_code == 0

    def test_node_add_json(self, mock_server):
        result = _invoke(["node", "add", "--x", "1", "--y", "2", "--z", "3"],
                         mock_server, json_mode=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "node_id" in data

    def test_node_list(self, mock_server):
        MOCK_RESPONSES["GET:/civil/db/NODE"] = {"NODE": {"1": {"X": 0, "Y": 0, "Z": 0}}}
        result = _invoke(["node", "list"], mock_server)
        assert result.exit_code == 0
        MOCK_RESPONSES["GET:/civil/db/NODE"] = {"message": ""}

    def test_node_list_json(self, mock_server):
        MOCK_RESPONSES["GET:/civil/db/NODE"] = {"NODE": {"1": {"X": 0, "Y": 0, "Z": 0}}}
        result = _invoke(["node", "list"], mock_server, json_mode=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "NODE" in data
        MOCK_RESPONSES["GET:/civil/db/NODE"] = {"message": ""}

    def test_element_beam(self, mock_server):
        result = _invoke(["element", "beam", "--i-node", "1", "--j-node", "2"], mock_server)
        assert result.exit_code == 0

    def test_material_steel(self, mock_server):
        result = _invoke(["material", "steel",
                          "--name", "A36", "--standard", "ASTM(S)", "--grade", "A36"],
                         mock_server)
        assert result.exit_code == 0

    def test_section_db(self, mock_server):
        result = _invoke(["section", "db",
                          "--name", "W8x35", "--shape", "H",
                          "--standard", "AISC", "--dbname", "W8x35"],
                         mock_server)
        assert result.exit_code == 0

    def test_boundary_support(self, mock_server):
        result = _invoke(["boundary", "support", "--nodes", "1,2", "--type", "fix"],
                         mock_server)
        assert result.exit_code == 0

    def test_load_case(self, mock_server):
        result = _invoke(["load", "case", "--name", "SW", "--type", "D"], mock_server)
        assert result.exit_code == 0

    def test_load_self_weight(self, mock_server):
        result = _invoke(["load", "self-weight", "--case", "SW"], mock_server)
        assert result.exit_code == 0

    def test_load_nodal(self, mock_server):
        result = _invoke(["load", "nodal", "--nodes", "1", "--case", "Wind",
                          "--fx", "50.0"], mock_server)
        assert result.exit_code == 0

    def test_load_beam(self, mock_server):
        result = _invoke(["load", "beam", "--elems", "1", "--case", "Floor",
                          "--value", "-5.0"], mock_server)
        assert result.exit_code == 0

    def test_result_reaction_json(self, mock_server):
        result = _invoke(["result", "reaction", "--case", "SW"],
                         mock_server, json_mode=True)
        assert result.exit_code == 0
        json.loads(result.output)

    def test_result_displacement(self, mock_server):
        result = _invoke(["result", "displacement", "--case", "SW"], mock_server)
        assert result.exit_code == 0

    def test_result_beam_force(self, mock_server):
        result = _invoke(["result", "beam-force", "--case", "SW"], mock_server)
        assert result.exit_code == 0

    def test_api_get_passthrough(self, mock_server):
        result = _invoke(["api", "get", "/config/ver"], mock_server)
        assert result.exit_code == 0
        assert "Civil NX Test" in result.output

    def test_api_get_json(self, mock_server):
        result = _invoke(["api", "get", "/config/ver"], mock_server, json_mode=True)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "VER" in data

    def test_api_post_passthrough(self, mock_server):
        result = _invoke(["api", "post", "/doc/NEW", "--body", "{}"], mock_server)
        assert result.exit_code == 0

    def test_model_status(self, mock_server):
        result = _invoke(["model", "status"], mock_server)
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# TestCLISubprocess — tests the installed binary
# ---------------------------------------------------------------------------

class TestCLISubprocess:
    @pytest.fixture(autouse=True)
    def _cli_path(self):
        self.cli_bin = _resolve_cli("cli-anything-midas-civil")

    def _run(self, args: list, env_extra: dict | None = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["MIDAS_MAPI_KEY"] = "testkey"
        env["MIDAS_BASE_URL"] = "https://moa-engineers.midasit.com:443/civil"
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [self.cli_bin] + args,
            capture_output=True, text=True, env=env, timeout=15
        )

    def test_installed_binary_exists(self):
        assert os.path.isfile(self.cli_bin)

    def test_installed_help(self):
        result = self._run(["--help"])
        assert result.returncode == 0
        assert "Usage" in result.stdout

    def test_installed_node_help(self):
        result = self._run(["node", "--help"])
        assert result.returncode == 0
        assert "add" in result.stdout

    def test_installed_model_help(self):
        result = self._run(["model", "--help"])
        assert result.returncode == 0
        assert "new" in result.stdout

    def test_installed_result_help(self):
        result = self._run(["result", "--help"])
        assert result.returncode == 0
        assert "reaction" in result.stdout

    def test_installed_status_json_shape(self):
        """Status with --json must produce parseable JSON (ok may be False without live server)."""
        result = self._run(["--json", "status"])
        # May fail to connect but output must be valid JSON
        try:
            data = json.loads(result.stdout)
            assert "ok" in data
        except json.JSONDecodeError:
            pytest.fail(f"Output was not valid JSON: {result.stdout!r}")
