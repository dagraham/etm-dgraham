import sqlite3
from sqlite3 import Error
from pendulum import Pendulum
from sqlite3 import register_adapter
register_adapter(Pendulum, lambda val: val.isoformat(' '))

from datetime import date, datetime
from model import timestamp_from_eid
import os

tables = dict(
    items = """ CREATE TABLE
        items ( 
            item_id integer PRIMARY KEY,
            item_type text NOT NULL,
            summary text NOT NULL,
            calendar text NOT NULL,
            item_index,
            created_dt TIMESTAMP NOT NULL,
            modified_dt TIMESTAMP,
            FOREIGN KEY (item_index) REFERENCES indices (item_index)
        ); """,
    indices = """ CREATE TABLE 
        indices (
            index_id integer PRIMARY KEY,
            item_index text UNIQUE
        ); """,
    moments = """ CREATE TABLE 
        moments ( 
            moment_id integer PRIMARY KEY,
            moment_dt TIMESTAMP NOT NULL,
            moment_type TEXT NOT NULL,  -- in s)tart, f)inish, b)egin
            extent TEXT,
            item_id,
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        ); """,
    alerts = """ CREATE TABLE  
        alerts (
            alerts_id integer PRIMARY KEY,
            alerts_dt TIMESTAMP NOT NULL,
            command text NOT NULL,
            item_id,
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        ); """,
    tags = """ CREATE TABLE 
        tags (
            tag_id integer PRIMARY KEY,
            tag_name text NOT NULL
        ); """,
    item_tag = """ CREATE TABLE
        item_tag (
            item_id,
            tag_id,
            FOREIGN KEY (item_id) REFERENCES items (item_id),
            FOREIGN KEY (tag_id) REFERENCES tags (tag_id)
        ); """,
    )


class Table(object):

    def __init__(self, db_file=':memory:', overwrite=True):
        self.db_file = db_file
        self.overwrite = overwrite
        self.lastrowid =  None
        self.conn = self.create_connection()
        self.sqlite3_version = sqlite3.version
        self.sqlite_version = sqlite3.sqlite_version
        if self.conn is not None:
            with self.conn:
                c = self.conn.cursor()
                for table in tables:
                    try:
                        c.execute(tables[table])
                    except Error as e:
                        print(e)
                        print(tables[table])
                self.conn.commit()

    def create_connection(self):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        if (self.overwrite 
                and self.db_file != ':memory:' 
                and os.path.isfile(self.db_file)):
            os.remove(self.db_file) 
        try:
            conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
            return conn
        except Error as e:
            print(e)
        return None


    def sqlite_insert(self, table, row):
        keys = row.keys()
        cols = ', '.join('"{}"'.format(col) for col in keys)
        vals = ', '.join(':{}'.format(row[col]) for col in keys)
        sql = f'INSERT INTO "{table}" ({cols}) VALUES ({vals})'
        c = self.conn.cursor()
        c.execute(sql, row)
        self.conn.commit()
        self.lastrowid = c.lastrowid

    def add_item(self, item):
        """
        Add the elements of a TinyDB item to the relevant tables.
        """
        row = dict(
                item_id = item.eid,
                item_type = item['itemtype'],
                summary = item['summary'],
                item_index = item.get('i', "none"),
                calendar = item.get('c', "none"),
                created_dt = timestamp_from_eid(item.eid),
                )
        self.sqlite_insert('items', row)



def main():
    items = Table('test/items.db')
    print(f"sqlite3: {items.sqlite3_version}, sqlite: {items.sqlite_version}")

if __name__ == '__main__':
    main()
