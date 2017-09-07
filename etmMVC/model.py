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
    OBJ_CLASS = datetime  # This class handles both aware and naive datetime objects 

    def encode(self, obj):
        """
        Convert aware datetime objects to UTC and then serialize them.
        Serialize naive datetimes objects without conversion. 
        """
        if obj.tzinfo is None:
            return obj.strftime('%Y%m%dT%H%M')
        else:
            return obj.astimezone(tzutc()).strftime('%Y%m%dT%H%M')

    def decode(self, s):
        """
        Return the serialization as a datetime object.
        """
        return datetime.strptime(s, '%Y%m%dT%H%M')

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
    db.insert({'naivedatetime': datetime(2017, 9, 7, 12, 0, 0)})
    db.insert({'awaredatetime': datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Eastern'))})
    db.insert({'date': date(2017, 9, 7)})
    db.insert({'null': Null})
    for item in db:
        print(item.eid, item)
