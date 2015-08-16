import collections
import datetime
import json

import jsonschema
import six

from . import lib
from . import formats


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
        if hasattr(self, "_schema"):
            return self._schema
        self._schema = self.make_schema()
        return self._schema

    def make_schema(self):
        schema = {"type": self._type}
        if self.get("null"):
            schema["type"] = [self._type, "null"]
        if self.get("enum"):
            schema["enum"] = self["enum"]
        if self.get("format"):
            schema["format"] = self["format"]
        if self.get("title"):
            schema["title"] = self["title"]
        if self.get("description"):
            schema["description"] = self["description"]
        if self._definitions:
            definitions = collections.OrderedDict()
            for name, prop in self._definitions.items():
                definitions[prop.get("name", name)] = prop.get_schema()
            schema["definitions"] = definitions
        return schema

    def load(self, text):
        obj = json.loads(text)
        self.validate(obj)
        return self.to_python(obj)

    def dump(self, obj):
        obj = self.to_json(obj)
        self.validate(obj)
        return json.dumps(obj)

    def get_validator(self):
        if hasattr(self, "_validator"):
            return self._validator
        self._validator = self.make_validator()
        return self._validator

    def make_validator(self):
        return _make_validator(self.get_schema())

    def validate(self, obj):
        self.get_validator().validate(obj)

    def to_python(self, value):
        """Convert the value to a real python object"""
        return value

    def to_json(self, value):
        """Convert the value to a JSON compatible value"""
        return value

    def invalidate(self):
        if hasattr(self, "_schema"):
            del self._schema
        if hasattr(self, "_validator"):
            del self._validator


def _types_msg(instance, types, hint=''):
    reprs = []
    for type in types:
        try:
            reprs.append(repr(type["name"]))
        except Exception:
            reprs.append(repr(type))
    return "%r is not of type %s%s" % (instance, ", ".join(reprs), hint)


def _validate_type_draft4(validator, types, instance, schema):
    if isinstance(types, six.string_types):
        types = [types]

    if (
            'string' in types and
            'string' in schema.get('type') and
            schema.get('format') in ['date', 'datetime', 'time', 'duration']
    ):
        if isinstance(instance, six.string_types):
            return
        if schema.get('format') == 'date' and \
                isinstance(instance, datetime.date):
            return
        if schema.get('format') == 'datetime' and \
                isinstance(instance, datetime.datetime):
            return
        if schema.get('format') == 'time' and \
                isinstance(instance, datetime.time):
            return
        if schema.get('format') == 'timestamp' and \
                isinstance(instance, (datetime.timedelta, int, float)):
            return

        json_format_name = schema.get('format')
        datetime_type_name = json_format_name.replace('-', '')
        hint = ' (for format %r strings, use a datetime.%s)' % (
            json_format_name, datetime_type_name
        )
        yield jsonschema.ValidationError(
            _types_msg(instance, types, hint)
        )

    if not any(validator.is_type(instance, type) for type in types):
        yield jsonschema.ValidationError(_types_msg(instance, types))


def _make_validator(schema):
    format_checker = jsonschema.FormatChecker(formats.draft4_format_checkers)
    validator_funcs = jsonschema.Draft4Validator.VALIDATORS
    validator_funcs[u'type'] = _validate_type_draft4
    meta_schema = jsonschema.Draft4Validator.META_SCHEMA
    validator_cls = jsonschema.validators.create(
        meta_schema=meta_schema,
        validators=validator_funcs,
        version="draft4",
    )
    validator_cls.check_schema(schema)
    return validator_cls(schema, format_checker=format_checker)
