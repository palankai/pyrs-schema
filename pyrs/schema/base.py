import collections
import json

import jsonschema
import six

from . import lib


class _Base(object):
    pass


class DeclarativeMetaclass(type):
    def __new__(mcls, name, bases, attrs):
        Attrs = attrs.pop('Attrs', None)
        attributes = lib.get_public_attributes(Attrs)
        if "_attrs" in attrs:
            attrs["_attrs"].update(attributes)
        else:
            attrs["_attrs"] = attributes
        cls = super(DeclarativeMetaclass, mcls).__new__(
            mcls, name, bases, attrs
        )
        attrs_def = collections.OrderedDict()
        mro = [c for c in cls.__mro__ if issubclass(c, _Base)]
        for basecls in reversed(mro):
            if hasattr(basecls, "_attrs"):
                attrs_def.update(basecls._attrs)
        cls._attrs = attrs_def
        return cls


@six.add_metaclass(DeclarativeMetaclass)
class Base(_Base):
    _type = None
    _attrs = {}
    _creation_index = 0

    def __init__(self, **attrs):
        self._creation_index = Base._creation_index
        Base._creation_index += 1
        self.attrs = self.__class__._attrs.copy()
        self.attrs.update(attrs)

    def __getitem__(self, name):
        return self.attrs[name]

    def __setitem__(self, name, value):
        self.attrs[name] = value

    def keys(self):
        return self.attrs.keys()

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    def get_schema(self):
        schema = {"type": self._type}
        if self.get("null"):
            schema["type"] = [self._type, "null"]
        if self.get("enum"):
            schema["enum"] = self["enum"]
        return schema

    def loads(self, text):
        obj = json.loads(text)
        self.validate(obj)
        return obj

    def dumps(self, obj):
        self.validate(obj)
        return json.dumps(obj)

    def validate(self, obj):
        jsonschema.validate(obj, self.get_schema())
