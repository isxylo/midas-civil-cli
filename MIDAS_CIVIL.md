# MIDAS Civil NX CLI Harness — SOP

## Overview

MIDAS Civil NX is a structural engineering GUI application. The `midas_civil` Python library wraps its REST API (MAPI), enabling programmatic model creation, analysis, and result extraction. This CLI harness exposes those capabilities as a stateful command-line tool for agent and automation use.

## Architecture

```
Agent / Script
    │
    ▼
cli-anything-midas-civil   (Click CLI + REPL)
    │
    ▼
cli_anything.midas_civil   (Python harness)
    │
    ▼
midas_civil library        (REST wrapper)
    │
    ▼
MIDAS Civil NX GUI (running locally, exposes MAPI HTTP server)
```

## Connection Model

MIDAS Civil NX must be running and the MAPI server enabled (`Apps > Connect` in Civil NX). The harness connects via:

- **MAPI_KEY**: API authentication key (from Civil NX `Apps > API Settings`)
- **MAPI_BASEURL**: HTTP endpoint (e.g. `https://moa-engineers.midasit.com:443/civil`)

These are passed via environment variables or CLI flags:

```bash
export MIDAS_MAPI_KEY="your-key-here"
export MIDAS_BASE_URL="https://moa-engineers.midasit.com:443/civil"
```

## Command Groups

| Group | Description |
|-------|-------------|
| `model` | Model-level ops: new, open, save, units, info, analyse |
| `node` | Node CRUD: add, list, get, delete, sync |
| `element` | Element CRUD: beam, plate, list, get, delete, sync |
| `material` | Material definitions: steel, concrete, list |
| `section` | Section definitions: db, list |
| `boundary` | Boundary conditions: support, elastic-link |
| `load` | Loads: self-weight, nodal, beam, pressure |
| `result` | Result extraction: reaction, displacement, beam-force |
| `group` | Structure/load/boundary groups |
| `api` | Raw MAPI passthrough for advanced use |

## State Model

The harness maintains a **session state file** at `~/.midas_civil_session.json` containing:

- `mapi_key`: current MAPI key
- `base_url`: current base URL
- `connected`: bool
- `last_command`: timestamp + command

## Output Modes

All commands support `--json` flag for machine-readable output:

```bash
cli-anything-midas-civil --json node list
cli-anything-midas-civil --json result reaction --load-case "SW"
```

Human output uses colored tables (colorama + tabulate).

## REPL Mode

```bash
cli-anything-midas-civil repl
```

Enters an interactive shell with command history. All sub-commands available. Type `exit` or `quit` to leave.

## Example Workflow

```bash
# Set connection
export MIDAS_MAPI_KEY="abc123"
export MIDAS_BASE_URL="https://moa-engineers.midasit.com:443/civil"

# Create a new model
cli-anything-midas-civil model new
cli-anything-midas-civil model units --force KN --length M

# Add geometry
cli-anything-midas-civil node add --x 0 --y 0 --z 0
cli-anything-midas-civil node add --x 0 --y 0 --z 5

# Add material and section
cli-anything-midas-civil material steel --name "A36" --standard "ASTM(S)" --grade "A36"
cli-anything-midas-civil section db --name "W8x35" --shape H --standard AISC --dbname "W8x35" --id 1

# Add support
cli-anything-midas-civil boundary support --nodes 1 --type fix

# Run analysis
cli-anything-midas-civil model analyse

# Get results
cli-anything-midas-civil result reaction --load-case "Self Weight"
```

## Key API Endpoints (MAPI)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/db/NODE` | GET/PUT/DELETE | Nodes |
| `/db/ELEM` | GET/PUT/DELETE | Elements |
| `/db/MATL` | GET/PUT/DELETE | Materials |
| `/db/SECT` | GET/PUT/DELETE | Sections |
| `/db/SPRI` | GET/PUT/DELETE | Supports |
| `/db/UNIT` | GET/PUT | Units |
| `/doc/NEW` | POST | New model |
| `/doc/OPEN` | POST | Open model |
| `/doc/SAVE` | POST | Save model |
| `/doc/ANAL` | POST | Run analysis |
| `/config/ver` | GET | Version/connection check |
| `/ope/PROJECTSTATUS` | GET | Project status + max IDs |

## Notes

- MIDAS Civil NX must be running on Windows. The harness can run on any OS that can reach the MAPI HTTP endpoint.
- The library uses class-level state (e.g. `Node.nodes`, `Element.elements`) as a local buffer before calling `Model.create()` to push to Civil NX.
- For result extraction, the model must first be analysed (`Model.analyse()`).
- The harness bypasses Windows Registry auto-detection and accepts credentials via env vars or CLI flags.
