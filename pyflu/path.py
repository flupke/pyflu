"""Path related utilities."""

from os.path import commonprefix


def sub_path(path, parent):
    """Returns the portion of ``path`` that lies under ``parent``"""
    return path[len(commonprefix((path, parent))) + 1:]
