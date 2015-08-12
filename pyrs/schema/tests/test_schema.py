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
