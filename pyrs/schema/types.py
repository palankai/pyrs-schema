import datetime

import isodate
import six

from . import base
from . import formats


class String(base.Base):
    _type = "string"

    def make_schema(self):
        schema = super(String, self).make_schema()
        if self.get("pattern"):
            schema["pattern"] = self["pattern"]
        return schema


class Integer(base.Base):
    _type = "integer"


class Number(base.Base):
    _type = "number"


class Boolean(base.Base):
    _type = "boolean"


class Array(base.Base):
    _type = "array"


class Date(String):
    _attrs = {"format": "date"}

    def to_python(self, value):
        if isinstance(value, datetime.date):
            return value
        try:
            return isodate.parse_date(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid date '%s'" % value)

    def to_json(self, value):
        if isinstance(value, datetime.date):
            return isodate.date_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_python(value)
            return value


class Time(String):
    _attrs = {"format": "time"}

    def to_python(self, value):
        if isinstance(value, datetime.time):
            return value
        try:
            return isodate.parse_time(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid time '%s'" % value)

    def to_json(self, value):
        if isinstance(value, datetime.time):
            return isodate.time_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_pyton(value)
            return value


class DateTime(String):
    _attrs = {"format": "datetime"}

    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            return value
        try:
            return formats.parse_datetime(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid datetime '%s'" % value)

    def to_json(self, value):
        if isinstance(value, datetime.time):
            return isodate.datetime_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_pyton(value)
            return value


class Duration(String):
    _attrs = {"format": "duration"}

    def to_python(self, value):
        if isinstance(value, (int, float)):
            return datetime.timedelta(seconds=value)
        try:
            return formats.parse_duration(value)
        except isodate.ISO8601Error:
            raise ValueError("Invalid duration '%s'" % value)

    def to_json(self, value):
        if isinstance(value, datetime.timedelta):
            return isodate.duration_isoformat(value)
        if isinstance(value, (int, float)):
            return isodate.duration_isoformat(
                datetime.timedelta(seconds=value)
            )
        if isinstance(value, six.string_types):
            self.to_pyton(value)
            return value


class TimeDelta(Number):

    def to_python(self, value):
        if isinstance(value, (int, float)):
            return datetime.timedelta(seconds=value)
        if isinstance(value, datetime.timedelta):
            return value
        raise ValueError("Invalid type of timedelta '%s'" % type(value))

    def to_json(self, value):
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

    def make_schema(self):
        """Ensure the generic schema, remove `types`

        :return: Gives back the schema
        :rtype: dict
        """
        schema = super(Enum, self).make_schema()
        schema.pop("type")
        if self.get("enum"):
            schema["enum"] = self["enum"]
        return schema


class Ref(base.Base):

    def make_schema(self):
        schema = super(Ref, self).make_schema()
        schema.pop("type")
        assert not schema
        return {"$ref": "#/definitions/"+self["ref"]}
