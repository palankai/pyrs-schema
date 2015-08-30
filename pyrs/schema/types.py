"""
This module introduce the basic schema types.
"""
import collections
import datetime

import isodate
import six

from . import base
from . import exceptions
from . import formats
from . import lib


class String(base.Base):
    """
    String specific arguments:
        pattern:
            The value of this keyword MUST be a string. This string SHOULD be
            a valid regular expression, according to the ECMA 262 regular
            expression dialect. A string instance is considered valid if the
            regular expression matches the instance successfully.
            Recall: regular expressions are not implicitly anchored.
        minlen (int >=0):
            The value of this keyword MUST be an integer. This integer MUST be
            greater than, or equal to, 0. A string instance is valid against
            this keyword if its length is greater than, or equal to,
            the value of this keyword.
        maxlen (int >=minlen):
            The value of this keyword MUST be an integer. This integer MUST be
            greater than, or equal to, 0. A string instance is valid against
            this keyword if its length is less than, or equal to,
            the value of this keyword.
        blank (bool):
            The value of `blank` MUST be a boolean.
            Successful validation depends on presence and value of `min_len`.
            If `min_len` is present and its value is greather than 0 this
            keyword has no effect. If `min_len` is not present or its value is
            0 the value of `min_len` will be set to 1.
    """
    _type = 'string'

    def get_jsonschema(self, context=None):
        schema = super(String, self).get_jsonschema(context=context)
        if self.has_attr('pattern', six.string_types):
            schema['pattern'] = self.get_attr('pattern')
        if self.has_attr('min_len', int):
            schema['minLength'] = self.get_attr('min_len')
        if not self.get_attr('blank', default=True, expected=bool):
            schema['minLength'] = max(self.get_attr('min_len', 0), 1)
        if self.has_attr('max_len', int):
            schema['maxLength'] = self.get_attr('max_len')
        return schema


class Number(base.Base):
    """
    Number specific agruments:
        maximum, exclusive_max:
            The value of `maximum` MUST be a number. The value of
            `exclusive_max` MUST be a boolean.
            If `exclusive_max` is present, `maximum` MUST also be present.
            Successful validation depends on the presence and value of
            `exclusive_max`. If it iss is not present, or has boolean value
            false, then the instance is valid if it is lower than, or equal to,
            the value of `maximum`. If `exclusive_max` has boolean value true,
            the instance is valid if it is strictly lower than the
            value of `maximum`
        minimum, exclusive_min:
            The value of `minimum` MUST be a number. The value of
            `exclusive_min` MUST be a boolean.
            If `exclusive_min` is present, `minimum` MUST also be present.
            Successful validation depends on the presence and value of
            `exclusive_min`. If it iss is not present, or has boolean value
            false, then the instance is valid if it is greater than,
            or equal to, the value of `minimum`. If `exclusive_min` is present
            and has boolean value true, the instance is valid if it is strictly
            greater than the value of `minimum`.
        multiple:
            The value MUST be an number. This number MUST be strictly
            greater than 0. A numeric instance is valid against `multiple`
            if the result of the division of the instance by this keyword's
            value is an integer.
    """
    _type = 'number'

    def get_jsonschema(self, context=None):
        schema = super(Number, self).get_jsonschema(context=context)
        if self.has_attr('multiple', int):
            schema['multipleOf'] = self.get_attr('multiple')
        if self.has_attr('maximum', int):
            schema['maximum'] = self.get_attr('maximum')
        if self.has_attr('minimum', int):
            schema['minimum'] = self.get_attr('minimum')
        if self.has_attr('exclusive_max', bool) and 'maximum' in schema:
            schema['exclusiveMaximum'] = self.get_attr('exclusive_max')
        if self.has_attr('exclusive_min', bool) and 'minimum' in schema:
            schema['exclusiveMinimum'] = self.get_attr('exclusive_min')
        return schema


