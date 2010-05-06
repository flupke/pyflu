from nose.tools import assert_equal, assert_raises
from pyflu.jsonalize import JSONAlizable, dumps, loads, NameConflictError, \
        UnregisteredClassError, SchemaValidationError, get_class, copy
import uuid
import numpy as np


class Base(JSONAlizable):

    schema = {
            "foo": None,
            "bar": 123,
            "list": None,
            "dict": None,
        }

    def __init__(self, foo=None, list=None, dict=None, **kwargs):
        super(Base, self).__init__(foo=foo, list=list, dict=dict, **kwargs)
        if foo is None:
            self.foo = Sub()
        if list is None:
            self.list = [Sub(baz="one"), Sub(baz="two")]
        if self.dict is None:
            self.dict = {"one": Sub(baz="one"), "two": Sub(baz="two")}

    def __eq__(self, other):
        for name in self.schema:
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)


class Sub(JSONAlizable):

    schema = {
            "baz": "yarr",
            "foo": None,
        }

    def __eq__(self, other):
        for name in self.schema:
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)


class SubSub(Sub):

    schema = {
            "new_field": None,
            "baz": "no_yarr",
        }


class SubSubSub(SubSub):

    schema = {
            "foo": 123,
            "slices": [slice(None, None, None), slice(1, 2, 3)],
        }


def test_basic():
    """
    Basic initialization and dump/load tests.
    """
    b = Base()
    assert_equal(b.bar, 123)
    b2 = copy(b)
    assert_equal(b2, b)
    s = SubSubSub()
    s2 = copy(s)
    assert_equal(s, s2)
    assert_equal(s2.slices, [slice(None, None, None), slice(1, 2, 3)])


def test_errors():
    def f():
        # Create a class whose name conflicts with Base
        class Foo(JSONAlizable):
            @staticmethod
            def json_class_name():
                return "Base"
        return Foo

    def g():
        # Create a class with a reserved name in its schema
        class Foo(JSONAlizable):
            schema = {
                    "uncall": None,
                }
        return Foo

    assert_raises(NameConflictError, f)
    assert_raises(SchemaValidationError, g)
    assert_raises(UnregisteredClassError, get_class, "gniarjh")
    assert_raises(NameError, Base, unknown=123)


def test_inherit():
    subsub_schema = {
            "new_field": None, 
            "baz": "no_yarr",
            "foo": None,
        }
    subsubsub_schema = {
            "new_field": None, 
            "baz": "no_yarr",
            "foo": 123,
            "slices": [slice(None, None, None), slice(1, 2, 3)],
        }
    assert_equal(SubSub.schema, subsub_schema)
    assert_equal(SubSubSub.schema, subsubsub_schema)


def test_builtin():

    objs = (
            1 + 2j,
            slice(1, 2, 3),
            slice(None, None, None),
            [slice(None, None, None), slice(1, 2, 3)],
            Ellipsis,
            uuid.uuid4(),
        )
    for obj in objs:
        assert_equal(obj, copy(obj))

    array = np.arange(5)
    assert_equal((array == copy(array)).all(), True)

