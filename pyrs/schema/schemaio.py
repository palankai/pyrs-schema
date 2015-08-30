"""
This module introduce the base classes for reading and writing data based on
schema.
The preferred way is using reader is writer rather than using the
schema itself. It gives more flexibility and more extensibility.

.. todo::
    Note that this package in this version does nothing. Just give an early
    interface.
"""
import inspect
import json
import six


from . import base
from . import exceptions


class SchemaIO(object):
    """
    The schema IO gives chance to Schema remain independent from the
    serialisation method. Even the schema provide conversion still just
    based on primitive values.
    """

    def __init__(self, schema, context=None):
        if inspect.isclass(schema):
            schema = schema()
        self.schema = schema
        self.context = context


class SchemaWriter(SchemaIO):
    """
    Abstract implementation of schema writer. The main purpose of this class
    to ensure different useage of the schema. Add extra value if it's
    necessary which can't be implemented by the schema itself.
    """

    def write(self):
        raise NotImplementedError(
            'The write method of SchemaWriter is abstract'
        )


class Writer(SchemaIO):
    """
    Writer abstract class
    At least the `write` method should be implemented

    .. code:: python

        sw = Writer(CustomSchema())
        encoded_data = sw.write({'custom': 'value'})
    """

    def write(self, data):
        """
        With `self.schema` select the proper schema, encode the given
        data then gives it back.
        """
        raise NotImplementedError(
            'The write method of Writer is abstract'
        )


class Reader(SchemaIO):
    """
    Reader abstract class
    At least the `read` method should be implemented

    .. code:: python

        sw = Reader(CustomSchema())
        data = sw.write(<custom datastructure>)
    """

    def read(self, data):
        """
        with `self.schema` select the proper schema and read the data,
        validate the input and gives back the decoded value
        """
        raise NotImplementedError(
            'The read method of Reader is abstract'
        )


class JSONSchemaWriter(SchemaWriter):

    def write(self, context=None):
        return self.schema.get_schema(context=context)

    def dump(self, context=None):
        return json.dumps(self.write(context=context))


class JSONWriter(Writer):

    def write(self, data):
        return self.schema.dump(data)


class JSONReader(Reader):

    def read(self, data):
        self._validate_format(data)
        value = self._load(data)
        self._validate(value)
        return self._to_python(value)

    def _validate_format(self, data):
        if not isinstance(data, six.string_types):
            raise exceptions.ParseError(
                'Unrecognised input format: %s given, string type expected'
                % type(data),
                value=data
            )

    def _load(self, data):
        try:
            return json.loads(data)
        except ValueError as ex:
            raise exceptions.ParseError(ex.args[0], value=data)

    def _validate(self, value):
        validator = base._make_validator(
            self.schema.get_schema(context=self.context)
        )
        errors = []
        for e in validator.iter_errors(value):
            errors.append({
                'error': 'ValidationError',
                'message': e.message,
                'value': e.instance,
                'invalid': e.schema_path[-1],
                'against': e.validator_value,
                'path': ".".join(e.path),
            })
        if errors:
            raise exceptions.ValidationErrors(
                '%s validation error(s) raised' % len(errors),
                value=value,
                errors=errors
            )

    def _to_python(self, value):
        return self.schema.to_python(value, context=self.context)
