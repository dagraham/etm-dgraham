#!/usr/bin/env python3

import os
import json
from tinydb import where 
from tinydb import JSONStorage, TinyDB, Storage, Query 
from tinydb.table import Table, Document 
from tinydb.middlewares import CachingMiddleware 
from contextlib import contextmanager
from typing import Dict, Any, Optional, Callable, Mapping
from prompt_toolkit.lexers import PygmentsLexer 

from tinydb import __version__ as tinydb_version 
from tinydb_serialization import Serializer 
from tinydb_serialization import SerializationMiddleware 
import base64  # for do_mask
import asyncio

from datetime import datetime, date, timedelta

import dateutil 
from dateutil.rrule import rrule
from dateutil.tz import gettz

import logging
logger = logging.getLogger('etmmv')

from dateutil.rrule import * 
import re
from etm.common import ( 
    WKDAYS_DECODE,
    WKDAYS_ENCODE,
    AWARE_FMT,
    NAIVE_FMT,
    DATE_FMT,
    TDBLexer,
    dataview,
    DBARCH,
    DBITEM,
    wrap,
    nowrap,
    openWithDefault,
    Period,
    is_aware,
    encode_datetime,
    decode_datetime,
    data_changed,
    write_back,
    update_db,
    db_replace,
)
from etm.model import item_details 
# from etm.common import Period, is_aware, encode_datetime, decode_datetime

##########################
### begin TinyDB setup ###
##########################

# def db_replace(new):
#     """
#     Used with update to replace the original doc with new.
#     """

#     def transform(doc):
#         # update doc to include key/values from new
#         doc.update(new)
#         # remove any key/values from doc that are not in new
#         for k in list(doc.keys()):
#             if k not in new:
#                 del doc[k]

#     return transform


# def update_db(db, doc_id, hsh={}):
#     old = db.get(doc_id=doc_id)
#     if not old:
#         logger.error(
#             f'Could not get document corresponding to doc_id {doc_id}'
#         )
#         return
#     if old == hsh:
#         return
#     hsh['modified'] = datetime.now()
#     logger.debug(f"starting db.update")
#     try:
#         db.update(db_replace(hsh), doc_ids=[doc_id])
#     except Exception as e:
#         logger.error(
#             f'Error updating document corresponding to doc_id {doc_id}\nhsh {hsh}\nexception: {repr(e)}'
#         )


# def write_back(db, docs):
#     logger.debug(f"starting write_back")
#     for doc in docs:
#         try:
#             doc_id = doc.doc_id
#             update_db(db, doc_id, doc)
#         except Exception as e:
#             logger.error(f'write_back exception: {e}')


local_tz = gettz()
utc_tz = gettz('UTC')

def insert_db(db, hsh={}):
    """
    Assume hsh has been vetted.
    """
    if not hsh:

        return
    hsh['created'] = datetime.now()
    try:
        db.insert(hsh)
    except Exception as e:
        logger.error(f'Error updating database:\nhsh {hsh}\ne {repr(e)}')


