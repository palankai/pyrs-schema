from . import base


class String(base.Base):
    _type = "string"

    def get_schema(self):
        schema = super(String, self).get_schema()
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


class Enum(base.Base):

    def get_schema(self):
        schema = super(Enum, self).get_schema()
        schema.pop("type")
        if self.get("enum"):
            schema["enum"] = self["enum"]
        return schema