class Integer(Number):
    """
    Integer specific agruments:
        maximum, exclusive_max:
            The value of `maximum` MUST be a number. The value of
            `exclusive_max` MUST be a boolean.
            If "exclusiveMaximum" is present, "maximum" MUST also be present.
            Successful validation depends on the presence and value of
            `exclusive_max`. If it iss is not present, or has boolean value
            false, then the instance is valid if it is lower than, or equal to,
            the value of `maximum`. If `exclusive_max` has boolean value true,
            the instance is valid if it is strictly lower than the
            value of `maximum`
        minimum, exclusive_min:
            The value of `minimum` MUST be a number. The value of
            `exclusive_min` MUST be a boolean.
            If "exclusiveMinimum" is present, "minimum" MUST also be present.
            Successful validation depends on the presence and value of
            `exclusive_min`. If it iss is not present, or has boolean value
            false, then the instance is valid if it is greater than,
            or equal to, the value of `minimum`. If `exclusive_min` is present
            and has boolean value true, the instance is valid if it is strictly
            greater than the value of `minimum`.
        multiple:
            The value MUST be an number. This number MUST be strictly
            greater than 0. A numeric instance is valid against `multiple`
            if the result of the division of the instance by this keyword's
            value is an integer.
    """
    _type = "integer"


class Boolean(base.Base):
    _type = 'boolean'


class Array(base.Base):
    """
    Successful validation of an array instance with regards to these two
    keywords is determined as follows:

    if "items" is not present, or its value is an object, validation of
    the instance always succeeds, regardless of the value of "additional"

    if the value of "additional" is boolean value true or an object,
    validation of the instance always succeeds;

    if the value of "additional" is boolean value false and the value of
    "items" is an array, the instance is valid if its size is less than,
    or equal to, the size of "items".

    Array specific options:
        min_items:
            An array instance is valid against "min_items" if its size is
            greater than, or equal to, the value of this keyword.
        max_items:
            An array instance is valid against "max_items" if its size is
            less than, or equal to, the value of this keyword.
        unique_items:
            If this keyword has boolean value false, the instance validates
            successfully. If it has boolean value true, the instance validates
            successfully if all of its elements are unique.
    """
    _type = 'array'

    def get_jsonschema(self, context=None):
        schema = super(Array, self).get_jsonschema(context=context)
        if self.has_attr('additional'):
            if isinstance(self.get_attr('additional'), base.Schema):
                schema['additionalItems'] = \
                    self.get_attr('additional').get_jsonschema(context=context)
            elif isinstance(self.get_attr('additional'), bool):
                schema['additionalItems'] = self.get_attr('additional')
            else:
                raise TypeError('The additional should be bool or schema')
        if self.get_attr('max_items') is not None:
            schema['maxItems'] = self.get_attr('max_items')
        if self.get_attr('min_items') is not None:
            schema['minItems'] = self.get_attr('min_items')
        if self.get_attr('unique_items') is not None:
            schema['uniqueItems'] = self.get_attr('unique_items')
        if self.get_attr('items'):
            if isinstance(self.get_attr('items'), (list, tuple)):
                schema['items'] = [
                    s.get_jsonschema(context=context)
                    for s in self.get_attr('items')
                ]
            else:
                schema['items'] = \
                    self.get_attr('items').get_jsonschema(context=context)
        return schema


