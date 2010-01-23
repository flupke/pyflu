"""
Charset encoding utilities.
"""

import sys


def to_fs_encoding(value):
    """
    Convert an unicode value to a str in the filesystem encoding.
    """
    if not isinstance(value, unicode):
        raise TypeError("expected a unicode value")
    return value.encode(sys.getfilesystemencoding())


def from_fs_encoding(value):
    """
    Convert a str value to an unicode object from the filesystem encoding.
    """
    if not isinstance(value, str):
        raise TypeError("expected a str value")
    return value.decode(sys.getfilesystemencoding())
