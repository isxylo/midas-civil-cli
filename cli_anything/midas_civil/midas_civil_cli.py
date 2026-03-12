"""cli-anything-midas-civil — CLI harness for MIDAS Civil NX.

Usage:
    cli-anything-midas-civil [--json] [--key KEY] [--url URL] <command> [args]
    cli-anything-midas-civil repl
"""
import sys
import json as _json

import click

from .core.session import Session
from .core.connection import Connection
from .core.model_ops import ModelOps
from .core.node_ops import NodeOps
from .core.element_ops import ElementOps
from .core.material_ops import MaterialOps
from .core.section_ops import SectionOps
from .core.boundary_ops import BoundaryOps
from .core.load_ops import LoadOps
from .core.result_ops import ResultOps
from .core.thickness_ops import ThicknessOps
from .core.group_ops import GroupOps
from .core.loadcomb_ops import LoadCombOps
from .core.tendon_ops import TendonOps
from .core.construction_ops import ConstructionOps
from .core.movingload_ops import MovingLoadOps
from .utils.output import print_result, error_exit, format_json
from .utils.validators import validate_nodes


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

@click.group()
@click.option("--json", "json_mode", is_flag=True, default=False,
              help="Output results as JSON.")
@click.option("--key", "mapi_key", default=None, envvar="MIDAS_MAPI_KEY",
              help="MAPI authentication key.")
@click.option("--url", "base_url", default=None, envvar="MIDAS_BASE_URL",
              help="MAPI base URL.")
@click.pass_context
def cli(ctx, json_mode, mapi_key, base_url):
    """CLI harness for MIDAS Civil NX."""
    ctx.ensure_object(dict)
    ctx.obj["json_mode"] = json_mode
    ctx.obj["mapi_key"] = Session.resolve_key(mapi_key)
    ctx.obj["base_url"] = Session.resolve_url(base_url)


def _conn(ctx) -> Connection:
    return Connection(
        mapi_key=ctx.obj["mapi_key"],
        base_url=ctx.obj["base_url"],
    )


def _out(ctx, data):
    print_result(data, json_mode=ctx.obj["json_mode"])


# ---------------------------------------------------------------------------
# connect / status
# ---------------------------------------------------------------------------

@cli.command("connect")
@click.option("--key", "mapi_key", required=True, prompt="MAPI Key",
              help="MAPI authentication key to save.")
@click.option("--url", "base_url", default=None, help="MAPI base URL.")
@click.pass_context
def connect(ctx, mapi_key, base_url):
    """Save connection credentials and verify connectivity."""
    sess = Session()
    sess.mapi_key = mapi_key
    if base_url:
        sess.base_url = base_url
    conn = Connection(mapi_key=mapi_key, base_url=sess.base_url)
    result = conn.ping()
    if result["ok"]:
        sess.connected = True
        sess.save()
    _out(ctx, result)


@cli.command("status")
@click.pass_context
def status(ctx):
    """Check connection status and Civil NX version."""
    conn = _conn(ctx)
    result = conn.ping()
    _out(ctx, result)


# ---------------------------------------------------------------------------
# model group
# ---------------------------------------------------------------------------

@cli.group()
def model():
    """Model-level operations."""


@model.command("new")
@click.pass_context
def model_new(ctx):
    """Create a new empty model."""
    _out(ctx, ModelOps(_conn(ctx)).new())


@model.command("open")
@click.argument("path")
@click.pass_context
def model_open(ctx, path):
    """Open a model file (.mcb or .mcbz)."""
    _out(ctx, ModelOps(_conn(ctx)).open(path))


@model.command("save")
@click.option("--path", default="", help="Save-as path (optional).")
@click.pass_context
def model_save(ctx, path):
    """Save the current model."""
    ops = ModelOps(_conn(ctx))
    _out(ctx, ops.save_as(path) if path else ops.save())


@model.command("analyse")
@click.pass_context
def model_analyse(ctx):
    """Run analysis on the current model."""
    _out(ctx, ModelOps(_conn(ctx)).analyse())


@model.command("units")
@click.option("--force", default="KN",
              type=click.Choice(["KN","N","KGF","TONF","LBF","KIPS"]),
              show_default=True)
@click.option("--length", default="M",
              type=click.Choice(["M","CM","MM","FT","IN"]),
              show_default=True)
@click.option("--heat", default="BTU",
              type=click.Choice(["CAL","KCAL","J","KJ","BTU"]),
              show_default=True)
@click.option("--temp", default="C", type=click.Choice(["C","F"]), show_default=True)
@click.pass_context
def model_units(ctx, force, length, heat, temp):
    """Set model units."""
    _out(ctx, ModelOps(_conn(ctx)).units(force, length, heat, temp))


@model.command("info")
@click.option("--project", default="")
@click.option("--revision", default="")
@click.option("--user", default="")
@click.option("--title", default="")
@click.option("--comment", default="")
@click.pass_context
def model_info(ctx, project, revision, user, title, comment):
    """Get or set project information."""
    _out(ctx, ModelOps(_conn(ctx)).info(project, revision, user, title, comment))


@model.command("export")
@click.argument("path")
@click.option("--format", "fmt", default="json",
              type=click.Choice(["json", "mct"]), show_default=True)
@click.pass_context
def model_export(ctx, path, fmt):
    """Export model to JSON or MCT file."""
    ops = ModelOps(_conn(ctx))
    result = ops.export_json(path) if fmt == "json" else ops.export_mct(path)
    _out(ctx, result)


@model.command("status")
@click.pass_context
def model_status(ctx):
    """Show project status and max IDs."""
    _out(ctx, ModelOps(_conn(ctx)).status())


