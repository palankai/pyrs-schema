import unittest

from .. import schema
from .. import types


class TestSchemaValidation(unittest.TestCase):

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

    def test_definitions(self):
        class MySubObject(schema.Schema):
            integer = types.Integer(name="int")

        class MyObject(schema.Schema):
            string = types.String(name="String")
            sub = types.Ref(ref="sub")

            class Definitions:
                sub = MySubObject(null=True)
        t = MyObject()

        self.assertEqual(
            t.get_schema(),
            {
                "type": "object",
                "properties": {
                    "String": {"type": "string"},
                    "sub": {"$ref": "#/definitions/sub"}
                },
                "definitions": {
                    "sub": {
                        "type": ["object", "null"],
                        "properties": {"int": {"type": "integer"}}
                    }
                }
            }
        )
        t.validate({"String": "hello", "sub": {"int": 12}})
        t.validate({"String": "hello", "sub": None})

    def test_deep_definitions(self):
        class MySubObject(schema.Schema):
            integer = types.Ref(ref="integer")

            class Definitions:
                integer = types.Integer()

        class MyObject(schema.Schema):
            string = types.String(name="String")
            sub = types.Ref(ref="sub")

            class Definitions:
                sub = MySubObject(null=True)
        t = MyObject()

        self.assertEqual(
            t.get_schema(),
            {
                "type": "object",
                "properties": {
                    "String": {"type": "string"},
                    "sub": {"$ref": "#/definitions/sub"}
                },
                "definitions": {
                    "sub": {
                        "type": ["object", "null"],
                        "properties": {
                            "integer": {"$ref": "#/definitions/integer"}
                        },
                        "definitions": {"integer": {"type": "integer"}}
                    }
                }
            }
        )
        t.validate({"String": "hello", "sub": {"int": 12}})
        t.validate({"String": "hello", "sub": None})


class TestSchemaToPython(unittest.TestCase):

    def test_schema_to_python(self):
        class MyObject(schema.Schema):
            _properties = {
                "int": types.Integer()
            }
            string = types.String(name="NewName")

        t = MyObject()
        p = t.to_python({"int": 1, "NewName": "hi", 'x': 'y'})
        self.assertEqual(p, {"int": 1, "string": "hi", 'x': 'y'})

    def test_special_type(self):

        class Spec(types.String):
            def to_python(self, src):
                if src.lower() == "yes":
                    return True
                else:
                    return False

        class MyObject(schema.Schema):
            username = types.String()
            can_login = Spec()

        t = MyObject()
        p = t.to_python({'username': 'user', 'can_login': 'Yes'})
        self.assertEqual(p, {'username': 'user', 'can_login': True})


class TestSchemaToJson(unittest.TestCase):

    def test_schema_to_json(self):
        class MyObject(schema.Schema):
            _properties = {
                "int": types.Integer()
            }
            string = types.String(name="NewName")

        t = MyObject()
        p = t.to_json({"int": 1, "string": "hi", "unknown": "x"})
        self.assertEqual(p, {"int": 1, "NewName": "hi", 'unknown': 'x'})

    def test_special_type(self):

        class Spec(types.String):
            def to_json(self, src):
                return "*******"

        class MyObject(schema.Schema):
            string = types.String()
            password = Spec()

        t = MyObject()
        p = t.to_json({'username': 'user', 'password': 'secret'})
        self.assertEqual(p, {'username': 'user', 'password': '*******'})
