#!/usr/bin/env python3

import pendulum

import re

from tinydb_serialization import Serializer
from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_smartcache import SmartCacheTable

from pendulum import parse

import dateutil
from dateutil import rrule
from dateutil.rrule import *

from jinja2 import Environment, Template

period_regex = re.compile(r'(([+-]?)(\d+)([wdhm]))+?')

period_hsh = dict(
    z=pendulum.Interval(seconds=0),
    m=pendulum.Interval(minutes=1),
    h=pendulum.Interval(hours=1),
    d=pendulum.Interval(days=1),
    w=pendulum.Interval(weeks=1),
        )

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
        current_id = int(pendulum.now('UTC').format("%Y%m%d%H%M%S%f"))
        self._last_id = current_id

        return current_id


TinyDB.table_class = DatetimeCacheTable

class PendulumDateTimeSerializer(Serializer):
    """
    This class handles both aware and 'factory' pendulum objects. 

    Encoding: If obj.tzinfo.abbrev is '-00' (tz=Factory), it is interpreted as naive, serialized without conversion and an 'N' is appended. Otherwise it is interpreted as aware, converted to UTC and an 'A' is appended. 
    Decoding: If the serialization ends with 'A', the pendulum object is treated as UTC and converted to localtime. Otherwise, the object is treated as localtime and no conversion is performed.

    This serialization discards both seconds and microseconds but preserves hours and minutes.
    """

    OBJ_CLASS = pendulum.pendulum.Pendulum

    def encode(self, obj):
        """
        Serialize '-00' objects without conversion but with 'N' for 'Naive' appended. Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        """
        if obj.tzinfo.abbrev == '-00':
            return obj.format('YYYYMMDDTHHmm[N]', formatter='alternative')
        else:
            return obj.in_timezone('UTC').format('YYYYMMDDTHHmm[A]', formatter='alternative' )

    def decode(self, s):
        """
        Return the serialization as a datetime object. If the serializaton ends with 'A',  first converting to localtime and returning an aware datetime object. If the serialization ends with 'N', returning without conversion as a naive datetime object. 
        """
        if s[-1] == 'A':
            return pendulum.from_format(s[:-1], '%Y%m%dT%H%M', 'UTC').in_timezone('local')
        else:
            return pendulum.from_format(s[:-1], '%Y%m%dT%H%M', 'Factory')


class PendulumDateSerializer(Serializer):
    """
    This class handles pendulum date objects.
    """
    OBJ_CLASS = pendulum.pendulum.Date 

    def encode(self, obj):
        """
        Serialize the naive date object without conversion.
        """
        return obj.format('%Y%m%d')

    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        return pendulum.from_format(s, '%Y%m%d').date()


class PendulumIntervalSerializer(Serializer):
    """
    This class handles pendulum interval (timedelta) objects.
    """
    OBJ_CLASS = pendulum.Interval  

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
        return pendulum.Interval(*days_seconds)


serialization = SerializationMiddleware()
serialization.register_serializer(PendulumDateTimeSerializer(), 'TinyPendulumDateTime')
serialization.register_serializer(PendulumDateSerializer(), 'TinyPendulumDate')
serialization.register_serializer(PendulumIntervalSerializer(), 'TinyPendulumInterval')

########################
### end TinyDB setup ###
########################


