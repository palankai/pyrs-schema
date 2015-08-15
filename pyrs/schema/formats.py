import datetime
import re

import isodate
import jsonschema
import six


draft4_format_checkers = list(jsonschema.draft4_format_checker.checkers.keys())


def parse_datetime(datetimestring):
    '''
    Parses ISO 8601 date-times into datetime.datetime objects.
    This function uses parse_date and parse_time to do the job, so it allows
    more combinations of date and time representations, than the actual
    ISO 8601:2004 standard allows.
    '''
    try:
        datestring, timestring = re.split('T| ', datetimestring)
    except ValueError:
        raise isodate.ISO8601Error(
            "ISO 8601 time designator 'T' or ' '  missing. Unable to parse "
            "datetime string %r" % datetimestring
        )
    tmpdate = isodate.parse_date(datestring)
    tmptime = isodate.parse_time(timestring)
    return datetime.combine(tmpdate, tmptime)


def format_checker(name, raises=()):
    def wrap(func):
        draft4_format_checkers.append(name)
        func = jsonschema.FormatChecker.cls_checks(name, raises)(func)
        return func
    return wrap


@format_checker('date', (ValueError, isodate.ISO8601Error, ))
def date_format_checker(instance):
    if isinstance(instance, datetime.date):
        return True
    if isinstance(instance, six.string_types):
        return isodate.parse_date(instance)


@format_checker('datetime', (ValueError, isodate.ISO8601Error, ))
def datetime_format_checker(instance):
    if isinstance(instance, datetime.datetime):
        return True
    if isinstance(instance, six.string_types):
        return parse_datetime(instance)


@format_checker('time', (ValueError, isodate.ISO8601Error, ))
def time_format_checker(instance):
    if isinstance(instance, datetime.datetime):
        return True
    if isinstance(instance, six.string_types):
        return isodate.parse_time(instance)


@format_checker('duration', (ValueError, isodate.ISO8601Error, ))
def duration_format_checker(instance):
    if isinstance(instance, (datetime.timedelta, int, float)):
        return True
    if isinstance(instance, six.string_types):
        return isodate.parse_duration(instance)