class Object(base.Base):
    """Declarative schema object

    Object specific attributes:
        additional:
            boolean value: enable or disable extra items on the object
            schema: items which are valid against the schema allowed to extend
            **false by default**
        min_properties:
            An object instance is valid against `min_properties` if its number
            of properties is greater than, or equal to, the value.
        max_properties:
            An object instance is valid against `max_properties` if its number
            of properties is less than, or equal to, the value.
        pattern:
            Should be a dict where the keys are valid regular excpressions
            and the values are schema instances. The object instance is valid
            if the extra properties (which are not listed as property) valid
            against the schema while name is match on the pattern.

        Be careful, the pattern sould be explicit as possible, if the pattern
        match on any normal property the validation should be successful
        against them as well.

        A normal object should looks like the following:

        .. code:: python

            class Translation(types.Object):
                keyword = types.String()
                value = types.String()

                class Attrs:
                    additional = False
                    patterns = {
                        'value_[a-z]{2}': types.String()
                    }
    """
    _type = "object"
    _attrs = {'additional': False}

    def __init__(self, extend=None, **attrs):
        super(Object, self).__init__(**attrs)
        if extend:
            self._fields.update(extend)

    def get_jsonschema(self, context=None):
        schema = super(Object, self).get_jsonschema(context=context)
        if self.get_attr('additional') is not None:
            if isinstance(self.get_attr('additional'), bool):
                schema['additionalProperties'] = self.get_attr('additional')
            else:
                schema['additionalProperties'] = \
                    self.get_attr('additional').get_jsonschema(context=context)
        if self.get_attr('min_properties') is not None:
            schema['minProperties'] = self.get_attr('min_properties')
        if self.get_attr('max_properties') is not None:
            schema['maxProperties'] = self.get_attr('max_properties')
        if self.get_attr('patterns'):
            patterns = collections.OrderedDict()
            for reg, pattern in self.get_attr('patterns').items():
                patterns[reg] = pattern.get_jsonschema(context=context)
            schema['patternProperties'] = patterns
        if context is None:
            context = {}
        attr_exclude_tags = lib.ensure_set(self.get_attr('exclude_tags'))
        ctx_exclude_tags = lib.ensure_set(context.get('exclude_tags'))
        exclude_tags = attr_exclude_tags | ctx_exclude_tags
        if attr_exclude_tags:
            context = context.copy()
            context['exclude_tags'] = exclude_tags
        required = []
        properties = collections.OrderedDict()
        for key, prop in self._fields.items():
            if key in self.get_attr('exclude', []):
                continue
            if self.get_attr('include'):
                if key not in lib.ensure_list(self.get_attr('include')):
                    continue
            if exclude_tags and prop.has_tags(exclude_tags):
                continue
            name = prop.get_attr("name", key)
            properties[name] = prop.get_jsonschema(context=context)
            if prop.get_attr('required'):
                required.append(name)
        schema["properties"] = properties
        if required:
            schema['required'] = sorted(required)
        return schema

    @property
    def fields(self):
        return self._fields

    def extend(self, properties, context=None):
        """Extending the exist same with new properties.
        If you want to extending with an other schema, you should
        use the other schame `properties`
        """
        self._fields.update(properties)

    def to_python(self, value, context=None):
        """Convert the value to a real python object"""
        value = value.copy()
        res = {}
        errors = []
        for field, schema in self._fields.items():
            name = schema.get_attr('name', field)
            if name in value:
                try:
                    res[field] = schema.to_python(
                        value.pop(name),
                        context=context
                    )
                except exceptions.ValidationErrors as ex:
                    self._update_errors_by_exception(errors, ex, name)
        self._raise_exception_when_errors(errors, value)
        res.update(value)
        return res

    def to_raw(self, value, context=None):
        """Convert the value to a JSON compatible value"""
        if value is None:
            return None
        res = {}
        value = value.copy()
        errors = []
        for field in list(set(value) & set(self._fields)):
            schema = self._fields.get(field)
            name = schema.get_attr('name', field)
            try:
                res[name] = \
                    schema.to_raw(value.pop(field), context=context)
            except exceptions.ValidationErrors as ex:
                self._update_errors_by_exception(errors, ex, name)

        self._raise_exception_when_errors(errors, value)
        res.update(value)
        return res

    def _update_errors_by_exception(self, errors, ex, name):
        for error in ex.errors:
            if error['path']:
                error['path'] = name+'.'+error['path']
            errors.append(error)

    def _raise_exception_when_errors(self, errors, value):
        if errors:
            raise exceptions.ValidationErrors(
                '%s validation error(s) raised' % len(errors),
                value=value,
                errors=errors
            )


class Date(String):
    _attrs = {'format': 'date'}

    def to_python(self, value, context=None):
        if isinstance(value, datetime.date):
            return value
        try:
            return isodate.parse_date(value)
        except (isodate.ISO8601Error, TypeError):
            raise exceptions.ValidationError(
                "Invalid date value '%s'" % value,
                value=value,
                invalid='format',
                against='date'
            )

    def to_raw(self, value, context=None):
        if isinstance(value, datetime.date):
            return isodate.date_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_python(value, context=context)
            return value
        raise exceptions.ValidationError(
            "Invalid date value '%s' and type %s" % (value, type(value)),
            value=value,
            invalid='type',
            against='date'
        )