@model.command("import")
@click.argument("path")
@click.option("--format", "fmt", default="json",
              type=click.Choice(["json", "mct"]), show_default=True)
@click.pass_context
def model_import(ctx, path, fmt):
    """Import model from JSON or MCT file."""
    ops = ModelOps(_conn(ctx))
    result = ops.import_json(path) if fmt == "json" else ops.import_mct(path)
    _out(ctx, result)


# ---------------------------------------------------------------------------
# node group
# ---------------------------------------------------------------------------

@cli.group()
def node():
    """Node operations."""


@node.command("add")
@click.option("--x", type=float, required=True)
@click.option("--y", type=float, required=True)
@click.option("--z", type=float, required=True)
@click.option("--id", "node_id", type=int, default=None, help="Node ID (auto if omitted).")
@click.pass_context
def node_add(ctx, x, y, z, node_id):
    """Add a single node."""
    _out(ctx, NodeOps(_conn(ctx)).add(x, y, z, node_id))


@node.command("list")
@click.pass_context
def node_list(ctx):
    """List all nodes."""
    _out(ctx, NodeOps(_conn(ctx)).list())


@node.command("get")
@click.argument("node_id", type=int)
@click.pass_context
def node_get(ctx, node_id):
    """Get a node by ID."""
    _out(ctx, NodeOps(_conn(ctx)).get(node_id))


@node.command("sync")
@click.pass_context
def node_sync(ctx):
    """Sync and summarise nodes from Civil NX."""
    result = NodeOps(_conn(ctx)).sync()
    _out(ctx, {"count": result["count"]})


@node.command("delete-all")
@click.confirmation_option(prompt="Delete ALL nodes?")
@click.pass_context
def node_delete_all(ctx):
    """Delete all nodes from the model."""
    _out(ctx, NodeOps(_conn(ctx)).delete_all())


# ---------------------------------------------------------------------------
# element group
# ---------------------------------------------------------------------------

@cli.group()
def element():
    """Element operations."""


@element.command("beam")
@click.option("--i-node", type=int, required=True, help="Start node ID.")
@click.option("--j-node", type=int, required=True, help="End node ID.")
@click.option("--mat", "mat_id", type=int, default=1, show_default=True)
@click.option("--sect", "sect_id", type=int, default=1, show_default=True)
@click.option("--id", "elem_id", type=int, default=None)
@click.option("--angle", type=float, default=0.0, show_default=True)
@click.pass_context
def element_beam(ctx, i_node, j_node, mat_id, sect_id, elem_id, angle):
    """Add a beam element."""
    _out(ctx, ElementOps(_conn(ctx)).add_beam(i_node, j_node, mat_id, sect_id, elem_id, angle))


@element.command("truss")
@click.option("--i-node", type=int, required=True)
@click.option("--j-node", type=int, required=True)
@click.option("--mat", "mat_id", type=int, default=1, show_default=True)
@click.option("--sect", "sect_id", type=int, default=1, show_default=True)
@click.option("--id", "elem_id", type=int, default=None)
@click.pass_context
def element_truss(ctx, i_node, j_node, mat_id, sect_id, elem_id):
    """Add a truss element."""
    _out(ctx, ElementOps(_conn(ctx)).add_truss(i_node, j_node, mat_id, sect_id, elem_id))


@element.command("list")
@click.pass_context
def element_list(ctx):
    """List all elements."""
    _out(ctx, ElementOps(_conn(ctx)).list())


@element.command("get")
@click.argument("elem_id", type=int)
@click.pass_context
def element_get(ctx, elem_id):
    """Get element by ID."""
    _out(ctx, ElementOps(_conn(ctx)).get(elem_id))


@element.command("sync")
@click.pass_context
def element_sync(ctx):
    """Sync and summarise elements from Civil NX."""
    result = ElementOps(_conn(ctx)).sync()
    _out(ctx, {"count": result["count"]})


@element.command("plate")
@click.option("--nodes", required=True, help="Comma-separated node IDs (3 or 4 nodes).")
@click.option("--mat", "mat_id", type=int, default=1, show_default=True)
@click.option("--thick", "thick_id", type=int, default=1, show_default=True)
@click.option("--id", "elem_id", type=int, default=None)
@click.pass_context
def element_plate(ctx, nodes, mat_id, thick_id, elem_id):
    """Add a plate element (3 or 4 nodes)."""
    node_ids = [int(n) for n in nodes.replace(",", " ").split()]
    _out(ctx, ElementOps(_conn(ctx)).add_plate(node_ids, mat_id, thick_id, elem_id))


@element.command("delete-all")
@click.confirmation_option(prompt="Delete ALL elements?")
@click.pass_context
def element_delete_all(ctx):
    """Delete all elements."""
    _out(ctx, ElementOps(_conn(ctx)).delete_all())


# ---------------------------------------------------------------------------
# material group
# ---------------------------------------------------------------------------

@cli.group()
def material():
    """Material definition operations."""


@material.command("steel")
@click.option("--name", required=True)
@click.option("--standard", required=True, help="e.g. ASTM(S)")
@click.option("--grade", required=True, help="e.g. A36")
@click.option("--id", "mat_id", type=int, default=None)
@click.pass_context
def material_steel(ctx, name, standard, grade, mat_id):
    """Add a steel material."""
    _out(ctx, MaterialOps(_conn(ctx)).add_steel(name, standard, grade, mat_id))


@material.command("concrete")
@click.option("--name", required=True)
@click.option("--standard", required=True)
@click.option("--grade", required=True)
@click.option("--id", "mat_id", type=int, default=None)
@click.pass_context
def material_concrete(ctx, name, standard, grade, mat_id):
    """Add a concrete material."""
    _out(ctx, MaterialOps(_conn(ctx)).add_concrete(name, standard, grade, mat_id))


