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

* Or by registering a class and an associated ``uncall()`` function. This
function takes an instance of the class in parameter and returns the positional
and keyword arguments needed to recreate this instance::

    from pyflu import jsonalize

    class MyClass:

        def __init__(self, a, b):
            self.a = a
            self.b = b

    def uncall_myclass(obj):
        return (obj.a, obj.b), {}

    jsonalize.register(MyClass, uncall_myclass)

You can then dump and load objects with the usual dump(s) and load(s)
functions::

    obj = MyClass()
    dumped_state = jsonalize.dumps(obj)
    obj2 = jsonalize.loads(dumped_state)
    assert obj == obj2

"""
from __future__ import with_statement
try:
    from json import dumps  
    del dumps
    import json
except ImportError:
    import simplejson as json
from copy import deepcopy
from pyflu.meta.inherit import InheritMeta


class JSONAlizeError(Exception): pass 
class NameConflictError(JSONAlizeError): pass
class SchemaValidationError(JSONAlizeError): pass

class UnregisteredClassError(JSONAlizeError):

    def __init__(self, msg, class_name):
        super(UnregisteredClassError, self).__init__(msg)
        self.class_name = class_name


# Classes and uncall() methods registry
registry = {}
reverse_registry = {}


def register(cls, uncall, name=None, constructor=None):
    """
    Register *cls* for auto serialization.

    *uncall* must be a callable taking the instance to be serialized and
    returning the arguments to pass to the constructor. *uncall* should return
    a tuple containing the positionnal and keyword arguments, in an iterable
    and a mapping.

    If *name* is given it is used to as the code to register *cls*. The default
    is to use *cls*' name.

    You can specify *constructor* to alter the way instances are created from
    the serialized state. It should be a callable and will be passed the
    arguments returned by *uncall* when unserializing this type of object.
    """
    if name is None:
        name = cls.__name__
    # Check for name conflicts
    if name in registry:
        conflicting_cls = registry[name][0]
        raise NameConflictError("can't register class %s "
                "under name '%s', it is already used by %s" % 
                (cls.__name__, name, conflicting_cls.__name__))
    registry[name] = (cls, constructor)
    reverse_registry[cls] = (uncall, name)


def unregister(cls, name=None):
    """
    Unregister *cls*.
    """
    if name is None:
        name = cls.__name__
    del registry[name]
    del reverse_registry[cls]
    


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
            # Try to copy the default value with jsonalize's copy(), else use
            # copy.deepcopy()
            try:
                default_copy = copy(default)
            except (JSONAlizeError, TypeError):
                default_copy = deepcopy(default)
            setattr(self, name, 
                    unserialize(kwargs.pop(name, default_copy)))
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
            
    @classmethod
    def load(cls, filename):
        """
        Create a new instance of this class from the contents of the file at
        *filename*.
        """
        with open(filename, "r") as fp:
            ret = load(fp)
        if not isinstance(ret, cls):
            raise TypeError("invalid type serialized type: expected '%s' "
                    "got '%s'" % (cls, type(ret)))
        return ret

    def save(self, filename):
        """
        Save this instance to *filename*.
        """
        with open(filename, "w") as fp:
            dump(self, fp)


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
    elif looks_like_mapping(obj):
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
            # Force kwargs keys to be of str type
            kwargs = {}
            for key, value in state["__kwargs__"].items():
                kwargs[str(key)] = value
            ret = cls(*state["__args__"], **kwargs)
        else:
            # A normal dict
            ret = {}
            for key, value in state.items():
                ret[key] = unserialize(value)
    else:
        # json only returns items of type list or dict, if we get anything else
        # then it's not a serialized state
        ret = state
    return ret


def dump(obj, fp, *args, **kwargs):
    """
    Dump JSON-serializable *obj* to an open file object *fp*.

    The arguments after *obj* are passed directly to json.dump().
    """    
    defaults = {"indent": 4}
    defaults.update(kwargs)
    json.dump(serialize(obj), fp, *args, **defaults)


def dumps(obj, *args, **kwargs):
    """
    Dump JSON-serializable *obj* object to a string.

    The arguments after *obj* are passed directly to json.dumps().
    """    
    defaults = {"indent": 4}
    defaults.update(kwargs)
    return json.dumps(serialize(obj), *args, **defaults)


def load(fp, *args, **kwargs):
    """
    Load an object from a file.

    The arguments are passed directly to json.load().
    """    
    state = json.load(fp, *args, **kwargs)
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
        cls, constructor = registry[name]
    except KeyError:
        raise UnregisteredClassError("'%s' is not a registered "
                "JSONAlizable class name" % name, name)
    if constructor is not None:
        return constructor
    return cls


def is_serialized_state(state):
    """
    Returns True if *state* appears to be a serialized object.
    """
    if looks_like_mapping(state) and len(state) == 3 \
            and "__class__" in state and "__args__" in state \
            and "__kwargs__" in state:
        return True
    return False    


def looks_like_mapping(obj):
    """
    Return True if *obj* looks like a mapping type object.
    """
    meths = ("items", "keys", "values")
    for meth in meths:
        if not callable(getattr(obj, meth, None)):
            return False
    return True


# Register common builtin types
import uuid
import types

def uncall_slice(obj):
    return (obj.start, obj.stop, obj.step), {}

register(slice, uncall_slice)

def uncall_complex(obj):
    return (obj.real, obj.imag), {}

register(complex, uncall_complex)

def uncall_uuid(obj):
    return (), {"hex": obj.hex}

register(uuid.UUID, uncall_uuid)

def uncall_ellipsis(obj):
    return (), {}

def get_ellipsis():
    return Ellipsis

register(types.EllipsisType, uncall_ellipsis, constructor=get_ellipsis)

try:
    import numpy as np

    def uncall_ndarray(obj):
        return (obj.tolist(), obj.dtype.name), {}

    def create_ndarray(data, dtype):
        return np.array(data, str(dtype))

    register(np.ndarray, uncall_ndarray, constructor=create_ndarray)
except ImportError:
    pass
