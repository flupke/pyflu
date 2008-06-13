"""Utilities for working with python modules"""

def deep_import(name):
    """
    A version of import that works as expected when using the form module.name.
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