@material.command("user")
@click.option("--name", required=True)
@click.option("--elasticity", type=float, required=True, help="Elastic modulus.")
@click.option("--poisson", type=float, required=True)
@click.option("--density", type=float, required=True)
@click.option("--thermal", type=float, default=1.2e-5, show_default=True)
@click.option("--id", "mat_id", type=int, default=None)
@click.pass_context
def material_user(ctx, name, elasticity, poisson, density, thermal, mat_id):
    """Add a user-defined isotropic material."""
    _out(ctx, MaterialOps(_conn(ctx)).add_user(name, elasticity, poisson, density, thermal, mat_id))


@material.command("list")
@click.pass_context
def material_list(ctx):
    """List all materials."""
    _out(ctx, MaterialOps(_conn(ctx)).list())


@material.command("get")
@click.argument("mat_id", type=int)
@click.pass_context
def material_get(ctx, mat_id):
    """Get material by ID."""
    _out(ctx, MaterialOps(_conn(ctx)).get(mat_id))


# ---------------------------------------------------------------------------
# section group
# ---------------------------------------------------------------------------

@cli.group()
def section():
    """Section definition operations."""


@section.command("db")
@click.option("--name", required=True, help="Section name.")
@click.option("--shape", required=True, help="Shape code, e.g. H.")
@click.option("--standard", required=True, help="Standard, e.g. AISC.")
@click.option("--dbname", required=True, help="Database section name, e.g. W8x35.")
@click.option("--id", "sect_id", type=int, default=None)
@click.pass_context
def section_db(ctx, name, shape, standard, dbname, sect_id):
    """Add a database section."""
    _out(ctx, SectionOps(_conn(ctx)).add_db(name, shape, standard, dbname, sect_id))


@section.command("value")
@click.option("--name", required=True)
@click.option("--shape", required=True)
@click.option("--dims", required=True, help="Comma-separated dimension values.")
@click.option("--id", "sect_id", type=int, default=None)
@click.pass_context
def section_value(ctx, name, shape, dims, sect_id):
    """Add a parametric section by dimensions."""
    dimensions = [float(d) for d in dims.split(",")]
    _out(ctx, SectionOps(_conn(ctx)).add_value(name, shape, dimensions, sect_id))


@section.command("list")
@click.pass_context
def section_list(ctx):
    """List all sections."""
    _out(ctx, SectionOps(_conn(ctx)).list())


@section.command("get")
@click.argument("sect_id", type=int)
@click.pass_context
def section_get(ctx, sect_id):
    """Get section by ID."""
    _out(ctx, SectionOps(_conn(ctx)).get(sect_id))


@section.command("psc")
@click.option("--name", required=True)
@click.option("--dims", default="", help="Comma-separated PSC dimensions.")
@click.option("--no-symm", "symm", is_flag=True, default=True, flag_value=False)
@click.option("--id", "sect_id", type=int, default=None)
@click.pass_context
def section_psc(ctx, name, dims, symm, sect_id):
    """Add a PSC box section."""
    joint = [float(d) for d in dims.split(",")] if dims else []
    _out(ctx, SectionOps(_conn(ctx)).add_psc(name, symm, joint, sect_id))


@section.command("i-shape")
@click.option("--name", required=True)
@click.option("--dims", required=True, help="Comma-separated dims: H,B1,tw,tf1,B2,tf2")
@click.option("--no-symm", "symm", is_flag=True, default=True, flag_value=False)
@click.option("--id", "sect_id", type=int, default=None)
@click.pass_context
def section_i_shape(ctx, name, dims, symm, sect_id):
    """Add a parametric I-shape section."""
    dimensions = [float(d) for d in dims.split(",")]
    _out(ctx, SectionOps(_conn(ctx)).add_i_shape(name, symm, dimensions, sect_id))


@section.command("tapered")
@click.option("--name", required=True)
@click.option("--sect-i", "sect_i_id", type=int, required=True, help="I-end section ID.")
@click.option("--sect-j", "sect_j_id", type=int, required=True, help="J-end section ID.")
@click.option("--id", "sect_id", type=int, default=None)
@click.pass_context
def section_tapered(ctx, name, sect_i_id, sect_j_id, sect_id):
    """Add a tapered section."""
    _out(ctx, SectionOps(_conn(ctx)).add_tapered(name, sect_i_id, sect_j_id, sect_id))


@section.command("sync")
@click.pass_context
def section_sync(ctx):
    """Sync and summarise sections from Civil NX."""
    result = SectionOps(_conn(ctx)).sync()
    _out(ctx, {"count": result["count"]})


@section.command("delete-all")
@click.confirmation_option(prompt="Delete ALL sections?")
@click.pass_context
def section_delete_all(ctx):
    """Delete all sections."""
    _out(ctx, SectionOps(_conn(ctx)).delete_all())


# ---------------------------------------------------------------------------
# boundary group
# ---------------------------------------------------------------------------

@cli.group()
def boundary():
    """Boundary condition operations."""


@boundary.command("support")
@click.option("--nodes", required=True,
              help="Comma-separated node IDs, e.g. 1,2,3.")
@click.option("--type", "constraint", default="fix",
              help="fix / pin / roller / 6-char string TTTTFF.")
@click.option("--group", default="")
@click.pass_context
def boundary_support(ctx, nodes, constraint, group):
    """Apply support boundary conditions."""
    node_ids = [int(n) for n in nodes.replace(",", " ").split()]
    _out(ctx, BoundaryOps(_conn(ctx)).add_support(node_ids, constraint, group))


@boundary.command("list-supports")
@click.pass_context
def boundary_list_supports(ctx):
    """List all support boundary conditions."""
    _out(ctx, BoundaryOps(_conn(ctx)).list_supports())