class ETMQuery(object):
    def __init__(self):
        self.filters = {
            'begins': self.begins,
            'includes': self.includes,
            'in': self.includes,
            'equals': self.equals,
            'more': self.more,
            'less': self.less,
            'exists': self.exists,
            'any': self.in_any,
            'all': self.in_all,
            'one': self.one_of,
            'info': self.info,
            'dt': self.dt,
        }

        self.op = {
            '=': self.maybe_equal,
            '>': self.maybe_later,
            '<': self.maybe_earlier,
        }

        self.update = {
            'replace': self.replace,  # a, rgx, rep
            'remove': self.remove,  #
            'archive': self.archive,  #
            'delete': self.delete,  # a
            'set': self.set,  # a, b
            'provide': self.provide,  # a, b
            'attach': self.attach,  # a, b
            'detach': self.detach,  # a, b
        }

        self.changed = False

        self.lexer = PygmentsLexer(TDBLexer)
        self.Item = Query()

        self.allowed_commands = ', '.join([x for x in self.filters])

    def replace(self, a, rgx, rep, items):
        """
        Replace matches for rgx with rep in item['a']. If item['a']
        is a list, do this for each element in item['a']
        """
        changed = []
        rep = re.sub(r'\\s', ' ', rep)
        for item in items:
            if a in item:
                if isinstance(item[a], list):
                    res = []
                    # apply to each component
                    for item in item[a]:
                        res.append(re.sub(rgx, rep, item, flags=re.IGNORECASE))
                else:
                    res = re.sub(rgx, rep, item[a], flags=re.IGNORECASE)
                if res != item[a]:
                    item[a] = res
                    item['modified'] = datetime.now().astimezone()
                    changed.append(item)
        if changed:
            write_back(dataview.db, changed)
        return changed

    def remove(self, items):
        """
        Remove items.
        """
        rem_ids = [item.doc_id for item in items]
        # warn
        if rem_ids:
            dataview.db.remove(doc_ids=rem_ids)
            self.changed = True

    def archive(self, items):
        """
        When querying the items table, move items to the archive table and vice versa.
        """
        rem_ids = [item.doc_id for item in items]

        try:
            if dataview.query_mode == 'items table':
                # move to archive
                DBARCH.insert_multiple(items)
                DBITEM.remove(doc_ids=rem_ids)
            else:
                # back to items
                DBITEM.insert_multiple(items)
                DBARCH.remove(doc_ids=rem_ids)
        except Exception as e:
            logger.error(
                f'move from {dataview.query_mode} failed for items: {items}; rem_ids: {rem_ids}; exception: {e}'
            )
            return False
        else:
            self.changed = True

    def delete(self, a, items):
        """
        For items having key 'a', remove the key and value from the item.
        """
        changed = []
        for item in items:
            if a in item:
                del item[a]
                item['modified'] = datetime.now().astimezone()
                changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True
        return changed

    def set(self, a, b, items):
        """
        Set the value of item[a] = b for items
        """
        changed = []
        b = re.sub(r'\\\s', ' ', b)
        for item in items:
            item[a] = b
            item['modified'] = datetime.now().astimezone()
            changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def provide(self, a, b, items):
        """
        Provide item['a'] = b for items without an exising entry for 'a'.
        """
        changed = []
        b = re.sub(r'\\\s', ' ', b)
        for item in items:
            item.setdefault(a, b)
            item['modified'] = datetime.now().astimezone()
            changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def attach(self, a, b, items):
        """
        Attach 'b' into the item['a'] list if 'b' is not in the list.
        """
        changed = []
        b = re.sub(r'\\\s', ' ', b)
        for item in items:
            if a not in item:
                item.setdefault(a, []).append(b)
                item['modified'] = datetime.now().astimezone()
                changed.append(item)
            elif isinstance(item[a], list) and b not in item[a]:
                item.setdefault(a, []).append(b)
                item['modified'] = datetime.now().astimezone()
                changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def detach(self, a, b, items):
        """
        Detatch 'b' from the item['a'] list if it belongs to the list.
        """
        changed = []
        b = re.sub(r'\\\s', ' ', b)
        for item in items:
            if a in item and isinstance(item[a], list) and b in item[a]:
                item[a].remove(b)
                item['modified'] = datetime.now().astimezone()
                changed.append(item)
        if changed:
            write_back(dataview.db, changed)
            self.changed = True

    def is_datetime(self, val):
        return isinstance(val, datetime)

    def is_date(self, val):
        return isinstance(val, date) and not isinstance(val, datetime)

    def maybe_equal(self, val, args):
        """
        args = year-month-...-minute
        """
        args = args.split('-')
        # args = list(args)
        if not isinstance(val, date):
            # neither a date or a datetime
            return False
        if args and val.year != int(args.pop(0)):
            return False
        if args and val.month != int(args.pop(0)):
            return False
        if args and val.day != int(args.pop(0)):
            return False
        if isinstance(val, datetime):
            # val has hours and minutes
            if args and val.hour != int(args.pop(0)):
                return False
            if args and val.minute != int(args.pop(0)):
                return False
        return True

    def maybe_later(self, val, args):
        """
        args = year-month-...-minute
        """
        args = args.split('-')
        # args = list(args)
        if not isinstance(val, date):
            # neither a date or a datetime
            return False
        if args and not val.year >= int(args.pop(0)):
            return False
        if args and not val.month >= int(args.pop(0)):
            return False
        if args and not val.day >= int(args.pop(0)):
            return False
        if isinstance(val, datetime):
            # val has hours and minutes
            if args and not val.hour >= int(args.pop(0)):
                return False
            if args and not val.minute >= int(args.pop(0)):
                return False
        return True

    def maybe_earlier(self, val, args):
        """
        args = year-month-...-minute
        """
        args = args.split('-')
        # args = list(args)
        if not isinstance(val, date):
            # neither a date or a datetime
            return False
        if args and not val.year <= int(args.pop(0)):
            return False
        if args and not val.month <= int(args.pop(0)):
            return False
        if args and not val.day <= int(args.pop(0)):
            return False
        if isinstance(val, datetime):
            # val has hours and minutes
            if args and not val.hour <= int(args.pop(0)):
                return False
            if args and not val.minute <= int(args.pop(0)):
                return False
        return True

    def begins(self, a, b):
        # the value of field 'a' begins with the case-insensitive regex 'b'
        return where(a).matches(b, flags=re.IGNORECASE)

    def includes(self, a, b):
        # the value of one of the fields in 'a' includes the case-insensitive regex 'b'
        if not isinstance(a, list):
            a = [a]
        results = [where(field).search(b, flags=re.IGNORECASE) for field in a]
        test = results.pop(0)
        for res in results:
            test = test | res
        return test

    def equals(self, a, b):
        # the value of field 'a' equals 'b'
        try:
            b = int(b)
        except:
            pass
        return where(a) == b

    def more(self, a, b):
        # the value of field 'a' >= 'b'
        try:
            b = int(b)
        except:
            pass
        return where(a) >= b

    def less(self, a, b):
        # the value of field 'a' equals 'b'
        try:
            b = int(b)
        except:
            pass
        return where(a) <= b

    def exists(self, a):
        # field 'a' exists
        return where(a).exists()

    def in_any(self, a, b):
        """
        the value of field 'a' is a list of values and at least
        one of them is an element from 'b'. Here 'b' should be a list with
        2 or more elements. With only a single element, there is no
        difference between any and all.

        With egs, "any,  blue, green" returns all three items.
        """

        if not isinstance(b, list):
            b = [b]
        return where(a).any(b)

    def in_all(self, a, b):
        """
        the value of field 'a' is a list of values and among the list
        are all the elements in 'b'. Here 'b' should be a list with
        2 or more elements. With only a single element, there is no
        difference between any and all.

        With egs, "all, blue, green" returns just "blue and green"
        """
        if not isinstance(b, list):
            b = [b]
        return where(a).all(b)

    def one_of(self, a, b):
        """
        the value of field 'a' is one of the elements in 'b'.

        With egs, "one, summary, blue, green" returns both "green" and "blue"
        """
        if not isinstance(b, list):
            b = [b]
        return where(a).one_of(b)

    def info(self, a):
        # field 'a' exists
        item = dataview.db.get(doc_id=int(a))
        return item if item else f'doc_id {a} not found'

    def dt(self, a, b):
        if b[0] == '?':
            if b[1] == 'time':
                return self.Item[a].test(self.is_datetime)
            elif b[1] == 'date':
                return self.Item[a].test(self.is_date)

        return self.Item[a].test(self.op[b[0]], b[1])

    def process_query(self, query):
        """ """
        dataview.last_query = []
        [fltr, *updt] = [x.strip() for x in query.split(' | ')]
        if len(updt) == 1:
            # get a list with the update command and arguments
            updt = [x.strip() for x in updt[0].split(' ')]
        else:
            updt = []

        parts = [x.split() for x in re.split(r' (and|or) ', fltr)]

        cmnds = []
        for part in parts:
            part = [x.strip() for x in part if x.strip()]
            negation = part[0].startswith('~')
            if part[0] not in ['and', 'or']:
                # we have a command
                if negation:
                    # drop the ~
                    part[0] = part[0][1:]
                if self.filters.get(part[0], None) is None:
                    return (
                        False,
                        wrap(
                            f"""bad command: '{part[0]}'. Only commands in {self.allowed_commands} are allowed."""
                        ),
                        updt,
                    )

            if len(part) > 3:
                if part[0] in ['in', 'includes']:
                    if negation:
                        cmnds.append(
                            ~self.filters[part[0]](
                                [x.strip() for x in part[1:-1]], part[-1]
                            )
                        )
                    else:
                        cmnds.append(
                            self.filters[part[0]](
                                [x.strip() for x in part[1:-1]], part[-1]
                            )
                        )
                else:
                    if negation:
                        cmnds.append(
                            ~self.filters[part[0]](
                                part[1], [x.strip() for x in part[2:]]
                            )
                        )
                    else:
                        cmnds.append(
                            self.filters[part[0]](
                                part[1], [x.strip() for x in part[2:]]
                            )
                        )
            elif len(part) > 2:
                if negation:
                    cmnds.append(~self.filters[part[0]](part[1], part[2]))
                else:
                    cmnds.append(self.filters[part[0]](part[1], part[2]))
            elif len(part) > 1:
                if negation:
                    cmnds.append(~self.filters[part[0]](part[1]))
                else:
                    cmnds.append(self.filters[part[0]](part[1]))
            else:
                cmnds.append(part[0])

        test = cmnds[0]
        for i in range(1, len(cmnds)):
            if i % 2 and cmnds[i] in ['and', 'or']:
                andor = cmnds[i]
                continue
            test = test | cmnds[i] if andor == 'or' else test & cmnds[i]
        return True, test, updt

    def do_query(self, query):
        """ """
        if query in ['?', 'help']:
            query_help = 'https://dagraham.github.io/etm-dgraham/#query-view'
            openWithDefault(query_help)
            return False, 'opened query help using default browser'
        try:
            ok, res, updt = self.process_query(query)
            if not ok or isinstance(res, str):
                return False, res

            if isinstance(res, Document):
                return False, item_details(res)
            else:
                items = dataview.db.search(res)
                if updt:
                    self.update[updt[0]](*updt[1:], items)
                    if self.changed:
                        loop = asyncio.get_event_loop()
                        loop.call_later(0, data_changed, loop)
                        self.changed = False
                return True, items
        except Exception as e:
            return False, f"exception processing '{query}':\n{e}"


