import unittest

from .. import base
from .. import exceptions
from .. import types


class TestBase(unittest.TestCase):

    def test_attrs(self):
        b = base.Base(attr=1)

        self.assertEqual(b.get_attr('attr'), 1)

    def test_get_jsonschema(self):
        b = base.Base(type='string')
        s = b.get_jsonschema()
        self.assertEqual(s, {'type': 'string'})
        self.assertIsNone(base.Base._type)

    def test_null(self):
        b = base.Base(null=True, type='string')
        self.assertEqual(b.get_jsonschema(), {'type': ['string', 'null']})

    def test_null_with_list(self):
        b = base.Base(null=True, type=['string', 'integer'])
        self.assertEqual(
            b.get_jsonschema(), {'type': ['string', 'integer', 'null']}
        )

    def test_id(self):
        b = base.Base(id='1', type='string')
        self.assertEqual(b.get_jsonschema(), {'type': 'string', 'id': '1'})

    def test_enum_validation(self):
        b = base.Base(enum=['a', 'b', 'c'], type='string')
        self.assertEqual(
            b.get_jsonschema(), {'type': 'string', 'enum': ['a', 'b', 'c']}
        )

    def test_default_attrs(self):
        class MyType(base.Base):
            _type = 'string'
            _attrs = {'null': True}
        t = MyType()

        self.assertEqual(t.get_jsonschema(), {'type': ['string', 'null']})

    def test_title_description(self):
        class MyType(base.Base):
            _type = "string"
        t = MyType(title="t", description='d')

        self.assertEqual(
            t.get_jsonschema(),
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
            t.get_jsonschema(),
            {"type": "string", "title": "t", "description": 'd'}
        )


class TestDeclarativeBase(unittest.TestCase):

    def test_declarative_attrs_update(self):
        class MyType(base.Base):
            _type = "string"

            class Attrs:
                null = True

        t = MyType()

        self.assertEqual(t.get_jsonschema(), {"type": ["string", "null"]})


class TestDefault(unittest.TestCase):

    def test_default_schema(self):
        class MySchema(types.Object):
            name = types.String(default='example')

        t = MySchema(additional=None)
        self.assertEqual(
            t.get_jsonschema(),
            {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'default': 'example'}
                }
            }
        )


class TestFields(unittest.TestCase):

    def test_fields(self):
        field = types.String(name='example')

        class MySchema(types.Object):
            name = field

        t = MySchema()
        self.assertEqual(t.fields['name'], field)
        self.assertIsNone(t._parent)
        self.assertEqual(field._parent, t)


class TestParentAndRoot(unittest.TestCase):

    def test_parents(self):
        field = types.String(name='example')

        class MidSchema(types.Object):
            name = field

        midschema = MidSchema()

        class MySchema(types.Object):
            name = midschema

        t = MySchema()
        self.assertEqual(t.parent, t)
        self.assertEqual(field.parent, midschema)
        self.assertEqual(midschema.parent, t)

        self.assertEqual(t.root, t)
        self.assertEqual(field.root, t)
        self.assertEqual(midschema.root, t)


class TestAttributes(unittest.TestCase):

    def test_attributes(self):
        field = types.String(spec_attr='spec')

        self.assertEqual(field.spec_attr, 'spec')

        with self.assertRaises(AttributeError):
            field.spec_attr2


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

    def test_declarative(self):
        class MySchema(base.Schema):
            _jsonschema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        s = MySchema()
        self.assertEqual(s.get_jsonschema(), {
            'type': 'object',
            'properties': {
                'num': {'type': 'integer'}
            }
        })

    def test_inline(self):
        s = base.Schema({
            'type': 'object',
            'properties': {
                'num': {'type': 'integer'}
            }
        })
        self.assertEqual(s.get_jsonschema(), {
            'type': 'object',
            'properties': {
                'num': {'type': 'integer'}
            }
        })

    def test_deserialize(self):
        class MySchema(base.Schema):
            _schema = {
                'type': 'object',
                'properties': {
                    'num': {'type': 'integer'}
                }
            }

        s = MySchema()
        res = s.to_python({'num': 12})
        self.assertEqual(res, {'num': 12})

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
        res = s.to_python({'code': {'num': 12}})
        self.assertEqual(res, {'code': {'num': 12}})


class TestConstaints(unittest.TestCase):

    def test_constraints(self):
        class MyType(base.Base):
            _type = 'string'

            class Attrs:
                constraints = {'code': 'code should be code'}
        t = MyType()

        self.assertEqual(
            t.get_jsonschema(), {
                'type': 'string',
                'constraints': {
                    'code': 'code should be code'
                }
            }
        )

    def test_declared_constraints(self):
        class MyType(base.Base):
            _type = 'string'

            @base.constraint('evenlength', 'Length should be even')
            def validate_evenlength(self, value):
                if len(value) % 2 != 0:
                    raise exceptions.ConstraintError("'%s' length is not even")

        t = MyType()

        self.assertEqual(
            t.validate_evenlength._constraint, 'evenlength'
        )
        self.assertEqual(
            t.validate_evenlength._constraint_hint, 'Length should be even'
        )

        self.assertEqual(
            t.get_jsonschema(), {
                'type': 'string',
                'constraints': {
                    'evenlength': 'Length should be even'
                }
            }
        )