@boundary.command("elastic-link")
@click.option("--i-node", type=int, required=True)
@click.option("--j-node", type=int, required=True)
@click.option("--type", "link_type", default="GEN", show_default=True)
@click.option("--sdx", type=float, default=0.0)
@click.option("--sdy", type=float, default=0.0)
@click.option("--sdz", type=float, default=0.0)
@click.option("--srx", type=float, default=0.0)
@click.option("--sry", type=float, default=0.0)
@click.option("--srz", type=float, default=0.0)
@click.pass_context
def boundary_elastic_link(ctx, i_node, j_node, link_type,
                          sdx, sdy, sdz, srx, sry, srz):
    """Add an elastic link between two nodes."""
    _out(ctx, BoundaryOps(_conn(ctx)).add_elastic_link(
        i_node, j_node, link_type, sdx, sdy, sdz, srx, sry, srz))


@boundary.command("list-elastic-links")
@click.pass_context
def boundary_list_elastic_links(ctx):
    """List all elastic links."""
    _out(ctx, BoundaryOps(_conn(ctx)).list_elastic_links())


@boundary.command("delete-elastic-links")
@click.confirmation_option(prompt="Delete ALL elastic links?")
@click.pass_context
def boundary_delete_elastic_links(ctx):
    """Delete all elastic links."""
    _out(ctx, BoundaryOps(_conn(ctx)).delete_elastic_links())


@boundary.command("rigid-link")
@click.option("--master", "master_node", type=int, required=True)
@click.option("--slaves", required=True, help="Comma-separated slave node IDs.")
@click.option("--dof", default="123456", show_default=True)
@click.option("--group", default="")
@click.pass_context
def boundary_rigid_link(ctx, master_node, slaves, dof, group):
    """Add a rigid link."""
    slave_ids = [int(n) for n in slaves.replace(",", " ").split()]
    _out(ctx, BoundaryOps(_conn(ctx)).add_rigid_link(master_node, slave_ids, dof, group))


@boundary.command("list-rigid-links")
@click.pass_context
def boundary_list_rigid_links(ctx):
    """List all rigid links."""
    _out(ctx, BoundaryOps(_conn(ctx)).list_rigid_links())


@boundary.command("delete-rigid-links")
@click.confirmation_option(prompt="Delete ALL rigid links?")
@click.pass_context
def boundary_delete_rigid_links(ctx):
    """Delete all rigid links."""
    _out(ctx, BoundaryOps(_conn(ctx)).delete_rigid_links())


@boundary.command("point-spring")
@click.option("--node", "node_id", type=int, required=True)
@click.option("--sdx", type=float, default=0.0)
@click.option("--sdy", type=float, default=0.0)
@click.option("--sdz", type=float, default=0.0)
@click.option("--srx", type=float, default=0.0)
@click.option("--sry", type=float, default=0.0)
@click.option("--srz", type=float, default=0.0)
@click.option("--group", default="")
@click.pass_context
def boundary_point_spring(ctx, node_id, sdx, sdy, sdz, srx, sry, srz, group):
    """Add a linear point spring support."""
    _out(ctx, BoundaryOps(_conn(ctx)).add_point_spring(
        node_id, sdx, sdy, sdz, srx, sry, srz, group))


@boundary.command("list-springs")
@click.pass_context
def boundary_list_springs(ctx):
    """List all point springs."""
    _out(ctx, BoundaryOps(_conn(ctx)).list_point_springs())


@boundary.command("delete-springs")
@click.confirmation_option(prompt="Delete ALL point springs?")
@click.pass_context
def boundary_delete_springs(ctx):
    """Delete all point springs."""
    _out(ctx, BoundaryOps(_conn(ctx)).delete_point_springs())


@boundary.command("mlfc")
@click.option("--name", required=True)
@click.option("--type", "func_type", default="FORCE",
              type=click.Choice(["FORCE", "MOMENT"]), show_default=True)
@click.option("--data", default="0,0,1,1",
              help="Alternating x,y pairs: x1,y1,x2,y2,...")
@click.option("--no-symm", "symm", is_flag=True, default=True, flag_value=False)
@click.pass_context
def boundary_mlfc(ctx, name, func_type, data, symm):
    """Add a multi-linear force-deformation function."""
    vals = [float(v) for v in data.split(",")]
    pairs = [[vals[i], vals[i+1]] for i in range(0, len(vals)-1, 2)]
    _out(ctx, BoundaryOps(_conn(ctx)).add_mlfc(name, func_type, symm, pairs))


@boundary.command("list-mlfc")
@click.pass_context
def boundary_list_mlfc(ctx):
    """List all multi-linear force-deformation functions."""
    _out(ctx, BoundaryOps(_conn(ctx)).list_mlfc())


@boundary.command("delete-supports")
@click.confirmation_option(prompt="Delete ALL supports?")
@click.pass_context
def boundary_delete_supports(ctx):
    """Delete all support boundary conditions."""
    _out(ctx, BoundaryOps(_conn(ctx)).delete_supports())


# ---------------------------------------------------------------------------
# load group
# ---------------------------------------------------------------------------

@cli.group()
def load():
    """Load operations."""


@load.command("case")
@click.option("--name", required=True)
@click.option("--type", "lc_type", default="USER", show_default=True)
@click.pass_context
def load_case(ctx, name, lc_type):
    """Add a static load case."""
    _out(ctx, LoadOps(_conn(ctx)).add_load_case(name, lc_type))


@load.command("list-cases")
@click.pass_context
def load_list_cases(ctx):
    """List all load cases."""
    _out(ctx, LoadOps(_conn(ctx)).list_load_cases())


