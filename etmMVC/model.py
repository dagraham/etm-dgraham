#!/usr/bin/env python3

from datetime import datetime, date, timedelta
import arrow
import re
from tinydb_serialization import Serializer
from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_smartcache import SmartCacheTable

import dateutil
from dateutil.parser import parse
from dateutil import rrule
from dateutil.tz import (tzlocal, gettz, tzutc)

ONEMINUTE = timedelta(minutes=1)
ONEHOUR = timedelta(hours=1)
ONEDAY = timedelta(days=1)
ONEWEEK = timedelta(weeks=1)

period_string_regex = re.compile(r'^\s*([+-]?(\d+[wWdDhHmM])+\s*$)')
week_regex = re.compile(r'[+-]?(\d+)w', flags=re.I)
day_regex = re.compile(r'[+-]?(\d+)d', flags=re.I)
hour_regex = re.compile(r'[+-]?(\d+)h', flags=re.I)
minute_regex = re.compile(r'[+-]?(\d+)m', flags=re.I)
sign_regex = re.compile(r'(^\s*([+-])?)')


##########################
### begin TinyDB setup ###
##########################

class DatetimeCacheTable(SmartCacheTable):

    def _get_next_id(self):
        """
        Use a readable, integer timestamp as the id - unique and stores
        the creation datetime - instead of consecutive integers. E.g.,
        the the id for an item created 2016-06-24 08:14:11:601637 would
        be 20160624081411601637.
        """
        # This must be an int even though it will be stored as a str
        current_id = int(arrow.utcnow().strftime("%Y%m%d%H%M%S%f"))
        self._last_id = current_id

        return current_id


TinyDB.table_class = DatetimeCacheTable

class DateTimeSerializer(Serializer):
    """
    This class handles both aware and naive datetime objects. 

    Encoding: If the datetime object is aware, it is first converted to UTC and then encoded with an 'A' appended to the serialization. Otherwise it is serialized without conversion and an 'N' is appended.

    Decoding: If the serialization ends with 'A', the datetime object is treated as UTC and then converted to localtime. Otherwise, the datetime object is treated as localtime and no conversion is necessary.

    This serialization discards both seconds and microseconds but preserves hours and minutes.
    """

    OBJ_CLASS = datetime

    def encode(self, obj):
        """
        Serialize naive datetimes objects without conversion but with 'N' for 'Naive' appended. Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        """
        if obj.tzinfo is None:
            return obj.strftime('%Y%m%dT%H%MN')
        else:
            return obj.astimezone(tzutc()).strftime('%Y%m%dT%H%MA')

    def decode(self, s):
        """
        Return the serialization as a datetime object. If the serializaton ends with 'A',  first converting to localtime and returning an aware datetime object. If the serialization ends with 'N', returning without conversion as a naive datetime object. 
        """
        if s[-1] == 'A':
            return datetime.strptime(s[:-1], '%Y%m%dT%H%M').replace(tzinfo=tzutc()).astimezone(tzlocal())
        else:
            return datetime.strptime(s[:-1], '%Y%m%dT%H%M')


class DateSerializer(Serializer):
    OBJ_CLASS = date  # The class handles date objects

    def encode(self, obj):
        """
        Serialize the naive date object without conversion.
        """
        return obj.strftime('%Y%m%d')

    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        return datetime.strptime(s, '%Y%m%d').date()


class TimeDeltaSerializer(Serializer):
    OBJ_CLASS = timedelta  # The class handles timedelta objects

    def encode(self, obj):
        """
        Serialize the timedelta object as days.seconds.
        """
        return "{0}.{1}".format(obj.days, obj.seconds)

    def decode(self, s):
        """
        Return the serialization as a timedelta object.
        """
        days_seconds = (int(x) for x in s.split('.')) 
        return timedelta(*days_seconds)


class RruleSerializer(Serializer):
    """
    All rrule datetimes are naive. When the rrule object is first created, the value for dtstart will be taken from the value of `s`, which is required and may either be aware, UTC time or naive. If aware, then all the rrule instances will need to be converted to localtime. 
    """

    OBJ_CLASS = dateutil.rrule.rrule  # The class handles rrule objects


    def encode(self, obj):
        """
        Serialize the rrule object.
        """
        return obj.__str__()


    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        print('s', s)
        return dateutil.rrule.rrulestr(s)


serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDateTime')
serialization.register_serializer(DateSerializer(), 'TinyDate')
serialization.register_serializer(TimeDeltaSerializer(), 'TinyTimeDelta')
serialization.register_serializer(RruleSerializer(), 'TinyRrule')

