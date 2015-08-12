import unittest

from .. import schema
from .. import types


class TestSchema(unittest.TestCase):

    def test_declarative_schema(self):
        class MyObject(schema.Schema):
            _properties = {
                "int": types.Integer()
            }
            string = types.String(name="String")

        t = MyObject()

        self.assertEqual(
            t.get_schema(),
            {
                "type": "object",
                "properties": {
                    "int": {"type": "integer"},
                    "String": {"type": "string"},
                }
            }
        )

    def test_declarative_schema_validation(self):
        class MyObject(schema.Schema):
            string = types.String(name="String")

        t = MyObject()
        t.validate({"String": "value"})

    def test_subschema(self):
        class MySubObject(schema.Schema):
            integer = types.Integer(name="int")

        class MyObject(schema.Schema):
            string = types.String(name="String")
            sub = MySubObject(null=True)
        t = MyObject()

        self.assertEqual(
            t.get_schema(),
            {
                "type": "object",
                "properties": {
                    "String": {"type": "string"},
                    "sub": {
                        "type": ["object", "null"],
                        "properties": {"int": {"type": "integer"}}
                    },
                }
            }
        )
        t.validate({"String": "hello", "sub": {"int": 12}})
        t.validate({"String": "hello", "sub": None})