class Time(String):
    _attrs = {'format': 'time'}

    def to_python(self, value, context=None):
        if isinstance(value, datetime.time):
            return value
        try:
            return isodate.parse_time(value)
        except (isodate.ISO8601Error, TypeError):
            raise exceptions.ValidationError(
                "Invalid time value '%s'" % value,
                value=value,
                invalid='format',
                against='time'
            )

    def to_raw(self, value, context=None):
        if isinstance(value, datetime.time):
            return isodate.time_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_python(value, context=context)
            return value
        raise exceptions.ValidationError(
            "Invalid time value '%s' and type %s" % (value, type(value)),
            value=value,
            invalid='type',
            against='time'
        )


class DateTime(String):
    _attrs = {'format': 'datetime'}

    def to_python(self, value, context=None):
        if isinstance(value, datetime.datetime):
            return value
        try:
            return formats.parse_datetime(value)
        except (isodate.ISO8601Error, TypeError):
            raise exceptions.ValidationError(
                "Invalid datetime value '%s'" % value,
                value=value,
                invalid='format',
                against='datetime'
            )

    def to_raw(self, value, context=None):
        if isinstance(value, datetime.datetime):
            return isodate.datetime_isoformat(value)
        if isinstance(value, six.string_types):
            self.to_python(value, context=context)
            return value
        raise exceptions.ValidationError(
            "Invalid datetime value '%s' and type %s" % (value, type(value)),
            value=value,
            invalid='type',
            against='datetime'
        )


class Duration(String):
    _attrs = {'format': 'duration'}

    def to_python(self, value, context=None):
        if isinstance(value, (int, float)):
            return datetime.timedelta(seconds=value)
        if isinstance(value, datetime.timedelta):
            return value
        try:
            return isodate.parse_duration(value)
        except (isodate.ISO8601Error, TypeError):
            raise exceptions.ValidationError(
                "Invalid duration value '%s'" % value,
                value=value,
                invalid='format',
                against='duration'
            )

    def to_raw(self, value, context=None):
        if isinstance(value, datetime.timedelta):
            return isodate.duration_isoformat(value)
        if isinstance(value, (int, float)):
            return isodate.duration_isoformat(
                datetime.timedelta(seconds=value)
            )
        if isinstance(value, six.string_types):
            self.to_python(value)
            return value
        raise exceptions.ValidationError(
            "Invalid duration value '%s' and type %s" % (value, type(value)),
            value=value,
            invalid='type',
            against='timedelta'
        )


class TimeDelta(Number):

    def to_python(self, value, context=None):
        if isinstance(value, (int, float)):
            return datetime.timedelta(seconds=value)
        if isinstance(value, datetime.timedelta):
            return value
        raise exceptions.ValidationError(
            "Invalid timedelta value '%s'" % value,
            value=value,
            invalid='type',
            against='timedelta'
        )

    def to_raw(self, value, context=None):
        if isinstance(value, datetime.timedelta):
            return value.total_seconds()
        if isinstance(value, (int, float)):
            return value
        raise exceptions.ValidationError(
            "Invalid timedelta value '%s' and type %s" % (value, type(value)),
            value=value,
            invalid='type',
            against='timedelta'
        )


class Enum(base.Base):
    """JSON generic enum class

    :param enum: list of possible values
    :type enum: list
    """

    def get_jsonschema(self, context=None):
        """Ensure the generic schema, remove `types`

        :return: Gives back the schema
        :rtype: dict
        """
        schema = super(Enum, self).get_jsonschema(context=None)
        schema.pop('type')
        if self.get_attr('enum'):
            schema['enum'] = self.get_attr('enum')
        return schema


class Ref(base.Base):

    def get_jsonschema(self, context=None):
        schema = super(Ref, self).get_jsonschema(context=context)
        schema.pop('type')
        assert not schema
        return {'$ref': '#/definitions/'+self.get_attr('ref')}
