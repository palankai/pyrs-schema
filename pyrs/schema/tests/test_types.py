import datetime
import unittest

from .. import exceptions
from .. import types


class TestAny(unittest.TestCase):

    def setUp(self):
        self.schema = types.Any()

    def test_jsonschema(self):
        self.assertEqual(self.schema.get_jsonschema(), {})


class TestString(unittest.TestCase):

    def test_jsonschema(self):
        t = types.String()

        self.assertEqual(t.get_jsonschema(), {'type': 'string'})

    def test_set_extra(self):
        t = types.String(pattern=r'.+', min_len=2, max_len=4)
        self.assertEqual(
            t.get_jsonschema(),
            {'type': 'string', 'pattern': '.+', 'minLength': 2, 'maxLength': 4}
        )

    def test_blank(self):
        t = types.String(blank=False)
        self.assertEqual(
            t.get_jsonschema(),
            {'type': 'string', 'minLength': 1}
        )

    def test_blank_with_min_len(self):
        t = types.String(min_len=2, blank=False)
        self.assertEqual(
            t.get_jsonschema(),
            {'type': 'string', 'minLength': 2}
        )

    def test_blank_with_zero_min_len(self):
        t = types.String(min_len=0, blank=False)
        self.assertEqual(
            t.get_jsonschema(),
            {'type': 'string', 'minLength': 1}
        )


class TestEnum(unittest.TestCase):

    def test_jsonschema(self):
        t = types.Enum()

        self.assertEqual(t.get_jsonschema(), {})

    def test_enum_set(self):
        t = types.Enum(enum=['a', 'b', 1, True])
        self.assertEqual(t.get_jsonschema(), {'enum': ['a', 'b', 1, True]})


class TestNumber(unittest.TestCase):

    def test_jsonschema(self):
        t = types.Number()

        self.assertEqual(t.get_jsonschema(), {'type': 'number'})

    def test_with_extra_args(self):
        t = types.Number(
            multiple=2,
            minimum=4, exclusive_min=True,
            maximum=256, exclusive_max=True
        )
        self.assertEqual(
            t.get_jsonschema(),
            {
                'type': 'number',
                'multipleOf': 2,
                'minimum': 4,
                'exclusiveMinimum': True,
                'maximum': 256,
                'exclusiveMaximum': True
            }
        )


class TestInteger(unittest.TestCase):

    def test_schama(self):
        t = types.Integer()

        self.assertEqual(t.get_jsonschema(), {'type': 'integer'})

    def test_with_extra_args(self):
        t = types.Integer(
            multiple=2,
            minimum=4, exclusive_min=True,
            maximum=256, exclusive_max=True
        )
        self.assertEqual(
            t.get_jsonschema(),
            {
                'type': 'integer',
                'multipleOf': 2,
                'minimum': 4,
                'exclusiveMinimum': True,
                'maximum': 256,
                'exclusiveMaximum': True
            }
        )


class TestBoolean(unittest.TestCase):

    def test_jsonschema(self):
        t = types.Boolean()

        self.assertEqual(t.get_jsonschema(), {'type': 'boolean'})


class TestArray(unittest.TestCase):

    def test_jsonschema(self):
        t = types.Array()

        self.assertEqual(t.get_jsonschema(), {'type': 'array'})

    def test_with_extra_args(self):
        t = types.Array(
            additional=True, min_items=2, max_items=5, unique_items=True,
            items=types.String()
        )
        self.assertEqual(
            t.get_jsonschema(),
            {
                'type': 'array',
                'additionalItems': True,
                'minItems': 2,
                'maxItems': 5,
                'uniqueItems': True,
                'items': {'type': 'string'}
            }
        )

    def test_list_of_items(self):
        t = types.Array(
            items=[types.String(), types.Integer()]
        )
        self.assertEqual(
            t.get_jsonschema(),
            {
                'type': 'array',
                'items': [{'type': 'string'}, {'type': 'integer'}]
            }
        )

    def test_type_additional(self):
        t = types.Array(
            additional=types.String()
        )
        self.assertEqual(
            t.get_jsonschema(),
            {
                'type': 'array',
                'additionalItems': {'type': 'string'}
            }
        )


class TestDate(unittest.TestCase):

    def setUp(self):
        self.schema = types.Date()

    def test_jsonschema(self):
        self.assertEqual(
            self.schema.get_jsonschema(), {'type': 'string', 'format': 'date'}
        )

    def test_to_python_string(self):
        v = self.schema.to_python('2012-12-24')
        self.assertEqual(v, datetime.date(2012, 12, 24))

    def test_to_python_object(self):
        v = self.schema.to_python(datetime.date(2012, 12, 24))
        self.assertEqual(v, datetime.date(2012, 12, 24))

    def test_to_python_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_python(True)

    def test_to_raw_object(self):
        v = self.schema.to_raw(datetime.date(2012, 12, 24))
        self.assertEqual(v, '2012-12-24')

    def test_to_raw_string(self):
        v = self.schema.to_raw('2012-12-24')
        self.assertEqual(v, '2012-12-24')

    def test_to_raw_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_raw(True)


