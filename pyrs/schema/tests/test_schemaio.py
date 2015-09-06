import unittest

from .. import base
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
        io = schemaio.SchemaWriter()

        with self.assertRaises(NotImplementedError):
            io.write(t1)


class TestValidator(unittest.TestCase):

    def test_validate(self):
        t1 = types.String()
        io = schemaio.Validator(t1)

        with self.assertRaises(NotImplementedError):
            io.validate('"Hello"')


class TestWriter(unittest.TestCase):

    def test_write(self):
        t1 = types.String()
        io = schemaio.Writer(t1)

        with self.assertRaises(NotImplementedError):
            io.write('test')


class TestReader(unittest.TestCase):

    def test_read(self):
        t1 = types.String()
        io = schemaio.Reader(t1)

        with self.assertRaises(NotImplementedError):
            io.read('"test"')


class TestJSONSchemaWriter(unittest.TestCase):

    def test_extract(self):
        t1 = types.String()
        io = schemaio.JSONSchemaWriter()

        s = io.extract(t1)
        self.assertEqual(s, {'type': 'string'})

    def test_write(self):
        t1 = types.String()
        io = schemaio.JSONSchemaWriter()

        s = io.write(t1)
        self.assertEqual(s, '{"type": "string"}')


class TestJSONSchemaValidator(unittest.TestCase):

    def test_validation_error(self):
        t1 = types.String()
        io = schemaio.JSONSchemaValidator(t1)

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.validate(12)
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
        io = schemaio.JSONSchemaValidator(MyObject())

        io.validate({"s1": '12', "s2": '13'})

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.validate({"s1": 12, "s2": 13})
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

        io = schemaio.JSONSchemaValidator(MyObject())

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.validate({"o1": {"o2": {"s1": 12, "s2": "z"}}})
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

    def test_constraint_validation(self):
        class MyObject(types.Object):
            s1 = types.String(required=True)
            s2 = types.String(required=True)

            @base.constraint('identical', 's1 != s2')
            def identical(self, value):
                if value.get('s1') == value.get('s2'):
                    yield exceptions.ConstraintError('Incorrect combination')

            @base.constraint('complex', 's1 + s2 != 1212')
            def complex(self, value):
                if 's1' in value and 's2' in value:
                    if value.get('s1') + value.get('s2') == '1212':
                        yield exceptions.ConstraintError(
                            against='complex.1212'
                        )

            @base.constraint('never', 'Never fail')
            def never_fail(self, value):
                return

        class MySchema(types.Object):
            sub = MyObject()

        io = schemaio.JSONSchemaValidator(MySchema())

        io.validate({'sub': {'s1': '12', 's2': '13'}})

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.validate({'sub': {"s1": '12', "s2": '12'}})
        errors = sorted(ctx.exception.errors, key=lambda e: e['against'])

        self.assertEqual(errors[0]['message'], "s1 + s2 != 1212")
        self.assertEqual(errors[0]['path'], 'sub')
        self.assertEqual(errors[0]['value'], {'s1': '12', 's2': '12'})
        self.assertEqual(errors[0]['invalid'], 'constraints')
        self.assertEqual(errors[0]['against'], 'complex.1212')

        self.assertEqual(errors[1]['message'], "Incorrect combination")
        self.assertEqual(errors[1]['path'], 'sub')
        self.assertEqual(errors[1]['value'], {'s1': '12', 's2': '12'})
        self.assertEqual(errors[1]['invalid'], 'constraints')
        self.assertEqual(errors[1]['against'], 'identical')


class TestJSONSchemaDictValidator(unittest.TestCase):

    def test_validation_error_of_object(self):
        io = schemaio.JSONSchemaDictValidator({
            's1': types.String(),
            's2': types.String()
        })

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.validate({"s1": 12, "s2": 13})
        ex = ctx.exception

        errors = sorted(ex.errors, key=lambda v: v['value'])

        self.assertEqual(errors[0]['message'], "12 is not of type 'string'")
        self.assertEqual(errors[0]['path'], 's1')
        self.assertEqual(errors[0]['value'], 12)
        self.assertEqual(errors[0]['invalid'], 'type')
        self.assertEqual(errors[0]['against'], 'string')

    def test_validation_error_of_complex(self):
        class MyObjectBase(types.Object):
            s1 = types.String()
            s2 = types.String(min_len=2, pattern=r'^[0-9a-f]+$')

        class MyObjectMid(types.Object):
            o2 = MyObjectBase()

        io = schemaio.JSONSchemaDictValidator({'o1': MyObjectMid()})

        with self.assertRaises(exceptions.ValidationErrors) as ctx:
            io.validate({"o1": {"o2": {"s1": 12, "s2": "z"}}})
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


class TestJSONWriter(unittest.TestCase):

    def test_write_basic(self):
        t1 = types.String()
        io = schemaio.JSONWriter(t1)

        self.assertEqual(io.write('test'), '"test"')

    def test_write_schema(self):
        class MySchema(base.Schema):
            _jsonschema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        io = schemaio.JSONWriter(MySchema())
        res = io.write({'num': 12})
        self.assertEqual(res, '{"num": 12}')

    def test_write_as_field(self):
        class MyType(base.Schema):
            _jsonschema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        class MyObject(types.Object):
            code = MyType()

        io = schemaio.JSONWriter(MyObject())

        res = io.write({'code': {'num': 12}})
        self.assertEqual(res, '{"code": {"num": 12}}')


