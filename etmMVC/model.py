#!/usr/bin/env python3

from datetime import datetime, date
from tinydb_serialization import Serializer
from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware

from dateutil.parser import parse
from dateutil.tz import (tzlocal, gettz, tzutc)


class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        if obj.tzinfo is None:
            return obj.strftime('%Y%m%dT%H%M')
        else:
            return obj.strftime('%Y%m%dT%H%M')


    def decode(self, s):
        return datetime.strptime(s, '%Y%m%dT%H%M')

class DateSerializer(Serializer):
    OBJ_CLASS = date  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime('%Y%m%d')

    def decode(self, s):
        return datetime.strptime(s, '%Y%m%d')

if __name__ == '__main__':

    serialization = SerializationMiddleware()
    serialization.register_serializer(DateTimeSerializer(), 'TinyDateTime')
    serialization.register_serializer(DateSerializer(), 'TinyDate')

    db = TinyDB('db.json', storage=serialization)
    db.insert({'naivedatetime': datetime(2017, 9, 7, 12, 0, 0)})
    db.insert({'awaredatetime': datetime(2017, 9, 7, 12, 0, 0, tzinfo=gettz('US/Eastern'))})
    db.insert({'date': date(2017, 9, 7)})
    db.all() 
