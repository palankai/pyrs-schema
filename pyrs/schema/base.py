import collections
import json

import jsonschema
import six

from . import lib


class _Base(object):
    pass


class DeclarativeMetaclass(type):
    def __new__(mcls, name, bases, attrs):
        mcls.update_attrs(attrs, "_attrs", "Attrs")
        mcls.update_attrs(attrs, "_definitions", "Definitions")
        cls = super(DeclarativeMetaclass, mcls).__new__(
            mcls, name, bases, attrs
        )
        cls._attrs = mcls.get_inherited(cls, "_attrs", _Base)
        cls._definitions = mcls.get_inherited(cls, "_definitions", _Base)
        return cls

    @classmethod
    def update_attrs(mcls, attrs, name, clsname):
        Cls = attrs.pop(clsname, None)
        fields = lib.get_public_attributes(Cls)
        if name in attrs:
            attrs[name].update(fields)
        else:
            attrs[name] = fields

    @classmethod
    def get_inherited(mcls, cls, name, base):
        fields = collections.OrderedDict()
        mro = [c for c in cls.__mro__ if issubclass(c, base)]
        for basecls in reversed(mro):
            if hasattr(basecls, name):
                fields.update(getattr(basecls, name))
        return fields


@six.add_metaclass(DeclarativeMetaclass)
class Base(_Base):
    _type = None
    _attrs = {}
    _definitions = {}
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
        if self._definitions:
            definitions = collections.OrderedDict()
            for name, prop in self._definitions.items():
                definitions[prop.get("name", name)] = prop.get_schema()
            schema["definitions"] = definitions
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
