import collections
import datetime
import inspect

import jsonschema
import six

from . import formats
from . import lib


class SchemaDict(dict):

    def __init__(self, origin, *args, **kwargs):
        super(SchemaDict, self).__init__(*args, **kwargs)
        self.origin = origin


def constraint(code, hint):
    def decorate(func):
        func._constraint = code
        func._constraint_hint = hint
        return func
    return decorate


class Schema(object):
    _creation_index = 0
    _attrs = None
    _fields = None
    _parent = None

    def __init__(self, _jsonschema=None, **attrs):
        self._creation_index = Schema._creation_index
        Schema._creation_index += 1
        if _jsonschema:
            self._jsonschema = _jsonschema
        self._attrs = dict(self._attrs or {}, **attrs)

        self._validators = self._get_validators()

        if self._validators and 'constraints' not in self._attrs:
            self._attrs['constraints'] = dict([
                (v._constraint, v._constraint_hint)
                for v in self._validators.values()
            ])

    def _get_validators(self):
        validators = inspect.getmembers(
            self, lambda x: hasattr(x, '_constraint')
        )
        return dict([(v._constraint, v) for n, v in validators])

    def get_attr(self, name, default=None, expected=None):
        if self.has_attr(name, expected):
            return getattr(self, name)
        return default

    def has_attr(self, name, expected=None):
        if not hasattr(self, name):
            return False
        if expected:
            if isinstance(getattr(self, name), expected):
                return True
            raise TypeError(
                'Invalid type of \'%s\', expected: %s' % expected
            )
        return True

    def __getattr__(self, name):
        if name not in (self._attrs or ()):
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (
                    self.__class__.__name__, name
                )
            )
        return self._attrs[name]

    @property
    def parent(self):
        return self._parent or self

    @property
    def root(self):
        root = self
        while root._parent:
            root = root._parent
        return root

    @property
    def exclude_tags(self):
        tags = lib.ensure_set(self._attrs.get('exclude_tags'))
        if self._parent:
            tags.update(self._parent.exclude_tags)
        return tags

    def get_jsonschema(self):
        return SchemaDict(self, self._jsonschema)

    def get_tags(self):
        return self.get_attr('tags', set())

    def has_tags(self, tags):
        if not isinstance(tags, (list, tuple, set)):
            tags = {tags}
        if set(self.get_tags()) & set(tags):
            return True
        return False

    def to_raw(self, value):
        """Convert the value to a dict of primitives"""
        return value

    def to_python(self, value):
        """Convert the value to a real python object"""
        return value

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.get_jsonschema() == other
        if isinstance(other, Schema):
            return self.get_jsonschema() == other.get_jsonschema()
        return id(self) == id(other)


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

    def __init__(self, **attrs):
        super(Base, self).__init__(**attrs)
        if self._fields:
            for field in self._fields.values():
                field._parent = self
        if self._definitions:
            for field in self._definitions.values():
                field._parent = self

    def get_jsonschema(self):
        _type = self.get_attr('type', self._type)
        schema = SchemaDict(self, {"type": _type})
        if self.get_attr("null"):
            schema["type"] = lib.ensure_list(_type) + ["null"]
        if self.get_attr("id"):
            schema["id"] = self.get_attr("id")
        if self.get_attr("enum"):
            schema["enum"] = self.get_attr("enum")
        if self.get_attr("format"):
            schema["format"] = self.get_attr("format")
        if self.get_attr("title"):
            schema["title"] = self.get_attr("title")
        if self.get_attr("description"):
            schema["description"] = self.get_attr("description")
        if self.get_attr("default"):
            schema["default"] = self.get_attr("default")
        if self.get_attr("constraints"):
            schema["constraints"] = self.get_attr("constraints")
        if self._definitions:
            definitions = collections.OrderedDict()
            for name, prop in self._definitions.items():
                definitions[prop.get_attr("name", name)] = \
                    prop.get_jsonschema()
            schema["definitions"] = definitions
        return schema

    def get_name(self, default=None):
        return self.get_attr('name', default)

    @property
    def dialect(self):
        return self.root._attrs.get('dialect')


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

        json_format_name = schema.get_attr('format')
        datetime_type_name = json_format_name.replace('-', '')
        hint = ' (for format %r strings, use a datetime.%s)' % (
            json_format_name, datetime_type_name
        )
        yield jsonschema.ValidationError(
            _types_msg(instance, types, hint)
        )

    if not any(validator.is_type(instance, type) for type in types):
        yield jsonschema.ValidationError(_types_msg(instance, types))


def _validate_constraints(validator, constraints, instance, schema):
    for constraint, message in constraints.items():
        for ex in (schema.origin._validators[constraint](instance) or ()):
            yield jsonschema.ValidationError(
                ex.message or message,
                validator_value=ex.against or constraint
            )


def _make_validator(schema):
    format_checker = jsonschema.FormatChecker(formats.draft4_format_checkers)
    validator_funcs = jsonschema.Draft4Validator.VALIDATORS
    validator_funcs['type'] = _validate_type_draft4
    validator_funcs['constraints'] = _validate_constraints
    meta_schema = jsonschema.Draft4Validator.META_SCHEMA
    validator_cls = jsonschema.validators.create(
        meta_schema=meta_schema,
        validators=validator_funcs,
        version="draft4",
    )
    validator_cls.check_schema(schema)
    return validator_cls(schema, format_checker=format_checker)
