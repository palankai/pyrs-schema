"""
This module introduce the basic schema types.
"""
import collections
import datetime

import isodate
import six

from . import base
from . import formats
from . import lib


class String(base.Base):
    _type = "string"

    def make_schema(self, context=None):
        schema = super(String, self).make_schema(context=context)
        if self.get_attr("pattern"):
            schema["pattern"] = self.get_attr("pattern")
        return schema

    def to_object(self, value, context=None):
        return value


class Integer(base.Base):
    _type = "integer"


class Number(base.Base):
    _type = "number"


class Boolean(base.Base):
    _type = "boolean"


class Array(base.Base):
    """
    Successful validation of an array instance with regards to these two
    keywords is determined as follows:

    if "items" is not present, or its value is an object, validation of
    the instance always succeeds, regardless of the value of "additional"

    if the value of "additional" is boolean value true or an object,
    validation of the instance always succeeds;

    if the value of "additional" is boolean value false and the value of
    "items" is an array, the instance is valid if its size is less than,
    or equal to, the size of "items".

    Array specific options:
        min_items:
            An array instance is valid against "min_items" if its size is
            greater than, or equal to, the value of this keyword.
        max_items:
            An array instance is valid against "max_items" if its size is
            less than, or equal to, the value of this keyword.
        unique_items:
            If this keyword has boolean value false, the instance validates
            successfully. If it has boolean value true, the instance validates
            successfully if all of its elements are unique.
    """
    _type = "array"

    def make_schema(self, context=None):
        schema = super(Array, self).make_schema(context=context)
        if self.get_attr('additional') is not None:
            schema['additionalItems'] = self.get_attr('additional')
        if self.get_attr('max_items') is not None:
            schema['maxItems'] = self.get_attr('max_items')
        if self.get_attr('min_items') is not None:
            schema['minItems'] = self.get_attr('min_items')
        if self.get_attr('unique_items') is not None:
            schema['uniqueItems'] = self.get_attr('unique_items')
        if self.get_attr('items'):
            if isinstance(self.get_attr('items'), (list, tuple)):
                schema['items'] = [
                    s.get_schema(context=context)
                    for s in self.get_attr('items')
                ]
            else:
                schema['items'] = \
                    self.get_attr('items').get_schema(context=context)
        return schema


class Object(base.Base):
    """Declarative schema object

    Object specific attributes:
        additional:
            boolean value: enable or disable extra items on the object
            schema: items which are valid against the schema allowed to extend
            **false by default**
        min_properties:
            An object instance is valid against `min_properties` if its number
            of properties is greater than, or equal to, the value.
        max_properties:
            An object instance is valid against `max_properties` if its number
            of properties is less than, or equal to, the value.
        pattern:
            Should be a dict where the keys are valid regular excpressions
            and the values are schema instances. The object instance is valid
            if the extra properties (which are not listed as property) valid
            against the schema while name is match on the pattern.

        Be careful, the pattern sould be explicit as possible, if the pattern
        match on any normal property the validation should be successful
        against them as well.

        A normal object should looks like the following:

        .. code:: python

            class Translation(types.Object):
                keyword = types.String()
                value = types.String()

                class Attrs:
                    additional = False
                    patterns = {
                        'value_[a-z]{2}': types.String()
                    }
    """
    _type = "object"
    _attrs = {'additional': False}

    def __init__(self, extend=None, **attrs):
        super(Object, self).__init__(**attrs)
        if extend:
            self._fields.update(extend)

    def make_schema(self, context=None):
        schema = super(Object, self).make_schema(context=context)
        if self.get_attr('additional') is not None:
            if isinstance(self.get_attr('additional'), bool):
                schema['additionalProperties'] = self.get_attr('additional')
            else:
                schema['additionalProperties'] = \
                    self.get_attr('additional').get_schema(context=context)
        if self.get_attr('min_properties') is not None:
            schema['minProperties'] = self.get_attr('min_properties')
        if self.get_attr('max_properties') is not None:
            schema['maxProperties'] = self.get_attr('max_properties')
        if self.get_attr('patterns'):
            patterns = collections.OrderedDict()
            for reg, pattern in self.get_attr('patterns').items():
                patterns[reg] = pattern.get_schema(context=context)
            schema['patternProperties'] = patterns
        if context is None:
            context = {}
        attr_exclude_tags = lib.ensure_set(self.get_attr('exclude_tags'))
        ctx_exclude_tags = lib.ensure_set(context.get('exclude_tags'))
        exclude_tags = attr_exclude_tags | ctx_exclude_tags
        if attr_exclude_tags:
            context = context.copy()
            context['exclude_tags'] = exclude_tags
        required = []
        properties = collections.OrderedDict()
        for key, prop in self._fields.items():
            if key in self.get_attr('exclude', []):
                continue
            if self.get_attr('include'):
                if key not in lib.ensure_list(self.get_attr('include')):
                    continue
            if exclude_tags and prop.has_tags(exclude_tags):
                continue
            name = prop.get_attr("name", key)
            properties[name] = prop.get_schema(context=context)
            if prop.get_attr('required'):
                required.append(name)
        schema["properties"] = properties
        if required:
            schema['required'] = sorted(required)
        return schema

    @property
    def properties(self):
        return self._fields

    def extend(self, properties, context=None):
        """Extending the exist same with new properties.
        If you want to extending with an other schema, you should
        use the other schame `properties`
        """
        self._fields.update(properties)
        self.invalidate(context=None)

    def load(self, value, context=None):
        if isinstance(value, dict):
            value = value.copy()
            by_name = {}
            for field, prop in self._fields.items():
                by_name[prop.get_attr('name', field)] = prop
            for field in list(set(value) & set(by_name)):
                value[field] = by_name[field].to_object(
                    value[field], context=context
                )
            self.validate_dict(value, context=context)
            self._value = self.to_python(value, context=context)
            return self._value
        return super(Object, self).load(value, context=context)

    def to_python(self, value, context=None):
        """Convert the value to a real python object"""
        value = value.copy()
        res = {}
        for field, schema in self._fields.items():
            name = schema.get_attr('name', field)
            if name in value:
                res[field] = schema.to_python(
                    value.pop(name), context=context
                )
        res.update(value)
        return res

    def to_dict(self, value, context=None):
        """Convert the value to a JSON compatible value"""
        if value is None:
            return None
        res = {}
        value = value.copy()
        for field in list(set(value) & set(self._fields)):
            schema = self._fields.get(field)
            res[schema.get_attr('name', field)] = \
                schema.to_dict(value.pop(field), context=context)
        res.update(value)
        return res


