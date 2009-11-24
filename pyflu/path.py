"""Path related utilities."""

import os
from os.path import commonprefix, abspath, join, splitext


def sub_path(path, parent):
    """Returns the portion of ``path`` that lies under ``parent``"""
    path = abspath(path)
    parent = abspath(parent)
    return path[len(commonprefix((path, parent))) + 1:]


def iter_files(ext_filter, path="."):
    """
    An iterator returning all the files under ``path`` whose extension matches 
    ``ext_filter``.
    """
    for dirpath, dirname, filenames in os.walk(path):
        for fname in filenames:
            name, ext = splitext(fname)
            if ext == ext_filter:
                yield join(dirpath, fname)
