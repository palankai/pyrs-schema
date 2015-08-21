import collections
import datetime
import functools
import json

import isodate
import jsonschema
import six

from . import lib
from . import formats


class Schema(object):
    _creation_index = 0
    _schema = None
    _attrs = None

    def __init__(self, _schema=None, **attrs):
        self._creation_index = Schema._creation_index
        Schema._creation_index += 1
        if _schema and self._schema:
            raise AttributeError("The declared schema shouldn't be redefined")
        if _schema:
            self._schema = _schema
        if self.__class__._attrs is not None:
            self._attrs = self.__class__._attrs.copy()
        else:
            self._attrs = collections.OrderedDict()
        self._attrs.update(attrs)

    def __getitem__(self, name):
        return self._attrs[name]

    def __setitem__(self, name, value):
        self._attrs[name] = value
        self.invalidate()

    def keys(self):
        return self._attrs.keys()

    def get(self, name, default=None):
        return self._attrs.get(name, default)

    def get_schema(self, context=None):
        return self._schema

    def get_tags(self):
        return self.get('tags', [])

    def has_tags(self, tags):
        if not isinstance(tags, (list, tuple, set)):
            tags = {tags}
        if set(self.get_tags()) & set(tags):
            return True
        return False

    def load(self, value, context=None):
        if isinstance(value, six.string_types):
            obj = json.loads(value)
            self.validate_json(obj, context=context)
            self._value = self.to_python(obj, context=context)
            return self._value
        raise ValueError('Unrecognised input format')

    def dump(self, obj, context=None):
        obj = self.to_json(obj, context=context)
        self.validate_json(obj, context=context)
        return self._dump(obj, context=context)

    def _dump(self, obj, context=None):
        default = functools.partial(self._dump_default, context=context)
        return json.dumps(obj, default=default)

    def _dump_default(self, obj, context=None):
        if isinstance(obj, datetime.datetime):
            return isodate.datetime_isoformat(obj)
        elif isinstance(obj, datetime.date):
            return isodate.date_isoformat(obj)
        elif isinstance(obj, datetime.time):
            return isodate.time_isoformat(obj)
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        else:
            raise TypeError(obj)

    def make_validator(self, context=None):
        return _make_validator(self.get_schema(context=context))

    def validate(self, obj, context=None):
        self.validate_json(self.to_json(obj, context=context))

    def validate_json(self, obj, context=None):
        self.get_validator(context=context).validate(obj)

    def get_validator(self, context=None):
        if context:
            return self.make_validator(context=context)
        if getattr(self, "_validator", None):
            return self._validator
        self._validator = self.make_validator(context=context)
        return self._validator

    def to_json(self, value, context=None):
        """Convert the value to a JSON compatible value"""
        return value

    def to_python(self, value, context=None):
        """Convert the value to a real python object"""
        return value

    def to_object(self, value, context=None):
        """Convert the value to python object, make validation possible"""
        return json.loads(value)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.get_schema() == other
        if isinstance(other, Schema):
            return self.get_schema() == other.get_schema()
        return id(self) == id(other)

    def invalidate(self, context=None):
        if hasattr(self, "_validator"):
            self._validator = None


class DeclarativeMetaclass(type):
    def __new__(mcls, name, bases, attrs):
        mcls.update_attrs(attrs, "_attrs", "Attrs")
        mcls.update_attrs(attrs, "_definitions", "Definitions")
        mcls.update_fields(attrs, '_fields', Schema)
        cls = super(DeclarativeMetaclass, mcls).__new__(
            mcls, name, bases, attrs
        )
        cls._attrs = mcls.get_inherited(cls, "_attrs", Schema)
        cls._definitions = mcls.get_inherited(cls, "_definitions", Schema)
        cls._fields = mcls.get_inherited(cls, "_fields", Schema)
        return cls

    @classmethod
    def update_attrs(mcls, attrs, name, clsname):
        Cls = attrs.pop(clsname, None)
        fields = lib.get_public_attributes(Cls)
        if name in attrs and attrs[name] is not None:
            attrs[name].update(fields)
        else:
            attrs[name] = fields

    @classmethod
    def update_fields(mcls, attrs, name, base):
        current_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, base):
                current_fields.append((key, value))
                attrs.pop(key)
        current_fields.sort(key=lambda x: x[1]._creation_index)
        if name in attrs and attrs[name] is not None:
            attrs[name].update(
                collections.OrderedDict(current_fields)
            )
        else:
            attrs[name] = collections.OrderedDict(current_fields) or None
        pass

    @classmethod
    def get_inherited(mcls, cls, name, base, remove_if_none=False):
        fields = collections.OrderedDict()
        mro = [c for c in cls.__mro__ if issubclass(c, base)]
        for basecls in reversed(mro):
            if hasattr(basecls, name) and getattr(basecls, name) is not None:
                fields.update(getattr(basecls, name))
            if remove_if_none:
                for attr, value in basecls.__dict__.items():
                    if value is None and attr in fields:
                        fields.pop(attr)
        return fields or None