@load.command("self-weight")
@click.option("--case", "load_case_name", required=True)
@click.option("--dir", "direction", default="Z", show_default=True)
@click.option("--factor", type=float, default=-1.0, show_default=True)
@click.pass_context
def load_self_weight(ctx, load_case_name, direction, factor):
    """Add self-weight load."""
    _out(ctx, LoadOps(_conn(ctx)).add_self_weight(load_case_name, direction, factor))


@load.command("nodal")
@click.option("--nodes", required=True, help="Comma-separated node IDs.")
@click.option("--case", "load_case_name", required=True)
@click.option("--group", default="")
@click.option("--fx", type=float, default=0.0)
@click.option("--fy", type=float, default=0.0)
@click.option("--fz", type=float, default=0.0)
@click.option("--mx", type=float, default=0.0)
@click.option("--my", type=float, default=0.0)
@click.option("--mz", type=float, default=0.0)
@click.pass_context
def load_nodal(ctx, nodes, load_case_name, group, fx, fy, fz, mx, my, mz):
    """Add nodal loads."""
    node_ids = [int(n) for n in nodes.replace(",", " ").split()]
    _out(ctx, LoadOps(_conn(ctx)).add_nodal_load(
        node_ids, load_case_name, group, fx, fy, fz, mx, my, mz))


@load.command("beam")
@click.option("--elems", required=True, help="Comma-separated element IDs.")
@click.option("--case", "load_case_name", required=True)
@click.option("--group", default="")
@click.option("--value", type=float, default=0.0)
@click.option("--dir", "direction", default="GZ", show_default=True)
@click.pass_context
def load_beam(ctx, elems, load_case_name, group, value, direction):
    """Add uniform beam distributed load."""
    elem_ids = [int(e) for e in elems.replace(",", " ").split()]
    _out(ctx, LoadOps(_conn(ctx)).add_beam_load(
        elem_ids, load_case_name, group, value, direction))


@load.command("beam-trapezoidal")
@click.option("--elems", required=True, help="Comma-separated element IDs.")
@click.option("--case", "load_case_name", required=True)
@click.option("--d", "d_vals", required=True,
              help="Distance ratios, comma-separated e.g. 0,0.5,1")
@click.option("--p", "p_vals", required=True,
              help="Load values at each distance point, comma-separated.")
@click.option("--dir", "direction", default="GZ", show_default=True)
@click.option("--group", default="")
@click.pass_context
def load_beam_trapezoidal(ctx, elems, load_case_name, d_vals, p_vals, direction, group):
    """Add a trapezoidal (non-uniform) beam distributed load."""
    elem_ids = [int(e) for e in elems.replace(",", " ").split()]
    d = [float(v) for v in d_vals.split(",")]
    p = [float(v) for v in p_vals.split(",")]
    _out(ctx, LoadOps(_conn(ctx)).add_beam_load_trapezoidal(
        elem_ids, load_case_name, d, p, direction, group))


@load.command("pressure")
@click.option("--elems", required=True, help="Comma-separated plate element IDs.")
@click.option("--case", "load_case_name", required=True)
@click.option("--value", type=float, default=0.0)
@click.option("--dir", "direction", default="GZ", show_default=True)
@click.option("--group", default="")
@click.pass_context
def load_pressure(ctx, elems, load_case_name, value, direction, group):
    """Add pressure load on plate elements."""
    elem_ids = [int(e) for e in elems.replace(",", " ").split()]
    _out(ctx, LoadOps(_conn(ctx)).add_pressure_load(
        elem_ids, load_case_name, group, value, direction))


@load.command("load-to-mass")
@click.option("--dir", "direction", required=True,
              type=click.Choice(["X", "Y", "Z", "XY", "YZ", "XZ", "XYZ"]),
              help="Mass direction.")
@click.option("--cases", required=True, help="Comma-separated load case names.")
@click.option("--factors", default="", help="Comma-separated factors (default 1.0 each).")
@click.pass_context
def load_to_mass(ctx, direction, cases, factors):
    """Convert static loads to masses."""
    lc_list = [c.strip() for c in cases.split(",")]
    f_list = [float(f) for f in factors.split(",")] if factors else None
    _out(ctx, LoadOps(_conn(ctx)).add_load_to_mass(direction, lc_list, f_list))


@load.command("delete-case")
@click.argument("name")
@click.pass_context
def load_delete_case(ctx, name):
    """Delete a load case by name."""
    _out(ctx, LoadOps(_conn(ctx)).delete_load_case(name))


@load.command("list-nodal")
@click.pass_context
def load_list_nodal(ctx):
    """List all nodal loads."""
    _out(ctx, LoadOps(_conn(ctx)).list_nodal_loads())


@load.command("list-beam")
@click.pass_context
def load_list_beam(ctx):
    """List all beam loads."""
    _out(ctx, LoadOps(_conn(ctx)).list_beam_loads())


@load.command("list-pressure")
@click.pass_context
def load_list_pressure(ctx):
    """List all pressure loads."""
    _out(ctx, LoadOps(_conn(ctx)).list_pressure_loads())


# ---------------------------------------------------------------------------
# thickness group
# ---------------------------------------------------------------------------

@cli.group()
def thickness():
    """Plate thickness operations."""


@thickness.command("add")
@click.option("--name", required=True)
@click.option("--thick", type=float, required=True, help="Thickness value.")
@click.option("--thick-out", type=float, default=-1.0, show_default=True,
              help="Out-of-plane thickness (-1 = same as thick).")
@click.option("--offset", type=float, default=0.0, show_default=True)
@click.option("--id", "thick_id", type=int, default=None)
@click.pass_context
def thickness_add(ctx, name, thick, thick_out, offset, thick_id):
    """Add a plate thickness definition."""
    _out(ctx, ThicknessOps(_conn(ctx)).add(name, thick, thick_out, offset, thick_id))


