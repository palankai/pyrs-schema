import datetime

from . import base


class String(base.Base):
    _type = "string"

    def _get_schema(self):
        schema = super(String, self)._get_schema()
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
        y, m, d = value.split("-")
        return datetime.date(int(y), int(m), int(d))

    def to_json(self, value):
        if isinstance(value, datetime.date):
            return value.isoformat()


class Enum(base.Base):
    """JSON generic enum class

    :param enum: list of possible values
    :type enum: list
    """

    def _get_schema(self):
        """Ensure the generic schema, remove `types`

        :return: Gives back the schema
        :rtype: dict
        """
        schema = super(Enum, self)._get_schema()
        schema.pop("type")
        if self.get("enum"):
            schema["enum"] = self["enum"]
        return schema


class Ref(base.Base):

    def _get_schema(self):
        schema = super(Ref, self)._get_schema()
        schema.pop("type")
        assert not schema
        return {"$ref": "#/definitions/"+self["ref"]}
