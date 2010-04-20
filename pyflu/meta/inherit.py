class InheritMeta(type):
    """
    A meta class for types defining dict-like list of attributes that can be
    inherited by subclasses.
    
    Subtypes must define an iterable class attribute named *inherited_dicts*,
    containing the attributes names to be inherited.
    """

    def __new__(cls, cls_name, bases, attrs):
        super_new = super(InheritMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, InheritMeta)]
        if not parents:
            # Not a subclass of InheritMeta, don't do anything special
            return super_new(cls, cls_name, bases, attrs)
        # Inherit parent dicts
        for dict_name in cls.inherited_dicts:
            combined = {}
            for base in parents:
                combined.update(getattr(base, dict_name, {}))
            combined.update(attrs.get(dict_name, {}))
            attrs[dict_name] = combined
        return super_new(cls, cls_name, bases, attrs)
    
