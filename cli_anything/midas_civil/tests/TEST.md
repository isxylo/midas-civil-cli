# Test Plan — cli-anything-midas-civil

## Overview

This document covers the test plan and results for the `cli-anything-midas-civil` harness.
Tests are split into:

1. **Unit tests** (`test_core.py`) — synthetic data, no external deps, no live Civil NX
2. **E2E tests** (`test_full_e2e.py`) — full pipeline with a mocked HTTP server simulating MAPI
3. **Subprocess tests** (`TestCLISubprocess` in `test_full_e2e.py`) — test the installed CLI binary

---

## Unit Test Plan (`test_core.py`)

### Session
- `test_session_defaults` — new session has empty key, default URL, not connected
- `test_session_save_load` — save state, reload from file, values persist
- `test_session_clear` — clear removes file and resets to defaults
- `test_session_resolve_key_flag` — flag value wins over env var and file
- `test_session_resolve_key_env` — env var wins over session file
- `test_session_resolve_url_default` — returns default URL when nothing set

### Connection
- `test_connection_headers` — headers contain MAPI-Key and Content-Type
- `test_connection_ping_ok` — ping returns ok=True when VER in response
- `test_connection_ping_fail` — ping returns ok=False on connection error
- `test_connection_request_get` — GET request routed correctly
- `test_connection_request_put` — PUT request sends JSON body
- `test_connection_request_post` — POST request sends JSON body
- `test_connection_request_delete` — DELETE request routed correctly

### ModelOps
- `test_model_new` — calls /doc/NEW with correct body
- `test_model_units` — calls /db/UNIT with correct structure
- `test_model_analyse` — calls /doc/ANAL
- `test_model_info_get` — GET /db/PJCF when no args
- `test_model_info_set` — PUT /db/PJCF with provided fields
- `test_model_export_json_valid` — accepts .json extension
- `test_model_export_json_invalid` — returns error for missing extension
- `test_model_max_id` — parses max ID from db response
- `test_model_max_id_empty` — returns 0 for empty model

### NodeOps
- `test_node_add_auto_id` — auto-increments ID from existing nodes
- `test_node_add_explicit_id` — uses provided ID
- `test_node_add_empty_model` — assigns ID=1 when no nodes exist
- `test_node_list` — returns NODE dict from API
- `test_node_get_found` — returns node data for valid ID
- `test_node_get_not_found` — returns error for missing ID
- `test_node_sync_count` — returns correct count
- `test_node_add_many` — sends batch of nodes

### ElementOps
- `test_element_beam_auto_id` — auto-increments from existing elements
- `test_element_beam_body_structure` — correct TYPE/MATL/SECT/NODE
- `test_element_truss_body` — TYPE=TRUSS
- `test_element_plate_three_nodes` — accepts 3-node plate
- `test_element_plate_four_nodes` — accepts 4-node plate
- `test_element_plate_invalid_nodes` — returns error for wrong node count
- `test_element_list` — returns ELEM dict
- `test_element_get_found` — returns element data
- `test_element_get_not_found` — returns error

### MaterialOps
- `test_material_steel_body` — TYPE=STEEL, correct fields
- `test_material_concrete_body` — TYPE=CONC
- `test_material_user_body` — TYPE=USER with elastic params
- `test_material_list` — returns MATL dict
- `test_material_get_found` — returns material data
- `test_material_get_not_found` — returns error

### SectionOps
- `test_section_db_body` — TYPE=DB, correct fields
- `test_section_value_body` — TYPE=VALUE with dims
- `test_section_list` — returns SECT dict
- `test_section_get_found` — returns section data

### BoundaryOps
- `test_boundary_support_fix` — all 6 DOF True
- `test_boundary_support_pin` — translation True, rotation False
- `test_boundary_support_roller` — only Y,Z translation
- `test_boundary_support_custom_string` — TTTTFF parsed correctly
- `test_boundary_support_invalid` — returns error for bad string
- `test_boundary_support_multiple_nodes` — creates one entry per node
- `test_boundary_elastic_link_body` — correct SDx/SDy/SDz/SRx/SRy/SRz
- `test_boundary_rigid_link_body` — correct M_NODE/S_NODE/DOF

### LoadOps
- `test_load_case_body` — NAME and TYPE
- `test_load_self_weight_body` — LCNAME, DIR, FACT
- `test_load_nodal_body` — FX/FY/FZ/MX/MY/MZ per node
- `test_load_nodal_multiple_nodes` — creates one entry per node
- `test_load_beam_body` — DIRECTION, D, P arrays
- `test_load_pressure_body` — PRES, DIR, bPROJ

### ResultOps
- `test_result_reaction_global` — TABLE_TYPE=REACTIONG
- `test_result_reaction_local` — TABLE_TYPE=REACTIONL
- `test_result_displacement_global` — TABLE_TYPE=DISPLACEMENTG
- `test_result_beam_force` — TABLE_TYPE=BEAMFORCE
- `test_result_beam_stress` — TABLE_TYPE=BEAMSTRESS
- `test_result_truss_force` — TABLE_TYPE=TRUSSFORCE
- `test_result_raw_table` — passes through TABLE_TYPE verbatim

