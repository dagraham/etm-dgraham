import sqlite3
from sqlite3 import Error
from datetime import date, datetime
from model import timestamp_from_eid
import os

db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

def create_connection(db_file=':memory:', overwrite=True):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    if overwrite and db_file != ':memory:' and os.path.isfile(db_file):
        os.remove(db_file) 
    try:
        conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        return conn
    except Error as e:
        print(e)
    return None

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
            item_index TEXT PRIMARY KEY
        ); """,
    starts = """ CREATE TABLE 
        starts (
            starts_id integer PRIMARY KEY,
            starts_dt TIMESTAMP NOT NULL,
            ends_dt TIMESTAMP,
            item_id,
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        ); """,
    dones = """ CREATE TABLE  
        dones (
            done_id integer PRIMARY KEY,
            done_dt TIMESTAMP NOT NULL,
            past_due text,
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
    begins = """ CREATE TABLE  
        begins (
            begins_id integer PRIMARY KEY,
            begins_dt TIMESTAMP NOT NULL,
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


def sqlite_insert(conn, table, row):
    keys = row.keys()
    cols = ', '.join('"{}"'.format(col) for col in keys)
    vals = ', '.join(':{}'.format(row[col]) for col in keys)
    sql = f'INSERT INTO "{table}" ({cols}) VALUES ({vals})'
    c = conn.cursor()
    c.execute(sql, row)
    conn.commit()
    return c.lastrowid

def add_item(conn, item):
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
    rid = sqlite_insert(conn, 'items', row)

    # if 's' in item



def main():
    conn = create_connection('test/items.db')
    if conn is not None:
        with conn:
            c = conn.cursor()
            # for table in tables.keys():
            #     try:
            #         sql = f"DROP TABLE IF EXISTS {table};"
            #         c.execute(sql)
            #     except Error as e:
            #         print(e)
            #         print(sql)
            conn.commit()
            for table in tables:
                try:
                    c.execute(tables[table])
                except Error as e:
                    print(e)
                    print(tables[table])
            # conn.commit()

if __name__ == '__main__':
    main()
