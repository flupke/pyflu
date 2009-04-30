from setuptools import Command


def opts_dict(opts):
    """
    Convert an user_options style list to a dictionnary indexed by the long 
    option name.
    """
    return dict([(x[0], x) for x in opts])


class CommandBaseMetaClass(type):

    def __new__(cls, cls_name, bases, attrs):
        # Create the class
        module = attrs.pop("__module__")
        new_class = super(CommandBaseMetaClass, cls).__new__(
                cls, cls_name, bases, attrs)

        # Inherit base classes options attributes
        defaults = attrs.get("defaults", {})
        user_options = opts_dict(attrs.get("user_options", []))
        boolean_options = set(attrs.get("boolean_options", []))
        parent_defaults = {}
        parent_user_options = {}
        for base in bases:
            if hasattr(base, "defaults"):
                parent_defaults.update(base.defaults)
            if hasattr(base, "user_options"):
                parent_user_options.update(opts_dict(base.user_options))
            if hasattr(base, "boolean_options"):
                boolean_options.update(set(base.boolean_options))
        parent_defaults.update(defaults)
        parent_user_options.update(user_options)
        new_class.defaults = parent_defaults
        new_class.user_options = parent_user_options.values()
        new_class.boolean_options = list(boolean_options)

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
