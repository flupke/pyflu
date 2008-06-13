"""Utilities for working with python modules"""


def deep_import(name):
    """
    A version of __import__ that works as expected when using the form 
    'module.name' (returns the object corresponding to 'name' in this case,
    instead of 'module'.
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
