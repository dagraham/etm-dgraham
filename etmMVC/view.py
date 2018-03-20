import pendulum
from pendulum import parse
from model import timestamp_from_id, fmt_week, setup_logging, serialization, item_details, item_instances, beg_ends, fmt_extent, format_interval, getMonthWeeks, set_summary, TimeIt

from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware
from tinydb_smartcache import SmartCacheTable
import json

import logging
import logging.config
logger = logging.getLogger()

from pprint import pprint

if __name__ == '__main__':
    print('\n\n')
    setup_logging(1)
    import doctest
    tt = TimeIt(loglevel=1, label=f"views")
    my_views = Views()
    tt.stop()
    weeks = [(2018, 2), (2018, 11), (2018, 12)]
    for week in weeks:
        head, weekfmt = my_views.get_busy_week(week)
        print(f"  {head}")
        print(weekfmt)
        print(my_views.get_done_week(week))
        print()
        print(my_views.get_agenda_week(week))
        print()
    print('completions:', my_views.completions)

    doctest.testmod()