@thickness.command("list")
@click.pass_context
def thickness_list(ctx):
    """List all thickness definitions."""
    _out(ctx, ThicknessOps(_conn(ctx)).list())


@thickness.command("get")
@click.argument("thick_id", type=int)
@click.pass_context
def thickness_get(ctx, thick_id):
    """Get thickness definition by ID."""
    _out(ctx, ThicknessOps(_conn(ctx)).get(thick_id))


@thickness.command("delete-all")
@click.confirmation_option(prompt="Delete ALL thickness definitions?")
@click.pass_context
def thickness_delete_all(ctx):
    """Delete all thickness definitions."""
    _out(ctx, ThicknessOps(_conn(ctx)).delete_all())


# ---------------------------------------------------------------------------
# group group
# ---------------------------------------------------------------------------

@cli.group(name="group")
def grp():
    """Structure, boundary, and load group operations."""


@grp.command("structure-add")
@click.option("--name", required=True)
@click.option("--nodes", default="", help="Comma-separated node IDs.")
@click.option("--elems", default="", help="Comma-separated element IDs.")
@click.pass_context
def group_structure_add(ctx, name, nodes, elems):
    """Add or update a structure group."""
    node_ids = [int(n) for n in nodes.replace(",", " ").split()] if nodes else []
    elem_ids = [int(e) for e in elems.replace(",", " ").split()] if elems else []
    _out(ctx, GroupOps(_conn(ctx)).add_structure_group(name, node_ids, elem_ids))


@grp.command("structure-list")
@click.pass_context
def group_structure_list(ctx):
    """List all structure groups."""
    _out(ctx, GroupOps(_conn(ctx)).list_structure_groups())


@grp.command("structure-delete-all")
@click.confirmation_option(prompt="Delete ALL structure groups?")
@click.pass_context
def group_structure_delete_all(ctx):
    """Delete all structure groups."""
    _out(ctx, GroupOps(_conn(ctx)).delete_all_structure_groups())


@grp.command("boundary-add")
@click.option("--name", required=True)
@click.pass_context
def group_boundary_add(ctx, name):
    """Add a boundary group."""
    _out(ctx, GroupOps(_conn(ctx)).add_boundary_group(name))


@grp.command("boundary-list")
@click.pass_context
def group_boundary_list(ctx):
    """List all boundary groups."""
    _out(ctx, GroupOps(_conn(ctx)).list_boundary_groups())


@grp.command("boundary-delete-all")
@click.confirmation_option(prompt="Delete ALL boundary groups?")
@click.pass_context
def group_boundary_delete_all(ctx):
    """Delete all boundary groups."""
    _out(ctx, GroupOps(_conn(ctx)).delete_all_boundary_groups())


@grp.command("load-add")
@click.option("--name", required=True)
@click.pass_context
def group_load_add(ctx, name):
    """Add a load group."""
    _out(ctx, GroupOps(_conn(ctx)).add_load_group(name))


@grp.command("load-list")
@click.pass_context
def group_load_list(ctx):
    """List all load groups."""
    _out(ctx, GroupOps(_conn(ctx)).list_load_groups())


@grp.command("load-delete-all")
@click.confirmation_option(prompt="Delete ALL load groups?")
@click.pass_context
def group_load_delete_all(ctx):
    """Delete all load groups."""
    _out(ctx, GroupOps(_conn(ctx)).delete_all_load_groups())


# ---------------------------------------------------------------------------
# loadcomb group
# ---------------------------------------------------------------------------

@cli.group()
def loadcomb():
    """Load combination operations."""


@loadcomb.command("add")
@click.option("--name", required=True)
@click.option("--active", default="ACTIVE",
              type=click.Choice(["ACTIVE", "INACTIVE"]), show_default=True)
@click.option("--type", "typ", default="Add",
              type=click.Choice(["Add", "Envelope", "ABS", "SRSS"]), show_default=True)
@click.option("--cases", default="",
              help="Load cases as name:factor pairs, comma-separated. e.g. LC1:1.2,LC2:0.9")
@click.option("--id", "comb_id", type=int, default=None)
@click.pass_context
def loadcomb_add(ctx, name, active, typ, cases, comb_id):
    """Add a load combination."""
    case_list = []
    if cases:
        for item in cases.split(","):
            parts = item.strip().split(":")
            case_list.append({
                "name": parts[0],
                "factor": float(parts[1]) if len(parts) > 1 else 1.0,
            })
    _out(ctx, LoadCombOps(_conn(ctx)).add(name, active, typ, case_list, comb_id))


@loadcomb.command("list")
@click.pass_context
def loadcomb_list(ctx):
    """List all load combinations."""
    _out(ctx, LoadCombOps(_conn(ctx)).list())


@loadcomb.command("get")
@click.argument("comb_id", type=int)
@click.pass_context
def loadcomb_get(ctx, comb_id):
    """Get load combination by ID."""
    _out(ctx, LoadCombOps(_conn(ctx)).get(comb_id))


@loadcomb.command("delete-all")
@click.confirmation_option(prompt="Delete ALL load combinations?")
@click.pass_context
def loadcomb_delete_all(ctx):
    """Delete all load combinations."""
    _out(ctx, LoadCombOps(_conn(ctx)).delete_all())


# ---------------------------------------------------------------------------
# tendon group
# ---------------------------------------------------------------------------

@cli.group()
def tendon():
    """Tendon (prestress) operations."""


@tendon.command("property-add")
@click.option("--name", required=True)
@click.option("--rho", type=float, required=True, help="Density.")
@click.option("--ult-st", type=float, required=True, help="Ultimate strength.")
@click.option("--yield-st", type=float, required=True, help="Yield strength.")
@click.option("--curv-fric", type=float, default=0.0, show_default=True,
              help="Curvature friction factor.")
