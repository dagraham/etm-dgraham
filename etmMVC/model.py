#!/usr/bin/env python3

from datetime import datetime
from tinydb_serialization import Serializer
from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware

class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')

if __name__ == '__main__':

    serialization = SerializationMiddleware()
    serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

    db = TinyDB('db.json', storage=serialization)
    db.insert({'date': datetime(2000, 1, 1, 12, 0, 0)})
    db.all() 
