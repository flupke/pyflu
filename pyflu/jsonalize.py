from copy import deepcopy
import collections
import json
from pyflu.meta.inherit import InheritMeta


class JSONAlizeError(Exception): pass 
class UnserializeError(JSONAlizeError): pass
class UnregisteredClassError(JSONAlizeError): pass
class NameConflictError(JSONAlizeError): pass



class JSONAlizableMeta(InheritMeta):

    inherited_dicts = ("schema",)
    registered_names = {}
    reserved_names = ("uncall", "schema", "json_class_name", "__args__",
            "__class__")

    def __new__(cls, cls_name, bases, attrs):
        new_class = super(JSONAlizableMeta, cls).__new__(cls, cls_name, bases, attrs)
        # Check for name conflicts with other JSONAlizableMeta classes
        new_cls_name = new_class.json_class_name()
        if new_cls_name not in cls.registered_names:
            cls.registered_names[new_cls_name] = new_class
        else:
            raise NameConflictError("can't register JSONAlizable class %s "
                    "under name '%s', it is already used by %s" % (
                        new_cls_name, cls_name,
                        cls.registered_names[new_cls_name].__name__))
        # Validate schema
        for name in new_class.schema:
            if name in cls.reserved_names:
                raise ValueError("can't use reserved name '%s' in %s schema" %
                        (name, new_cls_name))
        return new_class


class JSONAlizableBase(object):
    """
    Mixin class to ease serializing objects to JSON.
    """

    schema = {}
    """
    A mapping storing the serialized attributes, and their default values.

    This parameter is inherited and extended in subclasses.
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
        a dict.

        The default implementation returns the attributes defined in
        :attr:`schema` processed by :func:`serialize`.
        """
        args = {}
        for name in self.schema:
            args[name] = serialize(getattr(self, name))
        return args
            

class JSONAlizable(JSONAlizableBase):

    __metaclass__ = JSONAlizableMeta


def serialize(obj):
    """
    Convert *obj* to its serialized form.
    """
    if hasattr(obj, "uncall") and callable(obj.uncall):
        # JSONAlizable object
        args = obj.uncall()
        data = {
                "__class__": obj.json_class_name(),
                "__args__": args,
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
            ret = cls(**state["__args__"])
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
    stack = JSONAlizableBase.__subclasses__()
    while stack:
        cls = stack.pop()
        if name == cls.json_class_name():
            return cls
        stack += cls.__subclasses__()
    raise UnregisteredClassError("class '%s' is not registered in "
            "serializable classes" % name)


def is_serialized_state(state):
    """
    Returns True if the mapping *state* appears to be a serialized state.
    """
    if isinstance(state, collections.Mapping) and "__class__" in state \
            and "__args__" in state and len(state) == 2:
        return True
    return False    


