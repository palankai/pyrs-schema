"""
This module introduce the basic schema types.
"""

import datetime
import json

import isodate
import six

from . import base
from . import formats


class String(base.Base):
    _type = "string"

    def make_schema(self, context=None):
        schema = super(String, self).make_schema(context=context)
        if self.get("pattern"):
            schema["pattern"] = self["pattern"]
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
        if self.get('additional') is not None:
            schema['additionalItems'] = self.get('additional')
        if self.get('max_items') is not None:
            schema['maxItems'] = self.get('max_items')
        if self.get('min_items') is not None:
            schema['minItems'] = self.get('min_items')
        if self.get('unique_items') is not None:
            schema['uniqueItems'] = self.get('unique_items')
        if self.get('items'):
            if isinstance(self.get('items'), base.Schema):
                schema['items'] = self.get('items').get_schema(context=context)
            elif isinstance(self.get('items'), (list, tuple)):
                items = []
                for item in self.get('items'):
                    if isinstance(item, base.Schema):
                        items.append(item.get_schema(context=context))
                    else:
                        items.append(item.get_schema(context))
                schema['items'] = items
            else:
                schema['items'] = self.get('items')
        return schema


class Object(base.Base):
    """This is the main class of objects"""
    _type = "object"

    def make_schema(self, context=None):
        schema = super(Object, self).make_schema(context=context)
        if 'description' not in schema and self.__doc__:
            schema['description'] = self.__doc__
        return schema


class Date(String):
    _attrs = {"format": "date"}

    def to_python(self, value, context=None):
        if isinstance(value, datetime.date):
            return value
        try:
            return isodate.parse_date(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid date '%s'" % value)

    def to_json(self, value, context=None):
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

    def to_json(self, value, context=None):
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

    def to_json(self, value, context=None):
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

    def to_json(self, value, context=None):
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
        if isinstance(value, six.string_types):
            value = json.loads(value)
        if isinstance(value, (int, float)):
            return datetime.timedelta(seconds=value)
        if isinstance(value, datetime.timedelta):
            return value
        raise ValueError("Invalid type of timedelta '%s'" % type(value))

    def to_json(self, value, context=None):
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
        if self.get("enum"):
            schema["enum"] = self["enum"]
        return schema


class Ref(base.Base):

    def make_schema(self, context=None):
        schema = super(Ref, self).make_schema(context=context)
        schema.pop("type")
        assert not schema
        return {"$ref": "#/definitions/"+self["ref"]}
