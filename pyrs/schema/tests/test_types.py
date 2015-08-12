import unittest

import jsonschema

from .. import types


class TestString(unittest.TestCase):

    def test_schema(self):
        t = types.String()

        self.assertEqual(t.get_schema(), {"type": "string"})

    def test_validation_pattern(self):
        t = types.String(pattern=r".+")

        t.validate("valid")
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate("")


class TestEnum(unittest.TestCase):

    def test_schema(self):
        t = types.Enum()

        self.assertEqual(t.get_schema(), {})

    def test_validation_enum(self):
        t = types.Enum(enum=["a", "b", 1, True])
        self.assertEqual(t.get_schema(), {"enum": ["a", "b", 1, True]})

        t.validate("a")
        t.validate(1)
        t.validate(True)
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate("c")
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate(2)
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate(False)


class TestInteger(unittest.TestCase):

    def test_schama(self):
        t = types.Integer()

        self.assertEqual(t.get_schema(), {"type": "integer"})

    def test_validation(self):
        t = types.Integer()

        t.validate(12)
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate(12.22)

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate("Hello")


class TestNumber(unittest.TestCase):

    def test_schema(self):
        t = types.Number()

        self.assertEqual(t.get_schema(), {"type": "number"})

    def test_validation(self):
        t = types.Number()

        t.validate(12)
        t.validate(12.22)

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate("Hello")


class TestBoolean(unittest.TestCase):

    def test_schema(self):
        t = types.Boolean()

        self.assertEqual(t.get_schema(), {"type": "boolean"})

    def test_validation(self):
        t = types.Boolean()

        t.validate(True)
        t.validate(False)

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate("Hello")


class TestArray(unittest.TestCase):

    def test_schema(self):
        t = types.Array()

        self.assertEqual(t.get_schema(), {"type": "array"})

    def test_validation(self):
        t = types.Array()
        t.validate([])
        t.validate([1, 2, 3])

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            t.validate("Hello")
