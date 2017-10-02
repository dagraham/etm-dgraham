#!/usr/bin/env python3

from datetime import datetime, date, timedelta
import pendulum
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
from dateutil.rrule import *
from dateutil.tz import (tzlocal, gettz, tzutc)

import pickle

ONEMINUTE = timedelta(minutes=1)
ONEHOUR = timedelta(hours=1)
ONEDAY = timedelta(days=1)
ONEWEEK = timedelta(weeks=1)

period_regex = re.compile(r'(([+-]?)(\d+)([wdhm]))+?')
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
        current_id = int(pendulum.now('UTC').format("%Y%m%d%H%M%S%f"))
        self._last_id = current_id

        return current_id


TinyDB.table_class = DatetimeCacheTable

class PendulumDateTimeSerializer(Serializer):
    """
    This class handles both aware and 'factory' pendulum objects. 

    Encoding: If the pendulum obj.tzinfo.abbrev != '-00', it is aware and is first converted to UTC and then encoded with an 'A' appended to the serialization. Otherwise, when obj.tzinfo.abbrev == '-00', it is serialized without conversion and an 'N' is appended.

    Decoding: If the serialization ends with 'A', the pendulum object is treated as UTC and converted to localtime. Otherwise, the object is treated as localtime and no conversion is performed.

    This serialization discards both seconds and microseconds but preserves hours and minutes.
    """

    OBJ_CLASS = pendulum.pendulum.Pendulum

    def encode(self, obj):
        """
        Serialize '-00' objects without conversion but with 'N' for 'Naive' appended. Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        """
        if obj.tzinfo.abbrev == '-00':
            # print('naive/factory')
            return obj.format('YYYYMMDDTHHmm[N]', formatter='alternative')
        else:
            # print('aware')
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
    OBJ_CLASS = pendulum.pendulum.Interval  

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
        return dateutil.rrule.rrulestr(s)


class RruleSetSerializer(Serializer):
    """
    All rrule datetimes are naive. When the rrule object is first created, the value for dtstart will be taken from the value of `s`, which is required and may either be aware, UTC time or naive. If aware, then all the rrule instances will need to be converted to localtime. 
    """

    OBJ_CLASS = dateutil.rrule.rruleset  # The class handles rruleset objects


    def encode(self, obj):
        """
        Serialize the rrule object.
        """
        return pickle.dumps(obj, protocol=4)


    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        return pickle.loads(s, protocol=4)


serialization = SerializationMiddleware()
serialization.register_serializer(PendulumDateTimeSerializer(), 'TinyPendulumDateTime')
# serialization.register_serializer(DateTimeSerializer(), 'TinyDateTime')
serialization.register_serializer(PendulumDateSerializer(), 'TinyPendulumDate')
serialization.register_serializer(TimeDeltaSerializer(), 'TinyTimeDelta')
serialization.register_serializer(RruleSerializer(), 'TinyRrule')
serialization.register_serializer(RruleSetSerializer(), 'TinyRruleSet')

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
    >>> parse_period("2d3h5m")[1]
    datetime.timedelta(2, 11100)
    >>> datetime(2015, 10, 15, 9, 0) + parse_period("-25m")[1]
    datetime.datetime(2015, 10, 15, 8, 35)
    >>> datetime(2015, 10, 15, 9, 0) + parse_period("1d")[1]
    datetime.datetime(2015, 10, 16, 9, 0)
    >>> datetime(2015, 10, 15, 9, 0) + parse_period("1w-2d+3h")[1]
    datetime.datetime(2015, 10, 20, 12, 0)
    """
    msg = []
    td = timedelta(seconds=0)

    m = period_regex.findall(s)
    if not m:
        msg.append("Invalid period '{0}'".format(s))
        return False, msg
    for g in m:
        sign = g[1] or '+'
        if g[1] == '-':
            num = -int(g[2])
        else:
            num = int(g[2])
        if g[3] == 'w':
            td += num * ONEWEEK
        elif g[3] == 'd':
            td += num * ONEDAY
        elif g[3] == 'h':
            td += num * ONEHOUR
        elif g[3] == 'm':
            td += num * ONEMINUTE
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
    # rr = rrulestr('DTSTART:20170914T105932\nFREQ=MONTHLY;INTERVAL=2;COUNT=10;BYDAY=-1SU,+1SU')
    # db.insert({'tr': rr})
    # set = rruleset()
    # set.rrule(rrule(WEEKLY, count=4, dtstart = datetime(2017, 9, 14, 9, 0)))
    # set.exdate(datetime(2017, 9, 28, 9, 0))
    # print(list(set))
    # db.insert({'rruleset': set})

    # hsh = {'type': '*', 'summary': 'my event', 's':  datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Pacific')), 'e': timedelta(hours=1, minutes=15)}
    # db.insert(hsh)
    for item in db:
        print(item.eid, item)

