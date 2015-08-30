import unittest

from .. import exceptions
from .. import schemaio
from .. import types


class TestSchemaIO(unittest.TestCase):

    def test_init_store_schema(self):
        t = types.String()
        io = schemaio.SchemaIO(t)

        self.assertEqual(io.schema, t)


class TestSchemaWriter(unittest.TestCase):

    def test_write(self):
        t1 = types.String()
        io = schemaio.SchemaWriter(t1)

        self.assertEqual(io.write('test'), '"test"')


class TestSchemaReader(unittest.TestCase):

    def test_write(self):
        t1 = types.String()
        io = schemaio.SchemaReader(t1)

        self.assertEqual(io.read('"test"'), 'test')


class TestJSONWriter(unittest.TestCase):

    def test_write(self):
        t1 = types.String()
        io = schemaio.JSONWriter(t1)

        self.assertEqual(io.write('test'), '"test"')


class TestJSONReader(unittest.TestCase):

    def test_read_basic(self):
        t1 = types.String()
        io = schemaio.JSONReader(t1)

        self.assertEqual(io.read('"test"'), 'test')

    def test_raise_parse_error_when_incorrect_Data(self):
        t1 = types.String()
        io = schemaio.JSONReader(t1)

        with self.assertRaises(exceptions.ParseError):
            io.read(12)

    def test_raise_parse_error(self):
        t1 = types.String()
        io = schemaio.JSONReader(t1)

        with self.assertRaises(exceptions.ParseError):
            io.read('text')

    def test_validation_error(self):
        t1 = types.String()
        io = schemaio.JSONReader(t1)

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.read('12')
        ex = ctx.exception

        self.assertEqual(ex.value, 12)
        self.assertEqual(len(ex.errors), 1)
        error = ex.errors[0]

        self.assertEqual(error['message'], "12 is not of type 'string'")
        self.assertEqual(error['path'], '')
        self.assertEqual(error['value'], 12)
        self.assertEqual(error['invalid'], 'type')

    def test_validation_error_of_object(self):
        class MyObject(types.Object):
            s1 = types.String()
            s2 = types.String()
        io = schemaio.JSONReader(MyObject)

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.read('{"s1": 12, "s2": 13}')
        ex = ctx.exception

        self.assertEqual(ex.errors[0]['message'], "12 is not of type 'string'")
        self.assertEqual(ex.errors[0]['path'], 's1')
        self.assertEqual(ex.errors[0]['value'], 12)
        self.assertEqual(ex.errors[0]['invalid'], 'type')
        self.assertEqual(ex.errors[0]['against'], 'string')

    def test_validation_error_of_complex(self):
        class MyObjectBase(types.Object):
            s1 = types.String()
            s2 = types.String(min_len=2, pattern=r'^[0-9a-f]+$')

        class MyObjectMid(types.Object):
            o2 = MyObjectBase()

        class MyObject(types.Object):
            o1 = MyObjectMid()

        io = schemaio.JSONReader(MyObject)

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.read('{"o1": {"o2": {"s1": 12, "s2": "z"}}}')
        ex = ctx.exception
        errors = sorted(ex.errors, key=lambda v: v['invalid'])

        self.assertEqual(errors[0]['path'], 'o1.o2.s2')
        self.assertEqual(errors[0]['invalid'], 'minLength')
        self.assertEqual(errors[0]['against'], 2)

        self.assertEqual(errors[1]['path'], 'o1.o2.s2')
        self.assertEqual(errors[1]['invalid'], 'pattern')
        self.assertEqual(errors[1]['against'], '^[0-9a-f]+$')

        self.assertEqual(errors[2]['message'], "12 is not of type 'string'")
        self.assertEqual(errors[2]['path'], 'o1.o2.s1')
        self.assertEqual(errors[2]['value'], 12)
        self.assertEqual(errors[2]['invalid'], 'type')
        self.assertEqual(errors[2]['against'], 'string')
