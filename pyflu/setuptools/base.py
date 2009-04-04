from setuptools import Command


class CommandBaseMetaClass(type):
    def __new__(cls, cls_name, bases, attrs):
        # Create the class
        module = attrs.pop("__module__")
        new_class = super(CommandBaseMetaClass, cls).__new__(
                cls, cls_name, bases, attrs)
        # Merge parent defaults
        defaults = attrs.get("defaults", {})
        parent_defaults = {}
        for base in bases:
            if hasattr(base, "defaults"):
                parent_defaults.update(base.defaults)
        parent_defaults.update(defaults)
        new_class.defaults = parent_defaults
        return new_class


class CommandBase(Command, object):

    __metaclass__ = CommandBaseMetaClass

    defaults = {}
    user_options = []

    def load_defaults(self):
        for k, v in self.defaults.items():
            setattr(self, k, v)

    def initialize_options(self):
        self.load_defaults()

    def finalize_options(self):
        pass