class Date(String):
    _attrs = {"format": "date"}

    def to_python(self, value, context=None):
        if isinstance(value, datetime.date):
            return value
        try:
            return isodate.parse_date(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid date '%s'" % value)

    def to_dict(self, value, context=None):
        if isinstance(value, datetime.date):
            return isodate.date_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_python(value)
            return value


class Time(String):
    _attrs = {"format": "time"}

    def to_python(self, value, context=None):
        if isinstance(value, datetime.time):
            return value
        try:
            return isodate.parse_time(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid time '%s'" % value)

    def to_dict(self, value, context=None):
        if isinstance(value, datetime.time):
            return isodate.time_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_pyton(value)
            return value


class DateTime(String):
    _attrs = {"format": "datetime"}

    def to_python(self, value, context=None):
        if isinstance(value, datetime.datetime):
            return value
        try:
            return formats.parse_datetime(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid datetime '%s'" % value)

    def to_dict(self, value, context=None):
        if isinstance(value, datetime.time):
            return isodate.datetime_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_pyton(value)
            return value


class Duration(String):
    _attrs = {"format": "duration"}

    def to_python(self, value, context=None):
        if isinstance(value, (int, float)):
            return datetime.timedelta(seconds=value)
        try:
            return isodate.parse_duration(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid duration '%s'" % value)

    def to_dict(self, value, context=None):
        if isinstance(value, datetime.timedelta):
            return isodate.duration_isoformat(value)
        if isinstance(value, (int, float)):
            return isodate.duration_isoformat(
                datetime.timedelta(seconds=value)
            )
        if isinstance(value, six.string_types):
            self.to_python(value)
            return value


class TimeDelta(Number):

    def to_python(self, value, context=None):
        if isinstance(value, (int, float)):
            return datetime.timedelta(seconds=value)
        if isinstance(value, datetime.timedelta):
            return value
        raise ValueError("Invalid type of timedelta '%s'" % type(value))

    def to_dict(self, value, context=None):
        if isinstance(value, datetime.timedelta):
            return value.total_seconds()
        if isinstance(value, (int, float)):
            return value
        raise ValueError("Invalid type of timedelta '%s'" % type(value))


class Enum(base.Base):
    """JSON generic enum class

    :param enum: list of possible values
    :type enum: list
    """

    def make_schema(self, context=None):
        """Ensure the generic schema, remove `types`

        :return: Gives back the schema
        :rtype: dict
        """
        schema = super(Enum, self).make_schema(context=None)
        schema.pop("type")
        if self.get_attr("enum"):
            schema["enum"] = self.get_attr("enum")
        return schema


class Ref(base.Base):

    def make_schema(self, context=None):
        schema = super(Ref, self).make_schema(context=context)
        schema.pop("type")
        assert not schema
        return {"$ref": "#/definitions/"+self.get_attr("ref")}
