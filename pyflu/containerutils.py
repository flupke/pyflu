"""
Various container utilities
"""


def get_from_dict(d, path):
    """
    Extract a value pointed by ``path`` from a nested dict.

    Example:
    >>> d = {
    ...     "path": {
    ...         "to": {
    ...             "item": "value"
    ...         }
    ...     }
    ... }
    >>> get_from_dict(d, "/path/to/item")
    'value'
    """
    components = [c for c in path.split("/") if c]
    if not len(components):
        raise ValueError("empty path")
    try:
        c = d[components.pop(0)]
        while components:
            c = c[components.pop(0)]
    except KeyError:
        raise ValueError("invalid path: %s" % path)
    return c