class TestTime(unittest.TestCase):

    def setUp(self):
        self.schema = types.Time()

    def test_jsonschema(self):
        self.assertEqual(
            self.schema.get_jsonschema(), {'type': 'string', 'format': 'time'}
        )

    def test_to_python_string(self):
        v = self.schema.to_python('16:22:00')
        self.assertEqual(v, datetime.time(16, 22, 00))

    def test_to_python_object(self):
        v = self.schema.to_python(datetime.time(16, 22, 0))
        self.assertEqual(v, datetime.time(16, 22, 0))

    def test_to_python_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_python(True)

    def test_to_raw_object(self):
        v = self.schema.to_raw(datetime.time(16, 22, 0))
        self.assertEqual(v, '16:22:00')

    def test_to_raw_string(self):
        v = self.schema.to_raw('16:22:00')
        self.assertEqual(v, '16:22:00')

    def test_to_raw_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_raw(True)


class TestDateTime(unittest.TestCase):

    def setUp(self):
        self.schema = types.DateTime()

    def test_jsonschema(self):
        self.assertEqual(
            self.schema.get_jsonschema(),
            {'type': 'string', 'format': 'datetime'}
        )

    def test_to_python_string(self):
        v = self.schema.to_python('2012-03-11T16:22:00')
        self.assertEqual(v, datetime.datetime(2012, 3, 11, 16, 22, 0))

    def test_to_python_object(self):
        v = self.schema.to_python(datetime.datetime(2012, 3, 11, 16, 22, 0))
        self.assertEqual(v, datetime.datetime(2012, 3, 11, 16, 22, 0))

    def test_to_python_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_python(True)

    def test_to_raw_object(self):
        v = self.schema.to_raw(datetime.datetime(2012, 3, 11, 16, 22, 0))
        self.assertEqual(v, '2012-03-11T16:22:00')

    def test_to_raw_string(self):
        v = self.schema.to_raw('2012-03-11 16:22:00')
        self.assertEqual(v, '2012-03-11 16:22:00')

    def test_to_raw_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_raw(True)


class TestDuration(unittest.TestCase):

    def setUp(self):
        self.schema = types.Duration()

    def test_jsonschema(self):
        self.assertEqual(
            self.schema.get_jsonschema(),
            {'type': 'string', 'format': 'duration'}
        )

    def test_to_python_string(self):
        v = self.schema.to_python('PT12S')
        self.assertEqual(v, datetime.timedelta(seconds=12))

    def test_to_python_int(self):
        v = self.schema.to_python(12)
        self.assertEqual(v, datetime.timedelta(seconds=12))

    def test_to_python_float(self):
        v = self.schema.to_python(12.5)
        self.assertEqual(v, datetime.timedelta(seconds=12, milliseconds=500))

    def test_to_python_object(self):
        v = self.schema.to_python(datetime.timedelta(seconds=12))
        self.assertEqual(v, datetime.timedelta(seconds=12))

    def test_to_python_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_python(datetime.date(2012, 3, 11))

    def test_to_raw_object(self):
        v = self.schema.to_raw(datetime.timedelta(seconds=12))
        self.assertEqual(v, 'PT12S')

    def test_to_raw_string(self):
        v = self.schema.to_raw('PT12S')
        self.assertEqual(v, 'PT12S')

    def test_to_raw_int(self):
        v = self.schema.to_raw(12)
        self.assertEqual(v, 'PT12S')

    def test_to_raw_float(self):
        v = self.schema.to_raw(12.5)
        self.assertEqual(v, 'PT12.5S')

    def test_to_raw_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_raw(datetime.date(2012, 3, 11))


class TestTimeDelta(unittest.TestCase):

    def setUp(self):
        self.schema = types.TimeDelta()

    def test_jsonschema(self):
        self.assertEqual(
            self.schema.get_jsonschema(),
            {'type': 'number'}
        )

    def test_to_python_int(self):
        v = self.schema.to_python(12)
        self.assertEqual(v, datetime.timedelta(seconds=12))

    def test_to_python_float(self):
        v = self.schema.to_python(12.5)
        self.assertEqual(v, datetime.timedelta(seconds=12, milliseconds=500))

    def test_to_python_object(self):
        v = self.schema.to_python(datetime.timedelta(seconds=12))
        self.assertEqual(v, datetime.timedelta(seconds=12))

    def test_to_python_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_python(datetime.date(2012, 3, 11))

    def test_to_raw_object(self):
        v = self.schema.to_raw(datetime.timedelta(seconds=12))
        self.assertEqual(v, 12)

    def test_to_raw_int(self):
        v = self.schema.to_raw(12)
        self.assertEqual(v, 12)

    def test_to_raw_float(self):
        v = self.schema.to_raw(12.5)
        self.assertEqual(v, 12.5)

    def test_to_raw_error(self):
        with self.assertRaises(exceptions.ValidationError):
            self.schema.to_raw(datetime.date(2012, 3, 11))


class TestObject(unittest.TestCase):

    def test_serialize(self):
        class MySchema(types.Object):
            username = types.String()
            password = types.String()

        data = {'username': 'admin', 'password': 'secret', 'pk': 1}
        raw = MySchema(additional=None).to_raw(data)
        self.assertEqual(
            raw,
            {'username': 'admin', 'password': 'secret', 'pk': 1}
        )
        self.assertEqual(
            data,
            {'username': 'admin', 'password': 'secret', 'pk': 1}
        )
