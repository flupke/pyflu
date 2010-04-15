from nose.tools import assert_equal, assert_raises
from pyflu.jsonalize import JSONAlizable, dumps, loads, NameConflictError


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
        return self.bar == other.bar and self.list == other.list and \
                self.foo == other.foo and self.dict == other.dict


class Sub(JSONAlizable):

    schema = {
            "baz": "yarr",
        }

    def __eq__(self, other):
        return self.baz == other.baz


class SubSub(Base):

    schema = {
            "new_field": None,
        }


def test_basic():
    """
    Basic initialization and dump/load tests.
    """
    b = Base()
    assert_equal(b.bar, 123)
    data = dumps(b)
    b2 = loads(data)
    assert_equal(b2, b)


def test_conflict():
    def f():
        class Foo(JSONAlizable):
            @staticmethod
            def json_class_name():
                return "Base"
        return Foo
    assert_raises(NameConflictError, f)


def test_inherit():
    combined = Base.schema.copy()
    combined.update({"new_field": None})
    assert SubSub.schema == combined

