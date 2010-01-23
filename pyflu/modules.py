"""Utilities for working with python modules"""

import os
import types


def deep_import(name):
    """
    A version of __import__ that works as expected when using the form 
    'module.name' (returns the object corresponding to 'name', instead of 
    'module').
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def path_to_name(path, root=None):
    """
    (Naively) converts a path to a .py file to the corresponding dotted 
    module path.

    If root is given, the module path is relative to root.
    """
    if not path.endswith(".py"):
        raise ValueError("you must give a .py file path")
    if root is not None:
        path = path[len(os.path.commonprefix((path, root))) + 1:]
    module_path = path.replace(os.sep, ".")[:-len(".py")]
    if module_path.endswith(".__init__"):
        module_path = module_path[:-len(".__init__")]
    return module_path


def pprint_func(f):
    """
    Nicely prints a function or method name, including the path to it.
    """
    if isinstance(f, types.MethodType):
        cls = f.im_class
        return "%s.%s.%s" % (cls.__module__, cls.__name__, f.__name__)
    else:
        return "%s.%s" % (f.__module__, f.__name__)

