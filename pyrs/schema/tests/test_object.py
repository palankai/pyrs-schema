import unittest

import jsonschema

from .. import types


class TestSchemaValidation(unittest.TestCase):

    def test_declarative_schema(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="String")

        t = MyObject()

        self.assertEqual(
            t.get_schema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                    "String": {"type": "string"},
                }
            }
        )

    def test_description_as_docstring(self):
        class MyObject(types.Object):
            """Description"""
            num = types.Integer()

        t = MyObject()

        self.assertEqual(
            t.get_schema(),
            {
                'type': 'object',
                'description': "Description",
                'properties': {'num': {'type': 'integer'}}
            }
        )

    def test_declarative_schema_required(self):
        class MyObject(types.Object):
            num = types.Integer(required=True)
            string = types.String(name="String", required=True)

        t = MyObject()
        s = t.get_schema()
        expected = {
            "type": "object",
            "properties": {
                "num": {"type": "integer"},
                "String": {"type": "string"},
            },
            "required": ['String', 'num']
        }
        self.assertEqual(
            s, expected
        )

    def test_declarative_schema_validation(self):
        class MyObject(types.Object):
            string = types.String(name="String")

        t = MyObject()
        t.validate({"string": "value"})

    def test_subschema(self):
        class MySubObject(types.Object):
            integer = types.Integer(name="int")

        class MyObject(types.Object):
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
        t.validate({"string": "hello", "sub": {"int": 12}})
        t.validate({"string": "hello", "sub": None})

    def test_definitions(self):
        class MySubObject(types.Object):
            integer = types.Integer(name="int")

        class MyObject(types.Object):
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
        class MySubObject(types.Object):
            integer = types.Ref(ref="integer")

            class Definitions:
                integer = types.Integer()

        class MyObject(types.Object):
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
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="NewName")

        t = MyObject()
        p = t.to_python({"num": 1, "NewName": "hi", 'x': 'y'})
        self.assertEqual(p, {"num": 1, "string": "hi", 'x': 'y'})

    def test_special_type(self):

        class Spec(types.String):
            def to_python(self, src, context=None):
                if src.lower() == "yes":
                    return True
                else:
                    return False

        class MyObject(types.Object):
            username = types.String()
            can_login = Spec()

        t = MyObject()
        p = t.to_python({'username': 'user', 'can_login': 'Yes'})
        self.assertEqual(p, {'username': 'user', 'can_login': True})


class TestSchemaToJson(unittest.TestCase):

    def test_schema_to_json(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="NewName")

        t = MyObject()
        p = t.to_json({"num": 1, "string": "hi", "unknown": "x"})
        self.assertEqual(p, {"num": 1, "NewName": "hi", 'unknown': 'x'})

    def test_special_type(self):

        class Spec(types.String):
            def to_json(self, src, context=None):
                return "*******"

        class MyObject(types.Object):
            string = types.String()
            password = Spec()

        t = MyObject()
        p = t.to_json({'username': 'user', 'password': 'secret'})
        self.assertEqual(p, {'username': 'user', 'password': '*******'})


class TestSchemaAdditional(unittest.TestCase):

    def test_schema(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="String")

            class Attrs:
                additional = False

        t = MyObject()

        self.assertEqual(
            t.get_schema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                    "String": {"type": "string"},
                },
                "additionalProperties": False
            }
        )

    def test_validation(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="String")

            class Attrs:
                additional = False

        t = MyObject()
        t.validate({'num': 12})
        t.validate({'string': 'string'})
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate({'string': 'string', 'extra': 'invalid'})


class TestSchemaPattern(unittest.TestCase):

    def test_schema(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="String")

            class Attrs:
                additional = False
                min_properties = 2
                max_properties = 4
                patterns = {
                    '[a-z]{2}': types.String()
                }

        t = MyObject()

        self.assertEqual(
            t.get_schema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                    "String": {"type": "string"},
                },
                "additionalProperties": False,
                'minProperties': 2,
                'maxProperties': 4,
                'patternProperties': {
                    '[a-z]{2}': {'type': 'string'}
                }
            }
        )

    def test_validation(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="String")

            class Attrs:
                additional = False
                patterns = {
                    'name_[a-z]{2}': types.String()
                }

        t = MyObject()
        t.validate({'num': 12})
        t.validate({'string': 'string'})
        t.validate({'string': 'string', 'name_en': 'English'})
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate({'string': 'string', 'extra': 'invalid'})


class TestSchemaLoadForm(unittest.TestCase):

    def test_load_form(self):
        class MySub(types.Object):
            sub = types.Integer()

        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="NewName")
            arr = types.Array()
            sub = MySub()

        t = MyObject()
        form = {
            'num': '1',
            'NewName': 'hi',
            'sub': '{"sub": 1}',
            'arr': '[1, 2, "hi"]',
            'unknown': '{"any": "value"}'
        }
        r = t.load(form)
        self.assertEqual(r, {
            "num": 1,
            "string": "hi",
            'sub': {'sub': 1},
            'arr': [1, 2, 'hi'],
            'unknown': '{"any": "value"}'
        })
