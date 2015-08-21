import datetime
import json
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


class TestDate(unittest.TestCase):

    def test_validation(self):
        t = types.Date()

        t.validate(datetime.date(2012, 12, 24))
        t.validate("2012-12-24")
        with self.assertRaises(ValueError):
            t.validate('crappy')

    def test_serialize(self):
        t = types.Date()
        v = t.dump(datetime.date(2012, 12, 24))
        self.assertEqual(v, '"2012-12-24"')

    def test_loads(self):
        t = types.Date()

        v = t.load('"2012-12-24"')
        self.assertEqual(v, datetime.date(2012, 12, 24))

    def test_complex(self):
        class MySchema(types.Object):
            date = types.Date()
        t = MySchema()
        t.validate({"date": datetime.date(2012, 12, 24)})
        t.dump({"date": datetime.date(2012, 12, 24)})


class TestDuration(unittest.TestCase):

    def test_validation(self):
        t = types.Duration()

        t.validate(datetime.timedelta(seconds=12))
        t.validate(12)
        with self.assertRaises(ValueError):
            t.validate('crappy')

    def test_serialize(self):
        t = types.Duration()
        v = t.dump(datetime.timedelta(seconds=12))
        self.assertEqual(v, '"PT12S"')

    def test_loads(self):
        t = types.Duration()

        v = t.load('"PT12S"')
        self.assertEqual(v, datetime.timedelta(seconds=12))

        v = t.load('12')
        self.assertEqual(v, datetime.timedelta(seconds=12))

        v = t.load('12.1')
        self.assertEqual(v, datetime.timedelta(seconds=12, milliseconds=100))

    def test_complex(self):
        class MySchema(types.Object):
            duration = types.Duration()
        t = MySchema()
        t.validate({"duration": datetime.timedelta(seconds=12)})
        t.dump({"duration": datetime.timedelta(seconds=12)})


class TestObject(unittest.TestCase):

    def test_serialize(self):
        class MySchema(types.Object):
            username = types.String()
            password = types.String()

        data = {'username': 'admin', 'password': 'secret', 'pk': 1}
        dumped = MySchema().dump(data)
        self.assertEqual(
            json.loads(dumped),
            {'username': 'admin', 'password': 'secret', 'pk': 1}
        )
        self.assertEqual(
            data,
            {'username': 'admin', 'password': 'secret', 'pk': 1}
        )
