#!/usr/bin/env python3

from datetime import datetime, date
import arrow
from tinydb_serialization import Serializer
from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from tinydb_smartcache import SmartCacheTable

from dateutil.parser import parse
from dateutil.tz import (tzlocal, gettz, tzutc)

parse_default = datetime.now().replace(hour=0, minute=1, second=0, 
microsecond=0)

def etm_parse(s):
    res = parse(s, default=parse_default)
    if (res.hour, res.minute, res.second, res.microsecond) == (0, 1, 0, 0):
        return res.date()
    else:
        return res.replace(second=0, microsecond=0)


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
        Return the serialization as a datetime object first converting to localtime if the serializaton ends with 'A'. Serializations that end with 'N' are naive or floating datetimes and are interpreted as already representing localtimes. 
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

if __name__ == '__main__':

    serialization = SerializationMiddleware()
    serialization.register_serializer(DateTimeSerializer(), 'TinyDateTime')
    serialization.register_serializer(DateSerializer(), 'TinyDate')

    db = TinyDB('db.json', storage=serialization)
    db.purge()
    db.insert({'dt': datetime(2017, 9, 7, 12, 0, 0)})
    db.insert({'dt': datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Eastern')) })
    db.insert({'dt': datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Pacific'))})
    db.insert({'dt': date(2017, 9, 7)})
    for item in db:
        print(item.eid, item)

    print(etm_parse('fri 2p'))
    print(etm_parse('fri 12a'))
    print(etm_parse('fri'))
