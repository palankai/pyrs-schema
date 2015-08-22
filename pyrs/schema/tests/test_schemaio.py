import unittest

from .. import schemaio
from .. import types


class TestSchemaIO(unittest.TestCase):

    def test_init_store_schema(self):
        t = types.String()
        io = schemaio.SchemaIO(t)

        self.assertEqual(io.schema, t)

    def test_init_store_schema_none(self):
        io = schemaio.SchemaIO()

        self.assertEqual(io.schema, None)

    def test_get_schema_raise_error_with_none(self):
        io = schemaio.SchemaIO()

        with self.assertRaises(AttributeError):
            io.get_schema()

    def test_get_schema_gives_back_the_param(self):
        t = types.String()
        io = schemaio.SchemaIO()

        self.assertEqual(io.get_schema(t), t)

    def test_get_schema_gives_back_the_init_schema(self):
        t = types.String()
        io = schemaio.SchemaIO(t)

        self.assertEqual(io.get_schema(), t)

    def test_get_schema_prioritise_well(self):
        t1 = types.String()
        t2 = types.Integer()
        io = schemaio.SchemaIO(t1)

        self.assertEqual(io.get_schema(t2), t2)


class TestSchemaWriter(unittest.TestCase):

    def test_write(self):
        t1 = types.String()
        io = schemaio.SchemaWriter(t1)

        self.assertEqual(io.write('test'), '"test"')

    def test_write_with_given(self):
        t1 = types.String()
        io = schemaio.SchemaWriter()

        self.assertEqual(io.write('test', schema=t1), '"test"')


class TestSchemaReader(unittest.TestCase):

    def test_write(self):
        t1 = types.String()
        io = schemaio.SchemaReader(t1)

        self.assertEqual(io.read('"test"'), 'test')

    def test_write_with_given(self):
        t1 = types.String()
        io = schemaio.SchemaReader()

        self.assertEqual(io.read('"test"', schema=t1), 'test')


class TestJSONWriter(unittest.TestCase):

    def test_write(self):
        t1 = types.String()
        io = schemaio.JSONWriter(t1)

        self.assertEqual(io.write('test'), '"test"')

    def test_write_with_given(self):
        t1 = types.String()
        io = schemaio.JSONWriter()

        self.assertEqual(io.write('test', schema=t1), '"test"')


class TestJSONReader(unittest.TestCase):

    def test_write(self):
        t1 = types.String()
        io = schemaio.JSONReader(t1)

        self.assertEqual(io.read('"test"'), 'test')

    def test_write_with_given(self):
        t1 = types.String()
        io = schemaio.JSONReader()

        self.assertEqual(io.read('"test"', schema=t1), 'test')