def parse_datetime(s):
    """
    's' will have the format 'datetime string' followed, optionally by a comma and a tz specification. Return a date object if the parsed datetime is exactly midnight. Otherwise return a naive datetime object if tz == 'float' or an aware datetime object using tzlocal if tz is None (missing) and using the provided tz otherwise.  
    >>> dt = parse_datetime("2015-10-15 2p")
    >>> dt[1]
    <Pendulum [2015-10-15T14:00:00-04:00]>
    >>> dt = parse_datetime("2015-10-15")
    >>> dt[1]
    <Date [2015-10-15]>

    To get a datetime for midnight, schedule for 1 second later and note
    that the second is removed from the datetime:
    >>> dt = parse_datetime("2015-10-15 00:00:01")
    >>> dt[1]
    <Pendulum [2015-10-15T00:00:00-04:00]>
    >>> dt = parse_datetime("2015-10-15 2p, float")
    >>> dt[1]
    <Pendulum [2015-10-15T14:00:00+00:00]>
    >>> dt = parse_datetime("2015-10-15 2p, US/Pacific")
    >>> dt[1]
    <Pendulum [2015-10-15T14:00:00-07:00]>
    """
    parts = s.split(", ")
    if len(parts) < 2:
        tz = None
        ok = 'none'
    else:
        tz = parts[1].strip()
        if tz == 'float':
            tz = 'Factory'
            ok = 'naive'
        else:
            ok = 'aware'
    s = parts[0]

    try:
        res = parse(s, tz=tz)
    except:
        return False, "Could not process '{}'".format(s)
    else:
        if (res.hour, res.minute, res.second, res.microsecond) == (0, 0, 0, 0):
            return 'date', res.date()
        else:
            return ok, res.replace(second=0, microsecond=0)


def parse_period(s):
    """\
    Take a period string and return a corresponding pendulum interval.
    Examples:
        parse_period('-2w3d4h5m')= Interval(weeks=-2,days=3,hours=4,minutes=5)
        parse_period('1h30m') = Inter(hours=1, minutes=30)
        parse_period('-10m') = timedelta(minutes=10)
    where:
        w: weeks
        d: days
        h: hours
        m: minutes
    If an integer is passed or a string that can be converted to an
    integer, then return a timedelta corresponding to this number of
    minutes if 'minutes = True', and this number of days otherwise.
    Minutes will be True for alerts and False for beginbys.

    >>> 3*60*60+5*60
    11100
    >>> parse_period("2d-3h5m")[1]
    <Interval [1 day 21 hours 5 minutes]>
    >>> pendulum.create(2015, 10, 15, 9, 0, tz='local') + parse_period("-25m")[1]
    <Pendulum [2015-10-15T08:35:00-04:00]>
    >>> pendulum.create(2015, 10, 15, 9, 0) + parse_period("1d")[1]
    <Pendulum [2015-10-16T09:00:00+00:00]>
    >>> pendulum.create(2015, 10, 15, 9, 0) + parse_period("1w-2d+3h")[1]
    <Pendulum [2015-10-20T12:00:00+00:00]>
    """
    td = period_hsh['z']

    m = period_regex.findall(s)
    if not m:
        return False, "Invalid period '{0}'".format(s)
    for g in m:
        if g[1] == '-':
            num = -int(g[2])
        else:
            num = int(g[2])
        td += num * period_hsh[g[3]]
    return True, td


if __name__ == '__main__':
    print('\n\n')
    import doctest
    doctest.testmod()

    db = TinyDB('db.json', storage=serialization)
    db.purge()
    db.insert({'naive pendulum': pendulum.Pendulum(2017, 9, 7, 14, 0, 0, tzinfo='Factory')})

    db.insert({'pacific pendulum': pendulum.Pendulum(2017, 9, 7, 14, 0, 0, tzinfo='US/Pacific') })
    db.insert({'local pendulum': pendulum.Pendulum(2017, 9, 7, 14, 0, 0, tzinfo='local') })
    db.insert({'pendulum list': [pendulum.Pendulum(2017, 9, 7, 12, 0, 0), pendulum.Pendulum(2017, 9, 7, 12, 0, 0, tzinfo='US/Pacific')]})
    db.insert({'pendulum date': pendulum.Pendulum(2017, 9, 7, tzinfo='Factory').date() })
    db.insert({'pendulum interval': pendulum.Interval(weeks=1, days=3, hours=7, minutes=15)})
    # hsh = {'type': '*', 'summary': 'my event', 's':  datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Pacific')), 'e': timedelta(hours=1, minutes=15)}
    # db.insert(hsh)
    for item in db:
        print(item.eid, item)

