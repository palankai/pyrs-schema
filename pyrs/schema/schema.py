import collections

import six

from . import base


class DeclarativeSchemaMetaclass(base.DeclarativeMetaclass):
    def __new__(mcls, name, bases, attrs):
        current_properties = []
        for key, value in list(attrs.items()):
            if isinstance(value, base.Base):
                current_properties.append((key, value))
                attrs.pop(key)
        current_properties.sort(key=lambda x: x[1]._creation_index)
        if "_properties" in attrs:
            attrs['_properties'].update(
                collections.OrderedDict(current_properties)
            )
        else:
            attrs['_properties'] = collections.OrderedDict(current_properties)
        cls = super(DeclarativeSchemaMetaclass, mcls).__new__(
            mcls, name, bases, attrs
        )
        declared_properties = collections.OrderedDict()
        mro = [c for c in cls.__mro__ if issubclass(c, base.Base)]
        for basecls in reversed(mro):
            if hasattr(basecls, "_properties"):
                declared_properties.update(basecls._properties)
            for attr, value in basecls.__dict__.items():
                if value is None and attr in declared_properties:
                    declared_properties.pop(attr)
        cls._properties = declared_properties
        return cls


@six.add_metaclass(DeclarativeSchemaMetaclass)
class Schema(base.Base):
    _type = "object"
    _properties = {}

    def _get_schema(self):
        schema = super(Schema, self)._get_schema()
        properties = collections.OrderedDict()
        for key, prop in self._properties.items():
            properties[prop.get("name", key)] = prop.get_schema()
        schema["properties"] = properties
        return schema

    def to_python(self, src):
        res = {}
        for field, schema in self._properties.items():
            name = schema.get('name', field)
            if name in src:
                res[field] = schema.to_python(src.pop(name))
        res.update(src)
        return res

    def to_json(self, src):
        res = {}
        for field in list(set(src) & set(self._properties)):
            schema = self._properties.get(field)
            res[schema.get('name', field)] = schema.to_json(src.pop(field))
        res.update(src)
        return res
