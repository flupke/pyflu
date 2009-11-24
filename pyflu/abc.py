"""
Abstract base classes utils.
"""


def is_fully_implemented(cls):
    """
    Returns True if a ``cls`` is a fully implemented derivate of an ABC.
    """
    return not getattr(cls, '__abstractmethods__', False)


def implements(cls, base):
    return issubclass(cls, base) and is_fully_implemented(cls)
