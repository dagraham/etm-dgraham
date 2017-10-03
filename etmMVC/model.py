#!/usr/bin/env python3

# from datetime import datetime, date, timedelta
import pendulum
import re
from tinydb_serialization import Serializer
from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_smartcache import SmartCacheTable

import dateutil
from pendulum import parse
# from dateutil.parser import parse
from dateutil import rrule
from dateutil.rrule import *
from dateutil.tz import (tzlocal, gettz, tzutc)

import pickle

ONEMINUTE = pendulum.Interval(minutes=1)
ONEHOUR = pendulum.Interval(hours=1)
ONEDAY = pendulum.Interval(days=1)
ONEWEEK = pendulum.Interval(weeks=1)

period_regex = re.compile(r'(([+-]?)(\d+)([wdhm]))+?', flags=re.I)
# period_string_regex = re.compile(r'^\s*([+-]?(\d+[wWdDhHmM])+\s*$)')
# week_regex = re.compile(r'[+-]?(\d+)w', flags=re.I)
# day_regex = re.compile(r'[+-]?(\d+)d', flags=re.I)
# hour_regex = re.compile(r'[+-]?(\d+)h', flags=re.I)
# minute_regex = re.compile(r'[+-]?(\d+)m', flags=re.I)
# sign_regex = re.compile(r'(^\s*([+-])?)')


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
serialization.register_serializer(PendulumIntervalSerializer(), 'TinyPendulumInterval')
serialization.register_serializer(RruleSerializer(), 'TinyRrule')
serialization.register_serializer(RruleSetSerializer(), 'TinyRruleSet')

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


period_hsh = dict(
    z=pendulum.Interval(seconds=0),
    m=pendulum.Interval(minutes=1),
    h=pendulum.Interval(hours=1),
    d=pendulum.Interval(days=1),
    w=pendulum.Interval(weeks=1),
        )

def parse_period(s):
    """\
    Take a case-insensitive period string and return a corresponding timedelta.
    Examples:
        parse_period('-2W3D4H5M')= timedelta(weeks=-2,days=3,hours=4,minutes=5)
        parse_period('1h30m') = timedelta(hours=1, minutes=30)
        parse_period('-10m') = timedelta(minutes=10)
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
    <Interval [2 days 3 hours 5 minutes]>
    >>> pendulum.Pendulum(2015, 10, 15, 9, 0) + parse_period("-25m")[1]
    <Pendulum [2015-10-15T08:35:00+00:00]>
    >>> pendulum.Pendulum(2015, 10, 15, 9, 0) + parse_period("1d")[1]
    <Pendulum [2015-10-16T09:00:00+00:00]>
    >>> pendulum.Pendulum(2015, 10, 15, 9, 0) + parse_period("1w-2D+3h")[1]
    <Pendulum [2015-10-20T12:00:00+00:00]>
    """
    msg = []
    td = period_hsh['z']

    m = period_regex.findall(s)
    if not m:
        msg.append("Invalid period '{0}'".format(s))
        return False, msg
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