---

## E2E Test Plan (`test_full_e2e.py`)

### TestCLIHelp
- `test_root_help` — `--help` exits 0 and shows usage
- `test_model_help` — `model --help` lists sub-commands
- `test_node_help` — `node --help` lists sub-commands
- `test_result_help` — `result --help` lists sub-commands
- `test_json_flag_in_help` — `--json` appears in root help

### TestCLIWithMockServer
- `test_status_ok` — status command against mock MAPI returns ok
- `test_status_json_output` — --json flag produces valid JSON
- `test_model_new` — model new returns response
- `test_node_add` — node add sends PUT /db/NODE
- `test_node_list` — node list returns NODE data
- `test_element_beam` — element beam sends PUT /db/ELEM
- `test_material_steel` — material steel sends PUT /db/MATL
- `test_section_db` — section db sends PUT /db/SECT
- `test_boundary_support` — boundary support sends PUT /db/SPRI
- `test_load_case` — load case sends PUT /db/STLD
- `test_load_self_weight` — self-weight sends PUT /db/SELFWEIGHT
- `test_api_get_passthrough` — api get proxies to endpoint
- `test_api_post_passthrough` — api post sends body
- `test_model_units` — model units sends correct force/length

### TestCLISubprocess
- `test_installed_binary_exists` — `which cli-anything-midas-civil` returns path
- `test_installed_help` — installed binary responds to --help
- `test_installed_status_json` — installed binary --json status returns JSON
- `test_installed_node_help` — installed binary node --help works
- `test_installed_model_help` — installed binary model --help works

---

## Test Results

## Test Results — 2026-03-12

