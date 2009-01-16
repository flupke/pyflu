import inspect
from pyflu.shell_color import colorize


__registered_renderers = {}
__enabled = True


def disable():
    global __enabled
    __enabled = False


def enable():
    global __enabled
    __enabled = True


def is_enabled():
    return __enabled


def register_renderer(value_type, func):
    __registered_renderers[value_type] = func


def log(f, ignore_first=False):
    """A decorator to log function calls"""

    def render_value(value):
        value_type = type(value)
        if value_type in __registered_renderers:
            return colorize(__registered_renderers[value_type](value),
                    "yellow")
        return colorize(repr(value), "yellow")

    def _f(*args, **kwargs):
        if not __enabled:
            return f(*args, **kwargs)
        if ignore_first:
            a = [render_value(v) for v in args[1:]]
        else:
            a = [render_value(v) for v in args]
        a += ["%s=%s" % (k, render_value(v)) for k, v in kwargs.items()]
        res = f(*args, **kwargs)
        print "%s(%s) => %s" % (colorize(f.__name__, "green"), 
                ", ".join(a), render_value(res))
        return res

    return _f


def log_method(f):
    """A decorator to log method calls"""
    return log(f, ignore_first=True)


class PhonyMetaClass(type):
    def __new__(cls, cls_name, bases, attrs):
        super_new = super(PhonyMetaClass, cls).__new__
        parents = [b for b in bases if isinstance(b, PhonyMetaClass)]
        if not parents:
            return super_new(cls, cls_name, bases, attrs)
        module = attrs.pop("__module__")
        new_class = super_new(cls, cls_name, bases, {"__module__": module})
        for name, value in attrs.items():
            if inspect.isfunction(value):
                setattr(new_class, name, log_method(value))
            else:
                setattr(new_class, name, value)
        return new_class


class Phony(object):       
    """Make your class inherit from this to make its methods phony"""
    __metaclass__ = PhonyMetaClass