@click.option("--wob-fric", type=float, default=0.0, show_default=True,
              help="Wobble friction factor.")
@click.option("--id", "prop_id", type=int, default=None)
@click.pass_context
def tendon_property_add(ctx, name, rho, ult_st, yield_st, curv_fric, wob_fric, prop_id):
    """Add a tendon material property."""
    _out(ctx, TendonOps(_conn(ctx)).add_property(
        name, rho, ult_st, yield_st, curv_fric, wob_fric, prop_id))


@tendon.command("list-properties")
@click.pass_context
def tendon_list_properties(ctx):
    """List all tendon properties."""
    _out(ctx, TendonOps(_conn(ctx)).list_properties())


@tendon.command("profile-add")
@click.option("--name", required=True)
@click.option("--prop-id", type=int, required=True, help="Tendon property ID.")
@click.option("--elems", required=True, help="Comma-separated element IDs.")
@click.option("--id", "profile_id", type=int, default=None)
@click.pass_context
def tendon_profile_add(ctx, name, prop_id, elems, profile_id):
    """Add a tendon profile."""
    elem_ids = [int(e) for e in elems.replace(",", " ").split()]
    _out(ctx, TendonOps(_conn(ctx)).add_profile(name, prop_id, elem_ids, profile_id))


@tendon.command("list-profiles")
@click.pass_context
def tendon_list_profiles(ctx):
    """List all tendon profiles."""
    _out(ctx, TendonOps(_conn(ctx)).list_profiles())


@tendon.command("prestress-add")
@click.option("--profile", "profile_name", required=True, help="Tendon profile name.")
@click.option("--force", type=float, required=True, help="Prestress force.")
@click.option("--tension-type", default="BOTH",
              type=click.Choice(["BOTH", "I_END", "J_END"]), show_default=True)
@click.option("--id", "prestress_id", type=int, default=None)
@click.pass_context
def tendon_prestress_add(ctx, profile_name, force, tension_type, prestress_id):
    """Add prestress to a tendon profile."""
    _out(ctx, TendonOps(_conn(ctx)).add_prestress(
        profile_name, force, tension_type, prestress_id))


@tendon.command("list-prestress")
@click.pass_context
def tendon_list_prestress(ctx):
    """List all prestress definitions."""
    _out(ctx, TendonOps(_conn(ctx)).list_prestress())


# ---------------------------------------------------------------------------
# cs (construction stage) group
# ---------------------------------------------------------------------------

@cli.group()
def cs():
    """Construction stage operations."""


@cs.command("add")
@click.option("--name", required=True)
@click.option("--day", type=int, default=0, show_default=True,
              help="Duration in days.")
@click.option("--id", "stage_id", type=int, default=None)
@click.pass_context
def cs_add(ctx, name, day, stage_id):
    """Add a construction stage."""
    _out(ctx, ConstructionOps(_conn(ctx)).add_stage(name, day, stage_id))


@cs.command("list")
@click.pass_context
def cs_list(ctx):
    """List all construction stages."""
    _out(ctx, ConstructionOps(_conn(ctx)).list_stages())


@cs.command("get")
@click.argument("stage_id", type=int)
@click.pass_context
def cs_get(ctx, stage_id):
    """Get construction stage by ID."""
    _out(ctx, ConstructionOps(_conn(ctx)).get(stage_id))


@cs.command("delete-all")
@click.confirmation_option(prompt="Delete ALL construction stages?")
@click.pass_context
def cs_delete_all(ctx):
    """Delete all construction stages."""
    _out(ctx, ConstructionOps(_conn(ctx)).delete_all())


# ---------------------------------------------------------------------------
# movingload group
# ---------------------------------------------------------------------------

@cli.group()
def movingload():
    """Moving load operations."""


@movingload.command("code-add")
@click.argument("code_name")
@click.pass_context
def movingload_code_add(ctx, code_name):
    """Add a moving load code."""
    _out(ctx, MovingLoadOps(_conn(ctx)).add_code(code_name))


@movingload.command("list-codes")
@click.pass_context
def movingload_list_codes(ctx):
    """List all moving load codes."""
    _out(ctx, MovingLoadOps(_conn(ctx)).list_codes())


@movingload.command("lane-add")
@click.option("--name", required=True)
@click.option("--elems", required=True, help="Comma-separated element IDs.")
@click.option("--ecc", type=float, default=0.0, show_default=True,
              help="Eccentricity.")
@click.option("--wheel-space", type=float, default=1.8, show_default=True,
              help="Wheel spacing.")
@click.pass_context
def movingload_lane_add(ctx, name, elems, ecc, wheel_space):
    """Add a moving load lane."""
    elem_ids = [int(e) for e in elems.replace(",", " ").split()]
    _out(ctx, MovingLoadOps(_conn(ctx)).add_lane(name, elem_ids, ecc, wheel_space))


@movingload.command("list-lanes")
@click.pass_context
def movingload_list_lanes(ctx):
    """List all moving load lanes."""
    _out(ctx, MovingLoadOps(_conn(ctx)).list_lanes())


@movingload.command("list-cases")
@click.pass_context
def movingload_list_cases(ctx):
    """List all moving load cases."""
    _out(ctx, MovingLoadOps(_conn(ctx)).list_cases())


# ---------------------------------------------------------------------------
# result group
# ---------------------------------------------------------------------------

@cli.group()
def result():
    """Result extraction operations (model must be analysed first)."""


@result.command("reaction")
@click.option("--case", "load_case", required=True)
@click.option("--type", "result_type", default="Global",
              type=click.Choice(["Global", "Local"]), show_default=True)
