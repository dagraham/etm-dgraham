#!/usr/bin/env python3

from tinydb import TinyDB, Query
from tinydb import __version__ as tinydb_version
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware
import base64  # for do_mask
import pytz
from pytz import timezone
from datetime import datetime
from datetime import tzinfo
from datetime import timedelta
import dateutil
import dateutil.rrule
from dateutil import tz
from dateutil.parser import parse as dateutil_parse
from dateutil.rrule import *
import re

##########################
### begin TinyDB setup ###
##########################

TinyDB.DEFAULT_TABLE = 'items'

AWARE_FMT = '%Y%m%dT%H%MA'
NAIVE_FMT = '%Y%m%dT%H%MN'
DATE_FMT = '%Y%m%d'

WKDAYS_DECODE = {"{0}{1}".format(n, d): "{0}({1})".format(d, n) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']}

WKDAYS_ENCODE = {"{0}({1})".format(d, n): "{0}{1}".format(n, d) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4']}

## Add those without integer prefixes
for wkd in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
    WKDAYS_ENCODE[wkd] = wkd


# def parse(s, **kwd):
#     ## enable pi when read by main
#     pi = dateutil.parser.parserinfo(
#             dayfirst=settings['dayfirst'],
#             yearfirst=settings['yearfirst']
#             )
#     dt = dateutil_parse(s, parserinfo=pi)
#     dt = dateutil_parse(s)
#     if 'tzinfo' in kwd:
#         tzinfo = kwd['tzinfo']
#         if tzinfo == 'float':
#             return dt
#         elif tzinfo == 'local':
#             return dt.astimezone()
#         else:
#             return timezone(tzinfo).localize(dt)
#     else:
#         return dt.astimezone()

def is_aware(dt):
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

def encode_datetime(obj):
    if not isinstance(obj, datetime):
        raise ValueError(f"{obj} is not a datetime instance")
    if is_aware(obj):
        return obj.astimezone(pytz.timezone('UTC')).strftime(AWARE_FMT)
    else:
        return obj.strftime(NAIVE_FMT)

def decode_datetime(s):
    if s[-1] not in 'AN' or len(s) != 14:
        # print(f"{s[-1] in 'AN'}, {len(s) == 14}")
        raise ValueError(f"{s} is not a datetime string")
    if s[-1] == 'A':
        return datetime.strptime(s, AWARE_FMT).astimezone(pytz.timezone('UTC')).astimezone(tz.tzlocal())
    else:
        return datetime.strptime(s, NAIVE_FMT).astimezone(tz.tzlocal())


def normalize_timedelta(delta):
    total_seconds = delta.total_seconds()
    sign = '-' if total_seconds < 0 else ''
    minutes, remainder = divmod(abs(int(total_seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    until = []
    if weeks:
        until.append(f"{weeks}w")
    if days:
        until.append(f"{days}d")
    if hours:
        until.append(f"{hours}h")
    if minutes:
        until.append(f"{minutes}m")
    if not until:
        until.append("0m")

    return sign + "".join(until)


# Test
td = timedelta(days=-1, hours=2, minutes=30)
normalized_td = normalize_timedelta(td)
print(f"neg '{td}' => {normalized_td}")

td = timedelta(days=1, hours=-2, minutes=-30)
normalized_td = normalize_timedelta(td)
print(f"pos '{td}' => {normalized_td}")


class Period:
    def __init__(self, datetime1, datetime2):
        # Ensure both inputs are datetime.datetime instances
        if not isinstance(datetime1, datetime) or not isinstance(datetime2, datetime):
            raise ValueError("Both inputs must be datetime instances")

        aware1 = is_aware(datetime1)
        aware2 = is_aware(datetime2)

        if aware1 != aware2:
            raise ValueError(f"start: {datetime1.tzinfo}, end: {datetime2.tzinfo}. Both datetimes must either be naive or both must be aware.")

        if aware1:
            self.start = datetime1.astimezone(timezone('UTC'))
            self.end = datetime2.astimezone(pytz.timezone('UTC'))
        else:
            self.start = datetime1.replace(tzinfo=None)
            self.end = datetime2.replace(tzinfo=None)

        self.diff = self.end - self.start

    def __repr__(self):
        return f"Period({encode_datetime(self.start)} -> {encode_datetime(self.end)}, {normalize_timedelta(self.diff)})"

# # Usage:
# period = Period(
#         parse('Fri 2:00p').replace(tzinfo=None),
#         parse('Sat 9:00a').replace(tzinfo=None)
#         )
# print(period)

# period = Period(
#         parse('Fri 2:00p', tzinfo='US/Eastern'),
#         parse('Sat 9:00a', tzinfo='US/Pacific')
#         )
# print(period)

# period = Period(
#         parse('Sat 9:00a', tzinfo='US/Pacific'),
#         parse('Fri 2:00p', tzinfo='US/Eastern')
#         )
# print(period)



class DateTimeSerializer(Serializer):
    """
    This class handles both aware and naive datetime objects.

    Encoding: If obj.tzinfo is 'None', it is interpreted as naive, serialized without conversion and an 'N' is appended. Otherwise it is interpreted as aware, converted to UTC and an 'A' is appended.
    Decoding: If the serialization ends with 'A', the datetime object is treated as 'UTC' and converted to localtime. Otherwise, the object is treated as 'Factory' and no conversion is performed.

    This serialization discards both seconds and microseconds but preserves hours and minutes.

    """

    OBJ_CLASS = datetime


    def encode(self, obj):
        """
        Serialize naive objects (Z == '') without conversion but with 'N' for 'Naive' appended. Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        >>> dts = DateTimeSerializer()
        >>> dts.encode(datetime(2018,7,25,10, 27).naive())
        '20180725T1027N'
        >>> dts.encode(datetime(2018,7,25,10, 27, tz='US/Eastern'))
        '20180725T1427A'
        """
        return encode_datetime(obj)
        # if is_aware(obj):
        #     return obj.astimezone(pytz.timezone('UTC')).strftime(AWARE_FMT)
        # else:
        #     return obj.strftime(NAIVE_FMT)

    def decode(self, s):
        """
        Return the serialization as a datetime object. If the serializaton ends with 'A',  first interpret as UTC aware and then return the corresponding aware datetime object in the local timezone. If the serialization ends with 'N', returning as an aware datetime object in the local timezone.
        >>> dts = DateTimeSerializer()
        >>> dts.decode('20180725T1027N')
        DateTime(2018, 7, 25, 10, 27, 0, tzinfo=Timezone('America/New_York'))
        >>> dts.decode('20180725T1427A')
        DateTime(2018, 7, 25, 10, 27, 0, tzinfo=Timezone('America/New_York'))
        """
        if s[-1] == 'A':
            return datetime.strptime(s, AWARE_FMT).astimezone(pytz.timezone('UTC')).astimezone(tz.tzlocal())
        else:
            return datetime.strptime(s, NAIVE_FMT).astimezone(tz.tzlocal())


class DateSerializer(Serializer):
    """
    This class handles datetime date objects. Encode as date string and decode as a midnight datetime without conversion in the local timezone.
    >>> ds = DateSerializer()
    >>> ds.encode(datetime(2018, 7, 25).date())
    '20180725'
    >>> ds.decode('20180725')
    Date(2018, 7, 25)
    """
    OBJ_CLASS = datetime.date

    def encode(self, obj):
        """
        Serialize the naive date object without conversion.
        """
        return obj.strftime(DATE_FMT)

    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        return datetime.strptime(s, DATE_FMT).date()


class PeriodSerializer(Serializer):
    """
    This class handles both aware and 'factory' datetime objects.

    Encoding: If obj.tzinfo.abbrev is '-00' (tz=Factory), it is interpreted as naive, serialized without conversion and an 'N' is appended. Otherwise it is interpreted as aware, converted to UTC and an 'A' is appended.
    Decoding: If the serialization ends with 'A', the datetime object is treated as 'UTC' and converted to localtime. Otherwise, the object is treated as 'Factory' and no conversion is performed.

    This serialization discards both seconds and microseconds but preserves hours and minutes.

    """

    OBJ_CLASS = Period

    # def __init__(self, obj):
    #     # Ensure both inputs are datetime.datetime instances
    #     self.obj = obj
    #     self.encoded = self.encode(obj)
    #     self.decoded = self.decode(self.encoded)
    #     self.diff = obj.diff

    def encode(self, obj):
        """
        Serialize naive objects (Z == '') without conversion but with 'N' for 'Naive' appended. Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        >>> ps = PeriodSerializer()
        >>> ps.encode(Period(datetime(2018,7,30,10,45).naive(), datetime(2018,7,25,10,27).naive()))
        '20180730T1045N -> 20180725T1027N'
        >>> ps.encode(Period(datetime(2018,7,30,10,45).astimezone(pytz.tzinfo('US/Eastern')), datetime(2018,7,25,10,27)astimezone(pytz('US/Pacific')))
        '20180730T1445A -> 20180725T1727A'
        """
        start_fmt = encode_datetime(obj.start)
        end_fmt = encode_datetime(obj.end)
        return f"{start_fmt} -> {end_fmt}"


    def decode(self, s):
        """
        Return the serialization as a period object. If the serializaton ends with 'A',  first converting to localtime and returning an aware datetime object in the local timezone. If the serialization ends with 'N', returning without conversion as an aware datetime object in the local timezone.
        >>> ps = PeriodSerializer()
        >>> ps.decode('20180730T1045N -> 20180725T1027N')
        <Period [2018-07-30T10:45:00-04:00 -> 2018-07-25T10:27:00-04:00]>
        >>> ps.decode('20180730T1445A -> 20180725T1727A')
        <Period [2018-07-30T10:45:00-04:00 -> 2018-07-25T13:27:00-04:00]>
        """

        start, end = [x.strip() for x in s.split('->')]
        start_enc = decode_datetime(start)
        end_enc = decode_datetime(end)
        return Period(start_enc, end_enc)

    def __repr__(self):
        return f"{self.obj}"



class DurationSerializer(Serializer):
    """
    This class handles timedelta (timedelta) objects.
    >>> dus = DurationSerializer()
    >>> dus.encode(timedelta(days=3, hours=5, minutes=15))
    '3d5h15m'
    >>> dus.decode('3d5h15m')
    Duration(days=3, hours=5, minutes=15)
    """
    OBJ_CLASS = timedelta

    def encode(self, obj):
        """
        Serialize the timedelta object as days.seconds.
        """
        return format_duration(obj)

    def decode(self, s):
        """
        Return the serialization as a timedelta object.
        """
        return parse_duration(s)[1]


class WeekdaySerializer(Serializer):
    """
    This class handles dateutil.rrule.weeday objects. Note in the following examples that unquoted weekdays, eg. MO(-3), are dateutil.rrule.weekday objects.
    >>> wds = WeekdaySerializer()
    >>> wds.encode(MO(-3))
    '-3MO'
    >>> wds.encode(SA(+3))
    '3SA'
    >>> wds.encode(WE)
    'WE'
    >>> wds.decode('-3MO')
    MO(-3)
    >>> wds.decode('3SA')
    SA(+3)
    >>> wds.decode('WE')
    WE
    """

    OBJ_CLASS = dateutil.rrule.weekday

    def encode(self, obj):
        """
        Serialize the weekday object.
        """
        s = WKDAYS_ENCODE[obj.__repr__()]
        if s.startswith('+'):
            # drop the leading + sign
            s = s[1:]
        # print('serializing', obj.__repr__(), type(obj), 'as', s)
        return s

    def decode(self, s):
        """
        Return the serialization as a weekday object.
        """
        # print('deseralizing', s, type(s))
        return eval('dateutil.rrule.{}'.format(WKDAYS_DECODE[s]))

########################################
###### Begin Mask ######################
########################################

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

# NOTE: The real secret is set in cfg.yaml
secret = "whatever"

class Mask():
    """
    Provide an encoded value with an "isinstance" test for serializaton
    >>> mask = Mask('my dirty secret')
    >>> isinstance(mask, Mask)
    True
    """

    def __init__(self, message=""):
        self.encoded = encode(secret, message)


    def __repr__(self):
        return decode(secret, self.encoded)



class MaskSerializer(Serializer):
    """
    """
    OBJ_CLASS = Mask

    def encode(self, obj):
        """
        Encode the string using base64
        """
        return obj.encoded

    def decode(self, s):
        """
        Decode the base
        """
        return Mask(decode(secret, s))

########################################
###### End Mask ########################
########################################

def initialize_tinydb(dbfile):
    """
    """
    serialization = SerializationMiddleware()
    serialization.register_serializer(DateTimeSerializer(), 'T') # Time
    serialization.register_serializer(DateSerializer(), 'D')     # Date
    serialization.register_serializer(PeriodSerializer(), 'P')   # Period
    serialization.register_serializer(DurationSerializer(), 'I') # Interval
    serialization.register_serializer(WeekdaySerializer(), 'W')  # Wkday
    serialization.register_serializer(MaskSerializer(), 'M')             # Mask
    if tinydb_version >= '4.0.0':
        db = TinyDB(dbfile, storage=serialization,
                indent=1, ensure_ascii=False)
        db.default_table_name='items'
    else:
        db = TinyDB(dbfile, storage=serialization,
                default_table='items',
                indent=1, ensure_ascii=False)
    return db

def format_duration(obj):
    """
    For etm, microseconds will be zero and seconds will always be an integer
    multiple of 60. Thus timedeltas can always be expressed using only weeks, days,
    hours and minutes.
    """
    if not isinstance(obj, datetime.timedelta):
        raise ValueError(f"{obj} is not a timedelta instance")
    until =[]
    weeks = obj.days // 7
    days = obj.days % 7
    hours = obj.seconds // (60*60)
    minutes = (obj.seconds // 60) % 60
    if weeks:
        until.append(f"{weeks}w")
    if days:
        until.append(f"{days}d")
    if hours:
        until.append(f"{hours}h")
    if minutes:
        until.append(f"{minutes}m")
    if not until:
        until.append("0m")
    return "".join(until)

def format_duration_list(obj_lst):
    try:
        return ", ".join([format_duration(x) for x in obj_lst])
    except Exception as e:
        print('format_duration_list', e)
        print(obj_lst)


period_regex = re.compile(r'(([+-]?)(\d+)([wdhms]))+?')
threeday_regex = re.compile(r'(MON|TUE|WED|THU|FRI|SAT|SUN)', re.IGNORECASE)
anniversary_regex = re.compile(r'!(\d{4})!')

period_hsh = dict(
    z=timedelta(seconds=0),
    s=timedelta(seconds=1),
    m=timedelta(minutes=1),
    h=timedelta(hours=1),
    d=timedelta(days=1),
    w=timedelta(weeks=1),
        )

def parse_duration(s):
    """\
    Take a period string and return a corresponding timedelta.
    Examples:
        parse_duration('-2w3d4h5m')= Duration(weeks=-2,days=3,hours=4,minutes=5)
        parse_duration('1h30m') = Duration(hours=1, minutes=30)
        parse_duration('-10m') = Duration(minutes=10)
    where:
        w: weeks
        d: days
        h: hours
        m: minutes

    >>> 3*60*60+5*60
    11100
    >>> parse_duration("2d-3h5m")[1]
    Duration(days=1, hours=21, minutes=5)
    >>> datetime(2015, 10, 15, 9, 0, tz='local') + parse_duration("-25m")[1]
    DateTime(2015, 10, 15, 8, 35, 0, tzinfo=Timezone('America/New_York'))
    >>> datetime(2015, 10, 15, 9, 0) + parse_duration("1d")[1]
    DateTime(2015, 10, 16, 9, 0, 0, tzinfo=Timezone('UTC'))
    >>> datetime(2015, 10, 15, 9, 0) + parse_duration("1w-2d+3h")[1]
    DateTime(2015, 10, 20, 12, 0, 0, tzinfo=Timezone('UTC'))
    """
    td = period_hsh['z']

    m = period_regex.findall(s)
    if not m:
        return False, "Invalid period '{0}'".format(s)
    for g in m:
        num = -int(g[2]) if g[1] == '-' else int(g[2])
        td += num * period_hsh[g[3]]
    return True, td

