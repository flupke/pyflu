"""
Classes and utilities to serialize objects to JSON.

There are two ways of using jsonalize:

* By creating a subclass of JSONAlizable and filling its schema::

    from pyflu import jsonalize

    class MyClass(jsonalize.JSONAlizable):
        
        schema = {
                "foo": None,
                "bar": 123,
            }

* By registering a class and an associated uncall function::

    from pyflu import jsonalize

    class MyClass:

        def __init__(self, a, b):
            self.a = a
            self.b = b

    def uncall_myclass(obj):
        return (obj.a, obj.b), {}

    jsonalize.register(MyClass, uncall_myclass)
"""

from copy import deepcopy
import collections
import json
from pyflu.meta.inherit import InheritMeta


class JSONAlizeError(Exception): pass 
class UnregisteredClassError(JSONAlizeError): pass
class NameConflictError(JSONAlizeError): pass
class SchemaValidationError(JSONAlizeError): pass


# Classes and uncall() methods registry
registry = {}
reverse_registry = {}


def register(cls, uncall, name=None):
    """
    Register *cls* for auto serialization.

    *uncall* must be a function equivalent to :meth:`JSONAlizable.uncall`,
    taking a *cls* object in parameter and returning its init arguments.

    If *name* is given it is used to as the code to register *cls*. The default
    is to use *cls*' name.
    """
    if name is None:
        name = cls.__name__
    # Check for name conflicts
    if name in registry:
        conflicting_cls = registry[name]
        raise NameConflictError("can't register class %s "
                "under name '%s', it is already used by %s" % 
                (cls.__name__, name, conflicting_cls.__name__))
    registry[name] = cls
    reverse_registry[cls] = (uncall, name)


class JSONAlizableMeta(InheritMeta):
    """
    Base type of JSONAlizable.

    Inherit and validate schema, register the new class.
    """

    inherited_dicts = ("schema",)
    reserved_names = ("uncall", "schema", "json_class_name", "__args__",
            "__kwargs__", "__class__")

    def __new__(cls, cls_name, bases, attrs):
        new_class = super(JSONAlizableMeta, cls).__new__(cls, cls_name, bases, attrs)
        new_cls_name = new_class.json_class_name()
        # Validate schema
        for name in new_class.schema:
            if name in cls.reserved_names:
                raise SchemaValidationError("can't use reserved name '%s' in "
                        "%s schema" % (name, new_cls_name))
        # Register class
        register(new_class, new_class.uncall, name=new_cls_name)
        return new_class


class JSONAlizableBase(object):
    """
    Mixin class to ease serializing objects to JSON.
    """

    schema = {}
    """
    A mapping storing the serialized attributes, and their default values.

    This attribute is inherited and extended in subclasses.
    """

    def __init__(self, **kwargs):
        """
        Initialize a JSONAlizable instance.

        Takes keyword arguments corresponding to the attributes defined in
        :attr:`schema`. Omitted parameters are set to their default value.
        """
        for name, default in self.schema.items():
            setattr(self, name, 
                    unserialize(kwargs.pop(name, deepcopy(default))))
        if kwargs:
            raise NameError("unknown parameters passed to constructor: %s" %
                    ", ".join(kwargs.keys()))

    @classmethod
    def json_class_name(cls):
        return cls.__name__

    def uncall(self):
        """
        Returns the constructor parameters needed to serialize the instance, as
        a tuple containing positionnal arguments and keyword arguments.

        The default implementation returns the attributes defined in
        :attr:`schema` processed by :func:`serialize`.
        """
        args = {}
        for name in self.schema:
            args[name] = serialize(getattr(self, name))
        return (), args
            

class JSONAlizable(JSONAlizableBase):

    __metaclass__ = JSONAlizableMeta


def serialize(obj):
    """
    Convert *obj* to its serialized form.
    """
    obj_type = type(obj)
    if obj_type in reverse_registry:
        # Registered entry
        uncall, name = reverse_registry[obj_type]
        args, kwargs = uncall(obj)
        data = {
                "__class__": name,
                "__args__": args,
                "__kwargs__": kwargs,
            }
    elif isinstance(obj, collections.Mapping):
        # Mapping like object
        data = {}
        for key, value in obj.iteritems():
            data[key] = serialize(value)
    elif isinstance(obj, (list, tuple)):
        # Sequence object
        data = []
        for value in obj:
            data.append(serialize(value))
    else:
        # Other types
        data = obj
    return data


def unserialize(state):
    """
    Transform a serialized state back to its initial form.
    """
    if isinstance(state, list):
        ret = []
        for value in state:
            ret.append(unserialize(value))
    elif isinstance(state, dict):
        if is_serialized_state(state):
            # Looks to be a serialized class
            cls = get_class(state["__class__"])
            ret = cls(*state["__args__"], **state["__kwargs__"])
        else:
            # A normal dict
            ret = {}
            for key, value in state.items():
                ret[key] = unserialize(value)
    else:
        ret = state
    return ret


def dump(obj, *args, **kwargs):
    """
    Dump JSON-serializable *obj* to a file.

    The arguments after *obj* are passed directly to json.dump().
    """    
    defaults = {"indent": 4}
    defaults.update(kwargs)
    json.dump(serialize(obj), *args, **defaults)


def dumps(obj, *args, **kwargs):
    """
    Dump JSON-serializable *obj* object to a string.

    The arguments after *obj* are passed directly to json.dumps().
    """    
    defaults = {"indent": 4}
    defaults.update(kwargs)
    return json.dumps(serialize(obj), *args, **defaults)


def load(*args, **kwargs):
    """
    Load an object from a file.

    The arguments are passed directly to json.load().
    """    
    state = json.load(*args, **kwargs)
    return unserialize(state)


def loads(*args, **kwargs):
    """
    Load an object from a string.

    The arguments are passed directly to json.loads().
    """    
    state = json.loads(*args, **kwargs)
    return unserialize(state)


def copy(obj):
    """
    Return a copy of 'obj' by serializing it then deserializing it.
    """
    return loads(dumps(obj))


def get_class(name):
    """
    Retrieve a JSONAlizable class by its name.
    """
    try:
        return registry[name]
    except KeyError:
        raise UnregisteredClassError("'%s' is not a registered "
                "JSONAlizable class name" % name)


def is_serialized_state(state):
    """
    Returns True if *state* appears to be a serialized state.
    """
    if isinstance(state, collections.Mapping) and len(state) == 3 \
            and "__class__" in state and "__args__" in state \
            and "__kwargs__" in state:
        return True
    return False    



# Register common builtin types

def uncall_slice(obj):
    return (obj.start, obj.stop, obj.step), {}

register(slice, uncall_slice)

def uncall_complex(obj):
    return (obj.real, obj.imag), {}

register(complex, uncall_complex)