@click.pass_context
def result_reaction(ctx, load_case, result_type):
    """Get support reactions."""
    _out(ctx, ResultOps(_conn(ctx)).reaction(load_case, result_type))


@result.command("displacement")
@click.option("--case", "load_case", required=True)
@click.option("--type", "result_type", default="Global",
              type=click.Choice(["Global", "Local"]), show_default=True)
@click.pass_context
def result_displacement(ctx, load_case, result_type):
    """Get node displacements."""
    _out(ctx, ResultOps(_conn(ctx)).displacement(load_case, result_type))


@result.command("beam-force")
@click.option("--case", "load_case", required=True)
@click.pass_context
def result_beam_force(ctx, load_case):
    """Get beam element forces."""
    _out(ctx, ResultOps(_conn(ctx)).beam_force(load_case))


@result.command("beam-stress")
@click.option("--case", "load_case", required=True)
@click.pass_context
def result_beam_stress(ctx, load_case):
    """Get beam element stresses."""
    _out(ctx, ResultOps(_conn(ctx)).beam_stress(load_case))


@result.command("truss-force")
@click.option("--case", "load_case", required=True)
@click.pass_context
def result_truss_force(ctx, load_case):
    """Get truss element forces."""
    _out(ctx, ResultOps(_conn(ctx)).truss_force(load_case))


@result.command("truss-stress")
@click.option("--case", "load_case", required=True)
@click.pass_context
def result_truss_stress(ctx, load_case):
    """Get truss element stresses."""
    _out(ctx, ResultOps(_conn(ctx)).truss_stress(load_case))


@result.command("plate-force")
@click.option("--case", "load_case", required=True)
@click.option("--type", "result_type", default="Global",
              type=click.Choice(["Global", "Local"]), show_default=True)
@click.pass_context
def result_plate_force(ctx, load_case, result_type):
    """Get plate element forces."""
    _out(ctx, ResultOps(_conn(ctx)).plate_force(load_case, result_type))


@result.command("beam-force-vbm")
@click.option("--case", "load_case", required=True)
@click.pass_context
def result_beam_force_vbm(ctx, load_case):
    """Get beam element forces in VBM format."""
    _out(ctx, ResultOps(_conn(ctx)).beam_force_vbm(load_case))


@result.command("beam-stress-psc")
@click.option("--case", "load_case", required=True)
@click.pass_context
def result_beam_stress_psc(ctx, load_case):
    """Get PSC beam element stresses."""
    _out(ctx, ResultOps(_conn(ctx)).beam_stress_psc(load_case))


@result.command("table")
@click.option("--type", "table_type", required=True, help="TABLE_TYPE string.")
@click.option("--case", "load_case", required=True)
@click.pass_context
def result_table(ctx, table_type, load_case):
    """Query a raw result table by type name."""
    _out(ctx, ResultOps(_conn(ctx)).raw_table(table_type, load_case))


# ---------------------------------------------------------------------------
# api group (raw passthrough)
# ---------------------------------------------------------------------------

@cli.group()
def api():
    """Raw MAPI passthrough."""


@api.command("get")
@click.argument("endpoint")
@click.pass_context
def api_get(ctx, endpoint):
    """Send a GET request to a MAPI endpoint."""
    _out(ctx, _conn(ctx).get(endpoint))


@api.command("post")
@click.argument("endpoint")
@click.option("--body", default="{}", help="JSON body string.")
@click.pass_context
def api_post(ctx, endpoint, body):
    """Send a POST request to a MAPI endpoint."""
    try:
        parsed = _json.loads(body)
    except _json.JSONDecodeError as exc:
        click.echo(f"Error parsing body JSON: {exc}", err=True)
        sys.exit(1)
    _out(ctx, _conn(ctx).post(endpoint, parsed))


@api.command("put")
@click.argument("endpoint")
@click.option("--body", default="{}", help="JSON body string.")
@click.pass_context
def api_put(ctx, endpoint, body):
    """Send a PUT request to a MAPI endpoint."""
    try:
        parsed = _json.loads(body)
    except _json.JSONDecodeError as exc:
        click.echo(f"Error parsing body JSON: {exc}", err=True)
        sys.exit(1)
    _out(ctx, _conn(ctx).put(endpoint, parsed))


@api.command("delete")
@click.argument("endpoint")
@click.pass_context
def api_delete(ctx, endpoint):
    """Send a DELETE request to a MAPI endpoint."""
    _out(ctx, _conn(ctx).delete(endpoint))


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

@cli.command("repl")
@click.pass_context
def repl(ctx):
    """Start an interactive REPL session."""
    import shlex
    click.echo("MIDAS Civil NX CLI REPL. Type 'exit' or 'quit' to leave.")
    click.echo(f"  key: {ctx.obj['mapi_key'][:8]}...  url: {ctx.obj['base_url']}")
    while True:
        try:
            line = click.prompt("midas-civil", default="", show_default=False)
        except (EOFError, KeyboardInterrupt):
            break
        line = line.strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break
        try:
            args = shlex.split(line)
        except ValueError as exc:
            click.echo(f"Parse error: {exc}")
            continue
        try:
            extra = []
            if ctx.obj["json_mode"]:
                extra = ["--json"]
            if ctx.obj["mapi_key"]:
                extra += ["--key", ctx.obj["mapi_key"]]
            if ctx.obj["base_url"]:
                extra += ["--url", ctx.obj["base_url"]]
            cli.main(args=extra + args, standalone_mode=False,
                     obj=dict(ctx.obj))
        except SystemExit:
            pass
        except Exception as exc:
            click.echo(f"Error: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    cli()


if __name__ == "__main__":
    main()