############# end query ################################


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
        >>> dts.encode(datetime(2018,7,25,10,27).naive())
        '20180725T1027N'
        >>> dts.encode(datetime(2018,7,25,10,27, tz='US/Eastern'))
        '20180725T1427A'
        """
        return encode_datetime(obj)
        if is_aware(obj):
            return obj.astimezone(utc_tz).strftime(AWARE_FMT)
        else:
            return obj.strftime(NAIVE_FMT)

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
            return (
                datetime.strptime(s, AWARE_FMT)
                .replace(tzinfo=utc_tz)
                .astimezone(local_tz)
            )
        else:
            return datetime.strptime(s, NAIVE_FMT).replace(tzinfo=local_tz)


class DateSerializer(Serializer):
    """
    This class handles datetime date objects. Encode as date string and decode as a midnight datetime without conversion in the local timezone.
    >>> ds = DateSerializer()
    >>> ds.encode(datetime(2018, 7, 25).date())
    '20180725'
    >>> ds.decode('20180725')
    Date(2018, 7, 25)
    """

    OBJ_CLASS = date

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

    def encode(self, obj):
        """
        Serialize naive objects (Z == '') without conversion but with 'N' for 'Naive' appended.
        Convert aware datetime objects to UTC and then serialize them with 'A' for 'Aware' appended.
        >>> ps = PeriodSerializer()
        >>> ps.encode(Period(datetime(2018,7,30,10,45).naive(), datetime(2018,7,25,10,27).naive()))
        '20180730T1045N -> 20180725T1027N'
        >>> ps.encode(Period(datetime(2018,7,30,10,45).astimezone(pytz.tzinfo('US/Eastern')), datetime(2018,7,25,10,27)astimezone(pytz('US/Pacific')))
        '20180730T1445A -> 20180725T1727A'
        """
        start_fmt = encode_datetime(obj.start)
        end_fmt = encode_datetime(obj.end)
        return f'{start_fmt} -> {end_fmt}'

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
        return f'{self.obj}'


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
    This class handles dateutil.rrule.weeday objects. Note in the following examples that
    unquoted weekdays, eg. MO(-3), are dateutil.rrule.weekday objects.
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
        return format_rrwkday(obj)

    def decode(self, s):
        """
        Return the serialization as a weekday object.
        """
        return parse_rrwkday(s)


def format_rrwkday(obj):
    s = WKDAYS_ENCODE.get(obj.__repr__(), '').lstrip('+')
    if s is None:
        raise ValueError(f'{obj} is not a dateutil rrule weekday instance')
    return s


def parse_rrwkday(s):
    s = WKDAYS_DECODE.get(s, '')
    if not s:
        raise ValueError(f'{s} is not a valid rrule weekday expression')
    obj = eval(f'dateutil.rrule.{s}')
    return obj


########################################
###### Begin Mask ######################
########################################


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode(''.join(enc).encode()).decode()


def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return ''.join(dec)


# NOTE: The real secret is set in cfg.yaml
secret = 'whatever'


class Mask:
    """
    Provide an encoded value with an "isinstance" test for serializaton
    >>> mask = Mask('my dirty secret')
    >>> isinstance(mask, Mask)
    True
    """

    def __init__(self, message=''):
        self.encoded = encode(secret, message)

    def __repr__(self):
        return decode(secret, self.encoded)


class MaskSerializer(Serializer):
    """ """

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
    """ """
    serialization = SerializationMiddleware()
    serialization.register_serializer(DateTimeSerializer(), 'T')   # Time
    serialization.register_serializer(DateSerializer(), 'D')     # Date
    serialization.register_serializer(PeriodSerializer(), 'P')   # Period
    serialization.register_serializer(DurationSerializer(), 'I')   # Interval
    serialization.register_serializer(WeekdaySerializer(), 'W')  # Wkday
    serialization.register_serializer(MaskSerializer(), 'M')    # Mask

    db = TinyDB(dbfile, storage=serialization, indent=1, ensure_ascii=False)
    logger.debug(f'db._storage: {db.__dict__}')

    db.default_table_name = 'items'

    # db.insert({'itemtype': '!', 'summary': 'inserted by data.py'})

    return db


def format_duration(obj):
    """
    For etm, microseconds will be zero and seconds will always be an integer
    multiple of 60. Thus timedeltas can always be expressed using only weeks, days,
    hours and minutes.
    """
    if not isinstance(obj, timedelta):
        raise ValueError(f'{obj} is not a timedelta instance')
    until = []
    weeks = obj.days // 7
    days = obj.days % 7
    hours = obj.seconds // (60 * 60)
    minutes = (obj.seconds // 60) % 60
    seconds = obj.seconds % 60
    if weeks:
        until.append(f'{weeks}w')
    if days:
        until.append(f'{days}d')
    if hours:
        until.append(f'{hours}h')
    if minutes:
        until.append(f'{minutes}m')
    if seconds:
        until.append(f'{seconds}s')
    if not until:
        until.append('0m')
    return ''.join(until)


def format_duration_list(obj_lst):
    try:
        return ', '.join([format_duration(x) for x in obj_lst])
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
