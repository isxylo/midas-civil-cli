"""Output formatting utilities: JSON mode and human-readable tables."""
import json
import sys


def format_json(data: dict | list) -> str:
    return json.dumps(data, indent=2, default=str)


def print_result(data: dict | list, json_mode: bool = False,
                 title: str = "") -> None:
    """Print data either as JSON or a human-readable table."""
    if json_mode:
        click_echo(format_json(data))
        return

    if title:
        click_echo(f"\n{title}")
        click_echo("-" * len(title))

    if isinstance(data, dict):
        _print_dict(data)
    elif isinstance(data, list):
        for item in data:
            _print_dict(item) if isinstance(item, dict) else click_echo(str(item))
    else:
        click_echo(str(data))


def _print_dict(d: dict, indent: int = 0) -> None:
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click_echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            click_echo(f"{prefix}{k}:")
            for item in v:
                _print_dict(item, indent + 1)
                click_echo(f"{prefix}  ---")
        else:
            click_echo(f"{prefix}{k}: {v}")


def click_echo(msg: str) -> None:
    """Write to stdout; import click only at call time to avoid circular deps."""
    try:
        import click
        click.echo(msg)
    except ImportError:
        print(msg, file=sys.stdout)


def error_exit(msg: str, json_mode: bool = False) -> None:
    """Print error and exit with code 1."""
    if json_mode:
        click_echo(format_json({"error": msg}))
    else:
        click_echo(f"Error: {msg}")
    sys.exit(1)
