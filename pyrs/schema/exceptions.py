class SchemaError(Exception):
    """
    Core exception, you can use it to catch all kind of errors.
    Unlikely to raised directly. Could contain multiple errors.
    """
    def __init__(self, message, value, error=None):
        super(SchemaError, self).__init__(message)
        self.error = error
        self.value = value


class FormatError(SchemaError):
    """
    Cover serialization and deserialization errors and related parse errors.
    It would be raised when the  object cannot be converted.
    """

    def __init__(self, message='Unrecognised input format', value=None):
        super(FormatError, self).__init__(message, value, error='FormatError')


class ParseError(SchemaError):
    """
    Cover serialization and deserialization errors and related parse errors.
    It would be raised when the  object cannot be converted.
    """

    def __init__(self, message, value, error='ParseError'):
        super(ParseError, self).__init__(message, value, error)


class ValidationError(SchemaError):
    """
    Cover the validation errors.
    """
    def __init__(
            self, message, value, errors=None, error='ValidationError',
            path=None, invalid=None, against=None
    ):
        super(ValidationError, self).__init__(message, value, error)
        self.errors = errors
        self.path = path
        self.invalid = invalid
        self.against = against