########################
### end TinyDB setup ###
########################


def parse_datetime(s, tz=None):
    """
    Return a date object if the parsed time is exactly midnight. Otherwise return a naive datetime object if tz == float or an aware datetime object using tzlocal if tz is None and the provided tz otherwise.  
    >>> dt = parse_datetime("2015-10-15 2p")
    >>> dt
    datetime.datetime(2015, 10, 15, 14, 0, tzinfo=tzlocal())

    >>> dt = parse_datetime("2015-10-15 0h")
    >>> dt
    datetime.date(2015, 10, 15)

    >>> dt = parse_datetime("2015-10-15")
    >>> dt
    datetime.date(2015, 10, 15)

    To get a datetime object for midnight use one second past midnight:
    >>> dt = parse_datetime("2015-10-15 12:00:01a", tz='float')
    >>> dt
    datetime.datetime(2015, 10, 15, 0, 0)

    """

    try:
        res = parse(s, yearfirst=True, dayfirst=False)
    except ValueError:
        return "Could not process '{}'".format(s)
    if (res.hour, res.minute, res.second, res.microsecond) == (0, 0, 0, 0):
        return res.date()
    else:
        res = res.replace(second=0, microsecond=0)
        if tz is None:
            res = res.replace(tzinfo=tzlocal()) 
        elif tz == 'float':
            res = res.replace(tzinfo=None)
        else:
            res = res.replace(tzinfo=gettz(tz))
        return res


def parse_period(s):
    """\
    Take a case-insensitive period string and return a corresponding timedelta.
    Examples:
        parse_period('-2W3D4H5M')= -timedelta(weeks=2,days=3,hours=4,minutes=5)
        parse_period('1h30m') = timedelta(hours=1, minutes=30)
        parse_period('-10') = timedelta(minutes= 10)
    where:
        W or w: weeks
        D or d: days
        H or h: hours
        M or m: minutes
    If an integer is passed or a string that can be converted to an
    integer, then return a timedelta corresponding to this number of
    minutes if 'minutes = True', and this number of days otherwise.
    Minutes will be True for alerts and False for beginbys.

    >>> 3*60*60+5*60
    11100
    >>> parse_period("2d3h5m")[0]
    datetime.timedelta(2, 11100)
    >>> datetime(2015, 10, 15, 9, 0) + parse_period("-25m")[0]
    datetime.datetime(2015, 10, 15, 8, 35)
    >>> datetime(2015, 10, 15, 9, 0) + parse_period("1d")[0]
    datetime.datetime(2015, 10, 16, 9, 0)
    >>> datetime(2015, 10, 15, 9, 0) + parse_period("1w2h")[0]
    datetime.datetime(2015, 10, 22, 11, 0)
    """
    msg = []
    td = timedelta(seconds=0)
    m = period_string_regex.match(s)
    if not m:
        msg.append("Invalid period '{0}'".format(s))
        return None, msg
    m = week_regex.search(s)
    if m:
        td += int(m.group(1)) * ONEWEEK
    m = day_regex.search(s)
    if m:
        td += int(m.group(1)) * ONEDAY
    m = hour_regex.search(s)
    if m:
        td += int(m.group(1)) * ONEHOUR
    m = minute_regex.search(s)
    if m:
        td += int(m.group(1)) * ONEMINUTE
    if type(td) is not timedelta:
        msg.append("Invalid period '{0}'".format(s))
        return None, msg
    m = sign_regex.match(s)
    if m and m.group(1) == '-':
        return -1 * td, msg
    else:
        return td, msg



if __name__ == '__main__':
    import doctest
    doctest.testmod()

    db = TinyDB('db.json', storage=serialization)
    db.purge()
    db.insert({'aware dt': [datetime(2017, 9, 7, 12, 0, 0), datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Pacific'))]})
    db.insert({'local dt': datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Eastern')) })
    db.insert({'local dt': datetime(2017, 9, 7, 12, 0, 0, tzinfo=tzlocal()) })
    db.insert({'date': date(2017, 9, 7)})
    db.insert({'time delta': timedelta(weeks=1, days=3, hours=7, minutes=15)})
    rr = rrule.rrulestr('DTSTART:20170914T105932\nFREQ=MONTHLY;INTERVAL=2;COUNT=10;BYDAY=-1SU,+1SU')
    db.insert({'tr': rr})
    hsh = {'type': '*', 'summary': 'my event', 's':  datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Pacific')), 'e': timedelta(hours=1, minutes=15)}
    db.insert(hsh)
    for item in db:
        print(item.eid, item)

