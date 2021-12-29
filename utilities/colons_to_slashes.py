import logging
import logging.config
logger = logging.getLogger()
import os
import sys
from tinydb import  Query

def colons_to_slashes():
    def transform(doc):
        res = doc.get('i', None)
        if res:
            doc['i'] = doc['i'].replace(':', '/')
        return doc
    return transform

def main():
    import etm.data as data
    etmdir = os.getcwd()

    loglevel = 2 # info
    log_levels = [str(x) for x in range(1, 6)]
    if len(sys.argv) > 1 and sys.argv[1] in log_levels:
        loglevel = sys.argv.pop(1)
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        etmdir = sys.argv.pop(1)

    logdir = os.path.normpath(os.path.join(etmdir, 'logs'))
    if not os.path.isdir(logdir):
        os.makedirs(logdir)

    dbfile = os.path.normpath(os.path.join(etmdir, 'db.json'))
    ETMDB = data.initialize_tinydb(dbfile)
    DBITEM = ETMDB.table('items', cache_size=None)
    DBARCH = ETMDB.table('archive', cache_size=None)

    Reminder = Query()
    ETMDB.update(colons_to_slashes(), Reminder.i.exists())

if __name__ == "__main__":
    main()

