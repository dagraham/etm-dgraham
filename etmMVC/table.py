import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

items_table = """ CREATE TABLE IF NOT EXISTS \
items_table ( 
    item_id integer PRIMARY KEY,
    type text NOT NULL,
    summary text NOT NULL,
    created_dt text NOT NULL,
    calendar text NOT NULL,
    modified_dt text NOT NULL,
    index text
); """

starting_table = """ CREATE TABLE IF NOT EXISTS \ 
starting_table (
    starting_id integer PRIMARY KEY,
    starting_dt text NOT NULL,
    interval text,
    FOREIGN KEY (item_id) REFERENCES items_table
); """

finished_table = """ CREATE TABLE IF NOT EXISTS \ 
starting_table (
    finished_id integer PRIMARY KEY,
    finished_dt text NOT NULL,
    past_due text,
    FOREIGN KEY (item_id) REFERENCES items_table
); """

tags_table = """ CREATE TABLE IF NOT EXISTS \ 
tags (
    tag_id integer PRIMARY KEY,
    tag_name text NOT NULL
); """

items_tags_bridge = """ CREATE TABLE IF NOT EXISTS \
item_tags_bridge (
    FOREIGN KEY (item_id) REFERENCES items_table,
    FOREIGN KEY (tags_id) REFERENCES tags_table,
); """
