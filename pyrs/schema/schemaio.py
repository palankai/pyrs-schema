"""
This module introduce the base classes for reading and writing data based on
schema.
The preferred way is using reader is writer rather than using the
schema itself. It gives more flexibility and more extensibility.

.. todo::
    Note that this package in this version does nothing. Just give an early
    interface.
"""


class SchemaIO(object):
    """
    The schema IO gives chance to Schema remain independent from the
    serialisation method. Even the schema provide conversion still just
    based on primitive values.
    """

    def __init__(self, schema=None):
        self.schema = schema

    def get_schema(self, schema=None):
        """
        Gives back either the given schema or the schema which was defined
        in the constructor.
        If none of the specified it raises AttributeError.
        """
        if not (schema or self.schema):
            raise AttributeError('Schema not specified in either way')
        return schema or self.schema


class SchemaWriter(SchemaIO):
    """
    Writing schema
    .. code:: python

        sw = SchemaWriter(CustomSchema())
        encoded_data = sw.write({'custom': 'value'})
    """

    def write(self, data, schema=None):
        """
        With `self.get_schema()` select the proper schema, encode the given
        data then gives it back.
        """
        return self.get_schema(schema).dump(data)


class SchemaReader(SchemaIO):
    """
    Reading value based on schema
    .. code:: python

        sw = SchemaReader(CustomSchema())
        data = sw.write(<custom datastructure>)
    """

    def read(self, data, schema=None):
        """
        with `self.get_schema()` select the proper schema and read the data,
        validate the input and gives back the decoded value
        """
        return self.get_schema(schema).load(data)


class JSONWriter(SchemaWriter):
    pass


class JSONReader(SchemaReader):
    pass
