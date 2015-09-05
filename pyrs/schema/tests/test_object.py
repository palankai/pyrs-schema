import unittest

from .. import types


class TestSchemaValidation(unittest.TestCase):

    def test_declarative_schema(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="String")

        t = MyObject(additional=None)

        self.assertEqual(
            t.get_jsonschema(),
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
            num = types.Integer()

            class Attrs:
                description = "Description"

        t = MyObject(additional=None)

        self.assertEqual(
            t.get_jsonschema(),
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

        t = MyObject(additional=None)
        s = t.get_jsonschema()
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

    def test_subschema(self):
        class MySubObject(types.Object):
            integer = types.Integer(name="int")

        class MyObject(types.Object):
            string = types.String(name="String")
            sub = MySubObject(null=True, additional=None)
        t = MyObject(additional=None)

        self.assertEqual(
            t.get_jsonschema(),
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

    def test_definitions(self):
        class MySubObject(types.Object):
            integer = types.Integer(name="int")

        class MyObject(types.Object):
            string = types.String(name="String")
            sub = types.Ref(ref="sub")

            class Definitions:
                sub = MySubObject(null=True, additional=None)
        t = MyObject(additional=None)

        self.assertEqual(
            t.get_jsonschema(),
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

    def test_deep_definitions(self):
        class MySubObject(types.Object):
            integer = types.Ref(ref="integer")

            class Definitions:
                integer = types.Integer()

        class MyObject(types.Object):
            string = types.String(name="String")
            sub = types.Ref(ref="sub")

            class Definitions:
                sub = MySubObject(null=True, additional=None)
        t = MyObject(additional=None)

        self.assertEqual(
            t.get_jsonschema(),
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
            def to_python(self, src, path='', context=None):
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

    def test_schema_to_raw(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="NewName")

        t = MyObject()
        p = t.to_raw({"num": 1, "string": "hi", "unknown": "x"})
        self.assertEqual(p, {"num": 1, "NewName": "hi", 'unknown': 'x'})

    def test_special_type(self):

        class Spec(types.String):
            def to_raw(self, src, context=None):
                return "*******"

        class MyObject(types.Object):
            string = types.String()
            password = Spec()

        t = MyObject()
        p = t.to_raw({'username': 'user', 'password': 'secret'})
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
            t.get_jsonschema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                    "String": {"type": "string"},
                },
                "additionalProperties": False
            }
        )


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
            t.get_jsonschema(),
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


class TestSchemaExtend(unittest.TestCase):

    def test_procedural_extend(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String()

            class Attrs:
                additional = False

        t = MyObject()
        t.extend({
            'title': types.String()
        })

        self.assertEqual(
            t.get_jsonschema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                    "string": {"type": "string"},
                    "title": {"type": "string"},
                },
                'additionalProperties': False,
            }
        )

    def test_initial_extend(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String()

            class Attrs:
                additional = False

        t = MyObject(extend={'title': types.String()})
        self.assertEqual(
            t.get_jsonschema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                    "string": {"type": "string"},
                    "title": {"type": "string"},
                },
                'additionalProperties': False,
            }
        )


class TestSchemaInclude(unittest.TestCase):

    def test_partial(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String()

            class Attrs:
                additional = False

        t = MyObject(include=['num'])
        self.assertEqual(
            t.get_jsonschema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                },
                'additionalProperties': False,
            }
        )


class TestSchemaExclude(unittest.TestCase):

    def test_initial_exclude(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(required=True)

            class Attrs:
                additional = False

        t = MyObject(exclude=['string'])
        self.assertEqual(
            t.get_jsonschema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                },
                'additionalProperties': False,
            }
        )


class TestSchemaTagFilter(unittest.TestCase):

    def test_context_exclude_initial(self):
        class SubSchema(types.Object):
            name = types.String()
            password = types.String(tags=['sensitive'])

        class MyObject(types.Object):
            fullname = types.String()
            email = types.String(required=True, tags=['sensitive'])
            login = SubSchema(additional=None)

            class Attrs:
                additional = False

        t = MyObject(exclude_tags='sensitive')
        self.assertEqual(
            t.get_jsonschema(),
            {
                "type": "object",
                "properties": {
                    "fullname": {"type": "string"},
                    'login': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'}
                        }
                    }
                },
                'additionalProperties': False,
            }
        )

    def test_context_exclude_tags_mix(self):
        class SubSchema(types.Object):
            name = types.String()
            password = types.String(tags=['sensitive'])
            last_update = types.String(tags=['readonly'])

        class MyObject(types.Object):
            fullname = types.String()
            email = types.String(required=True, tags=['sensitive'])
            login = SubSchema(additional=None, exclude_tags='readonly')

            class Attrs:
                additional = False

        t = MyObject(exclude_tags='sensitive')
        self.assertEqual(
            t.get_jsonschema(),
            {
                "type": "object",
                "properties": {
                    "fullname": {"type": "string"},
                    'login': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'}
                        }
                    }
                },
                'additionalProperties': False,
            }
        )
