"""Path related utilities."""

import os
import sys
from os.path import commonprefix, abspath, join, splitext


def sub_path(path, parent):
    """Returns the portion of ``path`` that lies under ``parent``"""
    path = abspath(path)
    parent = abspath(parent)
    return path[len(commonprefix((path, parent))) + 1:]


def iter_files(ext_filter, path=".", exclude=None):
    """
    An iterator returning all the files under *path* whose extension matches 
    *ext_filter*.

    The optional *exclude* argument should be a list of paths prefixes to 
    exclude from the search.
    """
    for dirpath, dirname, filenames in os.walk(path):
        excluded = False
        for excl_path in exclude:
            if dirpath.startswith(excl_path):
                excluded = True
                break
        if not excluded:
            for fname in filenames:
                name, ext = splitext(fname)
                if ext == ext_filter:
                    yield join(dirpath, fname)


def file_mtime(path):
    """
    Get the (correct) modification time of the file at *path*.
    """
    stat = os.stat(path)
    mtime = stat.st_mtime
    if sys.platform == "win32":
        mtime -= stat.st_ctime
    return mtime

