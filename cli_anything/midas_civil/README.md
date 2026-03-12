# cli-anything-midas-civil

A complete CLI harness for **MIDAS Civil NX** — a structural engineering GUI application.
Exposes the MAPI (MIDAS API) as a stateful command-line tool suitable for agent automation.

## Requirements

- Python 3.10+
- MIDAS Civil NX running with MAPI enabled (`Apps > Connect`)
- MAPI Key (from `Apps > API Settings` in Civil NX)

## Installation

```bash
cd agent-harness
pip install -e .
```

Verify:
```bash
which cli-anything-midas-civil
cli-anything-midas-civil --help
```

## Configuration

Set credentials via environment variables:
```bash
export MIDAS_MAPI_KEY="your-mapi-key-here"
export MIDAS_BASE_URL="https://moa-engineers.midasit.com:443/civil"
```

Or pass per-command:
```bash
cli-anything-midas-civil --key YOUR_KEY --url https://... status
```

Or save to session:
```bash
cli-anything-midas-civil connect --key YOUR_KEY
```

## Usage

### Check connection
```bash
cli-anything-midas-civil status
```

### Model operations
```bash
cli-anything-midas-civil model new
cli-anything-midas-civil model units --force KN --length M
cli-anything-midas-civil model info --project "Bridge Model" --user "Engineer"
cli-anything-midas-civil model analyse
cli-anything-midas-civil model save
cli-anything-midas-civil model save --path D:\\model.mcb
cli-anything-midas-civil model open D:\\existing.mcb
cli-anything-midas-civil model export D:\\model.json
```

### Nodes
```bash
cli-anything-midas-civil node add --x 0 --y 0 --z 0
cli-anything-midas-civil node add --x 0 --y 0 --z 5 --id 2
cli-anything-midas-civil node list
cli-anything-midas-civil node get 1
cli-anything-midas-civil node sync
```

### Elements
```bash
cli-anything-midas-civil element beam --i-node 1 --j-node 2 --mat 1 --sect 1
cli-anything-midas-civil element truss --i-node 1 --j-node 2
cli-anything-midas-civil element list
cli-anything-midas-civil element get 1
```

### Materials
```bash
cli-anything-midas-civil material steel --name A36 --standard "ASTM(S)" --grade A36
cli-anything-midas-civil material concrete --name C30 --standard "ACI" --grade C30
cli-anything-midas-civil material list
```

### Sections
```bash
cli-anything-midas-civil section db --name W8x35 --shape H --standard AISC --dbname W8x35 --id 1
cli-anything-midas-civil section list
```

### Boundary Conditions
```bash
cli-anything-midas-civil boundary support --nodes 1,2,3 --type fix
cli-anything-midas-civil boundary support --nodes 4 --type pin
cli-anything-midas-civil boundary list-supports
```

### Loads
```bash
cli-anything-midas-civil load case --name "Self Weight" --type D
cli-anything-midas-civil load self-weight --case "Self Weight"
cli-anything-midas-civil load nodal --nodes 3,4 --case "Wind" --fx 50.0
cli-anything-midas-civil load beam --elems 1,2 --case "Floor" --value -5.0 --dir GZ
cli-anything-midas-civil load list-cases
```

### Results (after analysis)
```bash
cli-anything-midas-civil result reaction --case "Self Weight"
cli-anything-midas-civil result displacement --case "Self Weight"
cli-anything-midas-civil result beam-force --case "Self Weight"
cli-anything-midas-civil result truss-force --case "Wind"
```

### Raw MAPI passthrough
```bash
cli-anything-midas-civil api get /config/ver
cli-anything-midas-civil api get /db/NODE
cli-anything-midas-civil api post /doc/NEW --body '{}'
cli-anything-midas-civil api put /db/UNIT --body '{"Assign":{"1":{"FORCE":"KN","DIST":"M","HEAT":"BTU","TEMPER":"C"}}}'
```

### JSON output mode (for agent consumption)
```bash
cli-anything-midas-civil --json node list
cli-anything-midas-civil --json result reaction --case "Self Weight"
cli-anything-midas-civil --json model status
```

### Interactive REPL
```bash
cli-anything-midas-civil repl
# midas-civil> model new
# midas-civil> node add --x 0 --y 0 --z 0
# midas-civil> exit
```

## Output Structure

All commands return either:
- **Human format**: key-value pairs, indented for readability
- **JSON format** (`--json`): machine-readable JSON for agent pipelines

## Session State

Credentials are stored in `~/.midas_civil_session.json` after running `connect`.
This allows subsequent commands to reuse credentials without flags.

## Architecture

```
cli-anything-midas-civil (Click CLI)
  └── cli_anything.midas_civil.core
        ├── Connection   — authenticated HTTP to MAPI
        ├── Session      — persistent credential store
        ├── ModelOps     — model-level operations
        ├── NodeOps      — node CRUD
        ├── ElementOps   — element CRUD
        ├── MaterialOps  — material definitions
        ├── SectionOps   — section definitions
        ├── BoundaryOps  — supports and links
        ├── LoadOps      — load cases and loads
        └── ResultOps    — post-analysis result extraction
```
