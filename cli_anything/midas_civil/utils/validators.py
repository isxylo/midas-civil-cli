"""Input validation helpers."""
import os


def validate_nodes(ctx, param, value):
    """Click callback: parse a comma-separated or space-separated node ID list."""
    if not value:
        return []
    ids = []
    for token in value.replace(",", " ").split():
        try:
            ids.append(int(token))
        except ValueError:
            from click import BadParameter
            raise BadParameter(f"Invalid node ID: {token!r}")
    return ids


def validate_path(path: str, extensions: list[str]) -> str | None:
    """Return error string if path does not end with one of the given extensions."""
    if not any(path.endswith(ext) for ext in extensions):
        return f"File must have one of these extensions: {extensions}"
    return None