class TestJSONReader(unittest.TestCase):

    def test_read_basic(self):
        t1 = types.String()
        io = schemaio.JSONReader(t1)

        self.assertEqual(io.read('"test"'), 'test')

    def test_raise_parse_error_when_incorrect_data(self):
        t1 = types.String()
        io = schemaio.JSONReader(t1)

        with self.assertRaises(exceptions.ParseError):
            io.read(12)

    def test_raise_parse_error(self):
        t1 = types.String()
        io = schemaio.JSONReader(t1)

        with self.assertRaises(exceptions.ParseError):
            io.read('text')


class TestJSONFormReader(unittest.TestCase):

    def test_load_form(self):
        class MySub(types.Object):
            sub = types.Integer()

        class MyObject(types.Object):
            num = types.Integer()
            string = types.String(name="NewName")
            arr = types.Array()
            sub = MySub(additional=None)

        t = MyObject(additional=None)
        io = schemaio.JSONFormReader(t)
        form = {
            'num': '1',
            'NewName': 'hi',
            'sub': '{"sub": 1}',
            'arr': '[1, 2, "hi"]',
            'unknown': '{"any": "value"}'
        }
        r = io.read(form)
        self.assertEqual(r, {
            "num": 1,
            "string": "hi",
            'sub': {'sub': 1},
            'arr': [1, 2, 'hi'],
            'unknown': '{"any": "value"}'
        })


class TestHiddenFields(unittest.TestCase):

    def test_hidden_doesnt_show_up_on_schema(self):
        class MySchema(types.Object):
            fullname = types.String()
            email = types.String(hidden=True)

        s = MySchema(additional=None)
        self.assertEqual(
            s.get_jsonschema(),
            {
                'type': 'object',
                'properties': {'fullname': {'type': 'string'}},
            }
        )

    def test_hidden_doesnt_show_up_on_raw(self):
        class MySchema(types.Object):
            fullname = types.String()
            email = types.String(hidden=True)

        s = MySchema(additional=None)
        self.assertEqual(
            s.to_raw({'fullname': 'name', 'email': 'name@exmaple.com'}),
            {'fullname': 'name'}
        )


class TestSetter(unittest.TestCase):

    def test_setter(self):
        class MySchema(types.Object):
            fullname = types.String(name='FullName')
            email = types.String(hidden=True, name='Email')

            @email.setter
            def set_email(self, data):
                name = self.fieldname
                return data['fullname']+'.'+name+'@example.com'

        s = MySchema(additional=None)
        self.assertEqual(
            s.to_python({'FullName': 'name'}),
            {'fullname': 'name', 'email': 'name.email@example.com'}
        )


    def test_setter_overwrite(self):
        class MySchema(types.Object):
            fullname = types.String(name='FullName')
            email = types.String(name='Email')

            @email.setter
            def set_email(self, data):
                name = self.fieldname
                return data['fullname']+'.'+data[name]+'.'+name+'@example.com'

        s = MySchema(additional=None)
        self.assertEqual(
            s.to_python({'FullName': 'name', 'Email': '123'}),
            {'fullname': 'name', 'email': 'name.123.email@example.com'}
        )


class TestGetter(unittest.TestCase):

    def test_getter(self):
        class MySchema(types.Object):
            fullname = types.String(name='FullName')
            email = types.String(name='Email')

            @email.getter
            def get_email(self, data):
                name = self.fieldname
                return data['fullname']+'.'+name+'@example.com'

        s = MySchema(additional=None)
        self.assertEqual(
            s.to_raw({'fullname': 'name'}),
            {'FullName': 'name', 'Email': 'name.email@example.com'}
        )

    def test_getter_overwrite(self):
        class MySchema(types.Object):
            fullname = types.String(name='FullName')
            email = types.String(name='Email')

            @email.getter
            def get_email(self, data):
                name = self.fieldname
                return data['fullname']+'.'+name+'@'+data[name]

        s = MySchema(additional=None)
        self.assertEqual(
            s.to_raw({'fullname': 'name', 'email': 'example.com'}),
            {'FullName': 'name', 'Email': 'name.email@example.com'}
        )

class TestFallback(unittest.TestCase):

    def setUp(self):
        class MySchema(types.Object):
            fullname = types.String(name='FullName')
            email = types.String(name='Email', fallback='default@example.com')

        self.schema = MySchema(additional=None)

    def test_to_raw(self):
        self.assertEqual(
            self.schema.to_raw({'fullname': 'name'}),
            {'FullName': 'name', 'Email': 'default@example.com'}
        )

    def test_to_raw_does_not_overwrite(self):
        self.assertEqual(
            self.schema.to_raw(
                {'fullname': 'name', 'email': 'user@example.com'}
            ),
            {'FullName': 'name', 'Email': 'user@example.com'}
        )

    def test_to_python(self):
        self.assertEqual(
            self.schema.to_python({'FullName': 'name'}),
            {'fullname': 'name', 'email': 'default@example.com'}
        )

    def test_to_python_does_not_overwrite(self):
        self.assertEqual(
            self.schema.to_python(
                {'FullName': 'name', 'Email': 'user@example.com'}
            ),
            {'fullname': 'name', 'email': 'user@example.com'}
        )
