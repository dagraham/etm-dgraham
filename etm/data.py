#!/usr/bin/env python3

from tinydb import TinyDB, Query
from tinydb import __version__ as tinydb_version
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware
import base64  # for do_mask
import pendulum
import dateutil
import dateutil.rrule
from dateutil.rrule import *
import re

##########################
### begin TinyDB setup ###
##########################

TinyDB.DEFAULT_TABLE = 'items'

class PendulumDateTimeSerializer(Serializer):
    """
    This class handles both aware and 'factory' pendulum objects.

    Encoding: If obj.tzinfo.abbrev is '-00' (tz=Factory), it is interpreted as naive, serialized without conversion and an 'N' is appended. Otherwise it is interpreted as aware, converted to UTC and an 'A' is appended.
    Decoding: If the serialization ends with 'A', the pendulum object is treated as 'UTC' and converted to localtime. Otherwise, the object is treated as 'Factory' and no conversion is performed.

    This serialization discards both seconds and microseconds but preserves hours and minutes.

    """

    OBJ_CLASS = pendulum.DateTime

    def encode(self, obj):
        """
        Serialize naive objects (Z == '') without conversion but with 'N' for 'Naive' appended. Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        >>> dts = PendulumDateTimeSerializer()
        >>> dts.encode(pendulum.datetime(2018,7,25,10, 27).naive())
        '20180725T1027N'
        >>> dts.encode(pendulum.datetime(2018,7,25,10, 27, tz='US/Eastern'))
        '20180725T1427A'
        """
        if obj.format('Z') == '':
            return obj.format('YYYYMMDDTHHmm[N]')
        else:
            return obj.in_tz('UTC').format('YYYYMMDDTHHmm[A]')

    def decode(self, s):
        """
        Return the serialization as a datetime object. If the serializaton ends with 'A',  first converting to localtime and returning an aware datetime object in the local timezone. If the serialization ends with 'N', returning without conversion as an aware datetime object in the local timezone.
        >>> dts = PendulumDateTimeSerializer()
        >>> dts.decode('20180725T1027N')
        DateTime(2018, 7, 25, 10, 27, 0, tzinfo=Timezone('America/New_York'))
        >>> dts.decode('20180725T1427A')
        DateTime(2018, 7, 25, 10, 27, 0, tzinfo=Timezone('America/New_York'))
        """
        if s[-1] == 'A':
            return pendulum.from_format(s[:-1], 'YYYYMMDDTHHmm', 'UTC').in_timezone('local')
        else:
            return pendulum.from_format(s[:-1], 'YYYYMMDDTHHmm').naive().in_timezone('local')


class PendulumDateSerializer(Serializer):
    """
    This class handles pendulum date objects. Encode as date string and decode as a midnight datetime without conversion in the local timezone.
    >>> ds = PendulumDateSerializer()
    >>> ds.encode(pendulum.date(2018, 7, 25))
    '20180725'
    >>> ds.decode('20180725')
    Date(2018, 7, 25)
    """
    OBJ_CLASS = pendulum.Date

    def encode(self, obj):
        """
        Serialize the naive date object without conversion.
        """
        return obj.format('YYYYMMDD')

    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        # return pendulum.from_format(s, 'YYYYMMDD').naive().in_timezone('local')
        return pendulum.from_format(s, 'YYYYMMDD').date()


class PendulumDurationSerializer(Serializer):
    """
    This class handles pendulum.duration (timedelta) objects.
    >>> dus = PendulumDurationSerializer()
    >>> dus.encode(pendulum.duration(days=3, hours=5, minutes=15))
    '3d5h15m'
    >>> dus.decode('3d5h15m')
    Duration(days=3, hours=5, minutes=15)
    """
    OBJ_CLASS = pendulum.Duration

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

class PendulumWeekdaySerializer(Serializer):
    """
    This class handles dateutil.rrule.weeday objects. Note in the following examples that unquoted weekdays, eg. MO(-3), are dateutil.rrule.weekday objects.
    >>> wds = PendulumWeekdaySerializer()
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
    This class handles pendulum.duration (timedelta) objects.
    >>> mask = MaskSerializer()
    >>> mask.encode(Mask("when to the sessions")) # doctest: +NORMALIZE_WHITESPACE
    'w5zDnMOSwo7CicOnwo_Cl8Ojw5bDicKFw6XDi8Oow5_CisOUw6LDoA=='
    >>> mask.decode('    w5zDnMOSwo7CicOnwo_Cl8Ojw5bDicKFw6XDi8Oow5_CisOUw6LDoA==') # doctest: +NORMALIZE_WHITESPACE
    when to the sessions
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
    serialization.register_serializer(PendulumDateTimeSerializer(), 'T') # Time
    serialization.register_serializer(PendulumDateSerializer(), 'D')     # Date
    serialization.register_serializer(PendulumDurationSerializer(), 'I') # Interval
    serialization.register_serializer(PendulumWeekdaySerializer(), 'W')  # Wkday
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
    >>> td = pendulum.duration(weeks=1, days=2, hours=3, minutes=27)
    >>> format_duration(td)
    '1w2d3h27m'
    """
    if not isinstance(obj, pendulum.Duration):
        return None
    try:
        until =[]
        if obj.weeks:
            until.append(f"{obj.weeks}w")
        if obj.remaining_days:
            until.append(f"{obj.remaining_days}d")
        if obj.hours:
            until.append(f"{obj.hours}h")
        if obj.minutes:
            until.append(f"{obj.minutes}m")
        if not until:
            until.append("0m")
        ret = "".join(until)
        return "".join(until)
    except Exception as e:
        print('format_duration', e)
        print(obj)
        return None

def format_duration_list(obj_lst):
    try:
        return ", ".join([format_duration(x) for x in obj_lst])
    except Exception as e:
        print('format_duration_list', e)
        print(obj_lst)


period_regex = re.compile(r'(([+-]?)(\d+)([wdhm]))+?')
threeday_regex = re.compile(r'(MON|TUE|WED|THU|FRI|SAT|SUN)', re.IGNORECASE)
anniversary_regex = re.compile(r'!(\d{4})!')

period_hsh = dict(
    z=pendulum.duration(seconds=0),
    m=pendulum.duration(minutes=1),
    h=pendulum.duration(hours=1),
    d=pendulum.duration(days=1),
    w=pendulum.duration(weeks=1),
        )

def parse_duration(s):
    """\
    Take a period string and return a corresponding pendulum.duration.
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
    >>> pendulum.datetime(2015, 10, 15, 9, 0, tz='local') + parse_duration("-25m")[1]
    DateTime(2015, 10, 15, 8, 35, 0, tzinfo=Timezone('America/New_York'))
    >>> pendulum.datetime(2015, 10, 15, 9, 0) + parse_duration("1d")[1]
    DateTime(2015, 10, 16, 9, 0, 0, tzinfo=Timezone('UTC'))
    >>> pendulum.datetime(2015, 10, 15, 9, 0) + parse_duration("1w-2d+3h")[1]
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

WKDAYS_DECODE = {"{0}{1}".format(n, d): "{0}({1})".format(d, n) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']}
WKDAYS_ENCODE = {"{0}({1})".format(d, n): "{0}{1}".format(n, d) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4']}
for wkd in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
    WKDAYS_ENCODE[wkd] = wkd

