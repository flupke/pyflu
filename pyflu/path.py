"""Path related utilities."""

from os.path import commonprefix, abspath


def sub_path(path, parent):
    """Returns the portion of ``path`` that lies under ``parent``"""
    path = abspath(path)
    parent = abspath(parent)
    return path[len(commonprefix((path, parent))) + 1:]