@six.add_metaclass(DeclarativeMetaclass)
class Base(Schema):
    _type = None
    _attrs = None
    _definitions = None
    _properties = None

    def __init__(self, **attrs):
        super(Base, self).__init__(**attrs)

    def get_schema(self, context=None):
        if context:
            self.make_schema(context=context)
        if getattr(self, "_schema", None):
            return self._schema
        self._schema = self.make_schema(context=context)
        return self._schema

    def make_schema(self, context=None):
        if context is None:
            context = {}
        attr_exclude_tags = lib.ensure_set(self.get('exclude_tags'))
        ctx_exclude_tags = lib.ensure_set(context.get('exclude_tags'))
        exclude_tags = attr_exclude_tags | ctx_exclude_tags
        if attr_exclude_tags:
            context = context.copy()
            context['exclude_tags'] = exclude_tags

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
        if self.get("default"):
            schema["default"] = self["default"]
        if self._definitions:
            definitions = collections.OrderedDict()
            for name, prop in self._definitions.items():
                definitions[prop.get("name", name)] = \
                    prop.get_schema(context=context)
            schema["definitions"] = definitions
        if self._fields is not None:
            required = []
            properties = collections.OrderedDict()
            for key, prop in self._fields.items():
                if key in self.get('exclude', []):
                    continue
                if self.get('include'):
                    if key not in lib.ensure_list(self.get('include')):
                        continue
                if exclude_tags and prop.has_tags(exclude_tags):
                    continue
                name = prop.get("name", key)
                properties[name] = prop.get_schema(context=context)
                if prop.get('required'):
                    required.append(name)
            schema["properties"] = properties
            if required:
                schema['required'] = sorted(required)
        return schema

    def get_name(self, default=None):
        return self.get('name', default)

    def load(self, value, context=None):
        if isinstance(value, dict):
            by_name = {}
            for field, prop in self._fields.items():
                by_name[prop.get('name', field)] = prop
            for field in list(set(value) & set(by_name)):
                value[field] = by_name[field].to_object(
                    value[field], context=context
                )
            self.validate_json(value, context=context)
            self._value = self.to_python(value, context=context)
            return self._value
        return super(Base, self).load(value, context=context)

    def to_python(self, value, context=None):
        """Convert the value to a real python object"""
        if self._fields is not None:
            res = {}
            for field, schema in self._fields.items():
                name = schema.get('name', field)
                if name in value:
                    res[field] = schema.to_python(
                        value.pop(name), context=context
                    )
            res.update(value)
            return res
        return value

    def to_json(self, value, context=None):
        """Convert the value to a JSON compatible value"""
        if value is None:
            return None
        if self._fields is not None:
            res = {}
            value = value.copy()
            for field in list(set(value) & set(self._fields)):
                schema = self._fields.get(field)
                res[schema.get('name', field)] = \
                    schema.to_json(value.pop(field), context=context)
            res.update(value)
            return res
        return value

    def invalidate(self, context=None):
        super(Base, self).invalidate(context=None)
        if hasattr(self, "_schema"):
            self._schema = None


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
            schema.get('format') in [
                'date', 'datetime', 'time', 'duration', 'timestamp'
            ]
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
        if schema.get('format') == 'duration' and \
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
