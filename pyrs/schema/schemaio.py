"""
This module introduce the base classes for reading and writing data based on
schema.
The preferred way is using reader is writer rather than using the
schema itself. It gives more flexibility and more extensibility.

.. todo::
    Note that this package in this version does nothing. Just give an early
    interface.
"""
import datetime
import inspect
import json
import six

import isodate

from . import base
from . import exceptions
from . import types


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


class Validator(SchemaIO):
    """
    Abstract base class of validators.
    """

    def validate(self, data):
        raise NotImplementedError(
            'The validate method of Validator is abstract'
        )


class SchemaWriter(object):
    """
    Abstract implementation of schema writer. The main purpose of this class
    to ensure different useage of the schema. Add extra value if it's
    necessary which can't be implemented by the schema itself.
    """

    def __init__(self, context=None):
        self.context = context

    def write(self, schema):
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

    def write(self, schema, context=None):
        return json.dumps(self.extract(schema, context=context))

    def extract(self, schema, context=None):
        if inspect.isclass(schema):
            schema = schema()
        return schema.get_jsonschema(context=context)


class JSONSchemaValidator(Validator):

    def __init__(self, schema, context=None):
        super(JSONSchemaValidator, self).__init__(schema, context)
        self._make_validator()

    def validate(self, data):
        errors = []
        for ex in self.validator.iter_errors(data):
            self._update_errors_with_exception(errors, ex)
        self._raise_exception_when_errors(errors, data)

    def _make_validator(self):
        self.validator = base._make_validator(
            self.schema.get_jsonschema(context=self.context)
        )

    def _update_errors_with_exception(self, errors, ex, path_prefix=None):
        path = list(ex.path)
        if path_prefix:
            path.insert(0, path_prefix)
        errors.append({
            'error': 'ValidationError',
            'message': ex.message,
            'value': ex.instance,
            'invalid': ex.schema_path[-1],
            'against': ex.validator_value,
            'path': ".".join(path),
        })

    def _raise_exception_when_errors(self, errors, data):
        if errors:
            raise exceptions.ValidationErrors(
                '%s validation error(s) raised' % len(errors),
                value=data,
                errors=errors
            )


class JSONSchemaDictValidator(JSONSchemaValidator):

    def _make_validator(self):
        self.validators = {}
        for field, item in self.schema.items():
            self.validators[field] = base._make_validator(
                item.get_jsonschema(context=self.context)
            )

    def validate(self, data):
        if not isinstance(data, dict):
            raise exceptions.ParseError(
                'Unrecognised input format: %s given, dict type expected'
                % type(data),
                value=data
            )
        errors = []
        for field, value in data.items():
            if field not in self.validators:
                continue
            validator = self.validators[field]
            for ex in validator.iter_errors(value):
                self._update_errors_with_exception(
                    errors, ex, path_prefix=field
                )
        self._raise_exception_when_errors(errors, data)


def select_json_validator(schema, context=None):
    if isinstance(schema, dict):
        return JSONSchemaDictValidator(schema, context=context)
    return JSONSchemaValidator(schema, context=context)


class JSONWriter(Writer):

    def __init__(self, schema, context=None):
        super(JSONWriter, self).__init__(schema, context=context)
        self.validator = select_json_validator(self.schema, context)

    def write(self, data):
        data = self._to_raw(data)
        self.validator.validate(data)
        return self._dumps(data)

    def _to_raw(self, data):
        return self.schema.to_raw(data, context=self.context)

    def _dumps(self, data):
        return json.dumps(data, default=self._dump_default)

    def _dump_default(self, obj):
        if isinstance(obj, datetime.datetime):
            return isodate.datetime_isoformat(obj)
        elif isinstance(obj, datetime.date):
            return isodate.date_isoformat(obj)
        elif isinstance(obj, datetime.time):
            return isodate.time_isoformat(obj)
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        else:
            raise TypeError(obj)


class JSONReader(Reader):

    def __init__(self, schema, context=None):
        super(JSONReader, self).__init__(schema, context=context)
        self.validator = select_json_validator(self.schema, context)

    def read(self, data):
        self._validate_format(data)
        value = self._loads(data)
        self.validator.validate(value)
        return self._to_python(value)

    def _validate_format(self, data):
        if not isinstance(data, six.string_types):
            raise exceptions.ParseError(
                'Unrecognised input format: %s given, string type expected'
                % type(data),
                value=data
            )

    def _loads(self, data):
        try:
            return json.loads(data)
        except ValueError as ex:
            raise exceptions.ParseError(ex.args[0], value=data)

    def _to_python(self, value):
        return self.schema.to_python(value, context=self.context)


class JSONFormReader(JSONReader):

    def __init__(self, schema, context=None):
        super(JSONFormReader, self).__init__(schema, context=context)
        self.validator = select_json_validator(self.schema, context)

    def read(self, data):
        self._validate_format(data)
        data = data.copy()
        by_name = {}
        for field, prop in self.schema.fields.items():
            by_name[prop.get_attr('name', field)] = prop
        for field in list(set(data) & set(by_name)):
            prop = by_name[field]
            if not isinstance(prop, types.String):
                data[field] = self._loads(data[field])
        self.validator.validate(data)
        return self._to_python(data)

    def _validate_format(self, data):
        if not isinstance(data, dict):
            raise exceptions.ParseError(
                'Unrecognised input format: %s given, dict type expected'
                % type(data),
                value=data
            )

    def _to_python(self, data):
        return self.schema.to_python(data, context=self.context)
