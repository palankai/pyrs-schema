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
            def to_python(self, src):
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
            def to_raw(self, src):
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


class TestObjectFields(unittest.TestCase):

    def test_procedural_extend(self):
        field = types.String()
        byarg = types.String()
        extend = types.String()

        class MyObject(types.Object):
            basefield = field

        t = MyObject(extend={'byarg': byarg})
        t.extend({
            'extend': extend
        })

        self.assertEqual(field.parent, t)
        self.assertEqual(field.fieldname, 'basefield')

        self.assertEqual(byarg.parent, t)
        self.assertEqual(byarg.fieldname, 'byarg')

        self.assertEqual(extend.parent, t)
        self.assertEqual(extend.fieldname, 'extend')


class TestSchemaExtend(unittest.TestCase):

    def test_procedural_extend(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String()

            class Attrs:
                additional = False

        t = MyObject()
        extra = types.String()
        t.extend({
            'title': extra
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

        extra = types.String()
        t = MyObject(extend={'title': extra})

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


class TestExclusive(unittest.TestCase):

    def setUp(self):
        class MyObject(types.Object):
            num = types.Integer()
            string = types.String()

            class Attrs:
                additional = False

        self.schema = MyObject(exclusive=['num'])

    def test_does_not_show_up_in_schema(self):
        self.assertEqual(
            self.schema.get_jsonschema(),
            {
                "type": "object",
                "properties": {
                    "num": {"type": "integer"},
                },
                'additionalProperties': False,
            }
        )

    def test_does_not_show_up_in_to_raw(self):
        self.assertEqual(
            self.schema.to_raw({'num': 12, 'string': 'str'}), {'num': 12}
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

    def test_exclude_initial(self):
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

    def test_exclude_tags_mix(self):
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
