import unittest

import jsonschema
import mock

from .. import base
from .. import exceptions
from .. import types


class TestBase(unittest.TestCase):

    def test_attrs(self):
        b = base.Base(attr=1)

        self.assertEqual(b.get_attr("attr"), 1)

    def test_load(self):
        b = base.Base()
        with mock.patch.object(b, "validate_dict") as validate:
            res = b.load('"Hello"')

        self.assertEqual(res, "Hello")
        validate.assert_called_with("Hello", context=None)

    def test_dump(self):
        b = base.Base()
        with mock.patch.object(b, "validate_dict") as validate:
            res = b.dump("Hello")

        self.assertEqual(res, '"Hello"')
        validate.assert_called_with("Hello", context=None)

    def test_get_schema(self):
        with mock.patch.object(base.Base, "_type", new="string"):
            b = base.Base()
            s = b.get_schema()
            self.assertEqual(s, {"type": "string"})
        self.assertIsNone(base.Base._type)

    def test_validation(self):
        with mock.patch.object(base.Base, "_type", new="string"):
            b = base.Base()
            b.validate("Hello")
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                b.validate(None)
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                b.validate({"string": 1})

    def test_null_validation(self):
        with mock.patch.object(base.Base, "_type", new="string"):
            b = base.Base(null=True)
            b.validate("Hello")
            b.validate(None)

    def test_enum_validation(self):
        with mock.patch.object(base.Base, "_type", new="string"):
            b = base.Base(enum=["a", "b", "c"])

            b.validate("a")
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                b.validate("Hello")

    def test_default_attrs(self):
        class MyType(base.Base):
            _type = "string"
            _attrs = {"null": True}
        t = MyType()

        self.assertEqual(t.get_schema(), {"type": ["string", "null"]})

    def test_title_description(self):
        class MyType(base.Base):
            _type = "string"
        t = MyType(title="t", description='d')

        self.assertEqual(
            t.get_schema(),
            {"type": "string", "title": "t", "description": 'd'}
        )

    def test_title_description_declarative(self):
        class MyType(base.Base):
            _type = "string"

            class Attrs:
                title = 't'
                description = 'd'
        t = MyType()

        self.assertEqual(
            t.get_schema(),
            {"type": "string", "title": "t", "description": 'd'}
        )


class TestDeclarativeBase(unittest.TestCase):

    def test_declarative_attrs_update(self):
        class MyType(base.Base):
            _type = "string"

            class Attrs:
                null = True

        t = MyType()

        self.assertEqual(t.get_schema(), {"type": ["string", "null"]})


class TestDefault(unittest.TestCase):

    def test_default_schema(self):
        class MySchema(types.Object):
            name = types.String(default='example')

        t = MySchema(additional=None)
        self.assertEqual(
            t.get_schema(),
            {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'default': 'example'}
                }
            }
        )


class TestSchema(unittest.TestCase):

    def test_creation_index(self):
        base.Schema._creation_index = 0

        b0 = base.Schema()
        b1 = base.Base()
        b2 = base.Base()

        self.assertEqual(b0._creation_index, 0)
        self.assertEqual(b1._creation_index, 1)
        self.assertEqual(b2._creation_index, 2)
        self.assertEqual(base.Base._creation_index, 3)

    def test_validation(self):
        class MySchema(base.Schema):
            _schema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        s = MySchema()
        s.validate({'num': 12})
        with self.assertRaises(exceptions.ValidationError):
            s.validate({'num': 12.1})

    def test_validation_inline(self):
        s = base.Schema({
            'type': 'object',
            'properties': {
                'num': {'type': 'integer'}
            }
        })
        s.validate({'num': 12})
        with self.assertRaises(exceptions.ValidationError):
            s.validate({'num': 12.1})

    def test_redeclaration_raise_error(self):
        class MySchema(base.Schema):
            _schema = {'type': 'string'}

        with self.assertRaises(AttributeError):
            MySchema({
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            })

    def test_load(self):
        class MySchema(base.Schema):
            _schema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        s = MySchema()
        res = s.load('{"num": 12}')
        self.assertEqual(res, {'num': 12})

    def test_dump(self):
        class MySchema(base.Schema):
            _schema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        s = MySchema()
        res = s.dump({'num': 12})
        self.assertEqual(res, '{"num": 12}')

    def test_dump_as_field(self):
        class MyType(base.Schema):
            _schema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        class MyObject(types.Object):
            code = MyType()

        s = MyObject()
        res = s.dump({'code': {'num': 12}})
        self.assertEqual(res, '{"code": {"num": 12}}')

    def test_load_as_field(self):
        class MyType(base.Schema):
            _schema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        class MyObject(types.Object):
            code = MyType()

        s = MyObject()
        res = s.load('{"code": {"num": 12}}')
        self.assertEqual(res, {'code': {'num': 12}})