```
============================= test session starts ==============================
platform linux -- Python 3.11.2, pytest-9.0.2, pluggy-1.6.0
rootdir: /root/midas-civil-python/agent-harness
collected 110 items

test_core.py::TestSession::test_session_defaults PASSED
test_core.py::TestSession::test_session_save_load PASSED
test_core.py::TestSession::test_session_clear PASSED
test_core.py::TestSession::test_session_resolve_key_flag PASSED
test_core.py::TestSession::test_session_resolve_key_env PASSED
test_core.py::TestSession::test_session_resolve_url_default PASSED
test_core.py::TestConnection::test_connection_headers PASSED
test_core.py::TestConnection::test_connection_ping_ok PASSED
test_core.py::TestConnection::test_connection_ping_fail PASSED
test_core.py::TestConnection::test_connection_ping_no_ver PASSED
test_core.py::TestConnection::test_connection_get PASSED
test_core.py::TestConnection::test_connection_put PASSED
test_core.py::TestConnection::test_connection_post PASSED
test_core.py::TestConnection::test_connection_delete PASSED
test_core.py::TestModelOps::test_model_new PASSED
test_core.py::TestModelOps::test_model_analyse PASSED
test_core.py::TestModelOps::test_model_units PASSED
test_core.py::TestModelOps::test_model_info_get PASSED
test_core.py::TestModelOps::test_model_info_set PASSED
test_core.py::TestModelOps::test_model_export_json_valid PASSED
test_core.py::TestModelOps::test_model_export_json_invalid_ext PASSED
test_core.py::TestModelOps::test_model_max_id PASSED
test_core.py::TestModelOps::test_model_max_id_empty PASSED
test_core.py::TestNodeOps::test_node_add_auto_id PASSED
test_core.py::TestNodeOps::test_node_add_explicit_id PASSED
test_core.py::TestNodeOps::test_node_add_empty_model PASSED
test_core.py::TestNodeOps::test_node_list PASSED
test_core.py::TestNodeOps::test_node_get_found PASSED
test_core.py::TestNodeOps::test_node_get_not_found PASSED
test_core.py::TestNodeOps::test_node_sync_count PASSED
test_core.py::TestNodeOps::test_node_add_many PASSED
test_core.py::TestElementOps::test_element_beam_auto_id PASSED
test_core.py::TestElementOps::test_element_beam_body_structure PASSED
test_core.py::TestElementOps::test_element_truss_body PASSED
test_core.py::TestElementOps::test_element_plate_three_nodes PASSED
test_core.py::TestElementOps::test_element_plate_four_nodes PASSED
test_core.py::TestElementOps::test_element_plate_invalid_nodes PASSED
test_core.py::TestElementOps::test_element_list PASSED
test_core.py::TestElementOps::test_element_get_found PASSED
test_core.py::TestElementOps::test_element_get_not_found PASSED
test_core.py::TestMaterialOps::test_material_steel_body PASSED
test_core.py::TestMaterialOps::test_material_concrete_body PASSED
test_core.py::TestMaterialOps::test_material_user_body PASSED
test_core.py::TestMaterialOps::test_material_list PASSED
test_core.py::TestMaterialOps::test_material_get_found PASSED
test_core.py::TestMaterialOps::test_material_get_not_found PASSED
test_core.py::TestSectionOps::test_section_db_body PASSED
test_core.py::TestSectionOps::test_section_value_body PASSED
test_core.py::TestSectionOps::test_section_list PASSED
test_core.py::TestSectionOps::test_section_get_found PASSED
test_core.py::TestBoundaryOps::test_boundary_support_fix PASSED
test_core.py::TestBoundaryOps::test_boundary_support_pin PASSED
test_core.py::TestBoundaryOps::test_boundary_support_roller PASSED
test_core.py::TestBoundaryOps::test_boundary_support_custom_string PASSED
test_core.py::TestBoundaryOps::test_boundary_support_invalid PASSED
test_core.py::TestBoundaryOps::test_boundary_support_multiple_nodes PASSED
test_core.py::TestBoundaryOps::test_boundary_elastic_link_body PASSED
test_core.py::TestBoundaryOps::test_boundary_rigid_link_body PASSED
test_core.py::TestLoadOps::test_load_case_body PASSED
test_core.py::TestLoadOps::test_load_self_weight_body PASSED
test_core.py::TestLoadOps::test_load_nodal_body PASSED
test_core.py::TestLoadOps::test_load_nodal_multiple_nodes PASSED
test_core.py::TestLoadOps::test_load_beam_body PASSED
test_core.py::TestLoadOps::test_load_pressure_body PASSED
test_core.py::TestResultOps::test_result_reaction_global PASSED
test_core.py::TestResultOps::test_result_reaction_local PASSED
test_core.py::TestResultOps::test_result_displacement_global PASSED
test_core.py::TestResultOps::test_result_beam_force PASSED
test_core.py::TestResultOps::test_result_beam_stress PASSED
test_core.py::TestResultOps::test_result_truss_force PASSED
test_core.py::TestResultOps::test_result_raw_table PASSED
test_full_e2e.py::TestCLIHelp::test_root_help PASSED
test_full_e2e.py::TestCLIHelp::test_model_help PASSED
test_full_e2e.py::TestCLIHelp::test_node_help PASSED
test_full_e2e.py::TestCLIHelp::test_result_help PASSED
test_full_e2e.py::TestCLIHelp::test_json_flag_in_help PASSED
test_full_e2e.py::TestCLIHelp::test_boundary_help PASSED
test_full_e2e.py::TestCLIHelp::test_load_help PASSED
test_full_e2e.py::TestCLIHelp::test_api_help PASSED
test_full_e2e.py::TestCLIWithMockServer::test_status_ok PASSED
test_full_e2e.py::TestCLIWithMockServer::test_status_json_output PASSED
test_full_e2e.py::TestCLIWithMockServer::test_model_new PASSED
test_full_e2e.py::TestCLIWithMockServer::test_model_new_json PASSED
test_full_e2e.py::TestCLIWithMockServer::test_model_units PASSED
test_full_e2e.py::TestCLIWithMockServer::test_model_analyse PASSED
test_full_e2e.py::TestCLIWithMockServer::test_node_add PASSED
test_full_e2e.py::TestCLIWithMockServer::test_node_add_json PASSED
test_full_e2e.py::TestCLIWithMockServer::test_node_list PASSED
test_full_e2e.py::TestCLIWithMockServer::test_node_list_json PASSED
test_full_e2e.py::TestCLIWithMockServer::test_element_beam PASSED
test_full_e2e.py::TestCLIWithMockServer::test_material_steel PASSED
test_full_e2e.py::TestCLIWithMockServer::test_section_db PASSED
test_full_e2e.py::TestCLIWithMockServer::test_boundary_support PASSED
test_full_e2e.py::TestCLIWithMockServer::test_load_case PASSED
test_full_e2e.py::TestCLIWithMockServer::test_load_self_weight PASSED
test_full_e2e.py::TestCLIWithMockServer::test_load_nodal PASSED
test_full_e2e.py::TestCLIWithMockServer::test_load_beam PASSED
test_full_e2e.py::TestCLIWithMockServer::test_result_reaction_json PASSED
test_full_e2e.py::TestCLIWithMockServer::test_result_displacement PASSED
test_full_e2e.py::TestCLIWithMockServer::test_result_beam_force PASSED
test_full_e2e.py::TestCLIWithMockServer::test_api_get_passthrough PASSED
test_full_e2e.py::TestCLIWithMockServer::test_api_get_json PASSED
test_full_e2e.py::TestCLIWithMockServer::test_api_post_passthrough PASSED
test_full_e2e.py::TestCLIWithMockServer::test_model_status PASSED
test_full_e2e.py::TestCLISubprocess::test_installed_binary_exists PASSED
test_full_e2e.py::TestCLISubprocess::test_installed_help PASSED
test_full_e2e.py::TestCLISubprocess::test_installed_node_help PASSED
test_full_e2e.py::TestCLISubprocess::test_installed_model_help PASSED
test_full_e2e.py::TestCLISubprocess::test_installed_result_help PASSED
test_full_e2e.py::TestCLISubprocess::test_installed_status_json_shape PASSED

============================== 110 passed in 2.47s ==============================
```

**Result: 110/110 passed (100%)**

### Coverage summary
- Unit tests: 71 tests covering all 9 core modules
- E2E tests (mock server): 33 tests covering full CLI pipeline
- Subprocess tests: 6 tests verifying installed binary at `/usr/local/bin/cli-anything-midas-civil`
