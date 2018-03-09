import pendulum
from model import timestamp_from_eid, fmt_week, setup_logging, serialization, item_details
from tinydb import TinyDB, Query, Storage
from tinydb.operations import delete
from tinydb.database import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import Serializer
from tinydb_serialization import SerializationMiddleware
from tinydb_smartcache import SmartCacheTable
import json


from pprint import pprint

pendulum.set_formatter('alternative')

short_dt_fmt = "YYYY-MM-DD HH:mm"

ETMFMT = "YYYYMMDDTHHmm"

# each view in views: (row, eid) where row = ((sort), (path), (columns))

class Views(object):
    """
    TODO
    with open(json_file, 'w') as jo:
        json.dump(self.views, jo, indent=1, sort_keys=True)


    """


    def __init__(self):
        self.views = dict(
                created_view = [],   # row for id not changed with updates to that item
                index_view = [],
                modified_view = [],
                tags_view = [],
                agenda_view = [],
                next_view = [],
                someday_view = [],
                done_view = []
                )
        items = {}
        self.relevant = {}  # id -> dt
        self.begins =  []   # (beg_dt, start_dt, id)

        self.commands = dict(
                update_index = self._update_index_view,
                update_modified = self._update_modified_view,
                update_tags = self._update_tags_view,
                update_done = self._update_done_view,
                update_busy = self._update_busy_view,
                )



    def load_TinyDB(self):
        """
        Populate the views 
        """
        self.items = TinyDB('db.json', storage=serialization, default_table='items', indent=1, ensure_ascii=False)
        for item in self.items:
            for cmd in self.commands:
                self.commands[cmd](item)
        for view in self.views:
            self.views[view].sort()

        with open('views.json', 'w') as jo:
            json.dump(self.views, jo, indent=1, sort_keys=True)


    def _add_rows(self, view, list_of_rows):
        if not isinstance(list_of_rows, list):
            list_of_rows = [list_of_rows]
        for row in list_of_rows:
            self.views[view].append(row)
        # self.views[view].sort() # FIXME do this after all rows have been added from all items 

    def _remove_rows(self, view, id):
        """
        Remove all rows from view corresponding to the given id. This shouldn't affect the sort.
        """
        self.views[view] = [x for x in self.views[view] if x[-1] != id]

    def _update_rows(self, view, list_of_rows, id):
        self._remove_rows(view, id)
        self._add_rows(view, list_of_rows)

    def _update_created_view(self, item):
        created = timestamp_from_eid(item.eid)
        self._update_rows(
                'created_view',
                [
                    ( item.eid, (), (f"{item['itemtype']} {item['summary']}", created.format(short_dt_fmt), item.eid))
                    ],
                item.eid
                )

    def _update_index_view(self, item):
        if 'i' in item:
            tup = item['i'].split(':')
            self._update_rows(
                    'index_view', 
                    [
                        (tup, tup, (f"{item['itemtype']} {item['summary']}"), item.eid)
                        ],
                    item.eid
                    )

    def _update_modified_view(self, item):
        if 'modified' in item:
            modified = item['modified']
            self._update_rows(
                    'modified_view',
                    [
                        ( modified.format(ETMFMT), (), (f"{item['itemtype']} {item['summary']}", modified.format(short_dt_fmt), item.eid)
                        )
                        ],
                item.eid
                    )

    def _update_tags_view(self, item):
        if 't' in item:
            rows = []
            tags = [x.strip() for x in item['t']]
            for tag in tags:
                rows.append((tag, tag, (f"{item['itemtype']} {item['summary']}"), item.eid))
            self._update_rows('tags_view', rows, item.eid)

    def _update_done_view(self, item):
        dts = []
        if 'f' in item:
            dts.append(item['f'])
        if 'h' in item:
            dts.extend(item['h'])
        if dts:
            rows = []
            for dt in dts:
                if type(dt) == pendulum.pendulum.Date:
                    dt = pendulum.create(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, tz=None)
                rows.append((dt.format(ETMFMT), (fmt_week(dt), dt.format('ddd MMM 2')),  (f"{item['itemtype']} {item['summary']}", dt.format("H:mm")), item.eid ))
            self._update_rows('done_view', rows, item.eid)

    def _update_busy_view(self, item):
        pass


    def _update_weeks(self, item):
        """
        events and dated unfinished tasks and journal entries 
        sort = (date, type, time)
        path = (year_week, date)
        cols = (display_char summary, ?)

        relevant datetime:
            repeating events: first instance on or after today
            non repeating events: "s"
            repeating tasks:
                last or only instance finished: "f" - no alerts or beginbys
                unfinished:
                    non-repeating: "s"
                    repeating:
                        @o s: first unfinished instance on or after today - can't be pastdue 
                        @o r, k: first unfinished instance: "s" - pastdue if before today or "f" is last instance is finished
            non repeating tasks or repeating and finish
            beginby: relevant > today and relevant - "b" < today

The relevant datetime of an item (used in index view):
Non repeating events and unfinished tasks: the datetime given in @s
    done: Actions: the datetime given in @f
    done: Finished tasks: the datetime given in @f
Repeating events: the datetime of the first instance falling on or after today or, if none, the datetime of the last instance
Repeating tasks: the datetime of the first unfinished instance
Undated and unfinished items: None

        """
        if (item['itemtype'] in ['?', '!', '~'] 
                or 'f' in item 
                or 's' not in item
                ):
            return
        pass
        # if @r in item get instances from rrulestr
        # elif @+ get instances from @s and @+
        # else @s is the only instance
        # note: tasks with jobs will contribute several rows for each instance
        # note: multiday events will contribute several rows for each instance


    def _refresh(self, item):
        # finished tasks
        if item['itemtype'] in ['?', '!']:
            return
        if "f" in item and item['f']:
            # this includes finished, undated tasks and actions
            # no past dues or begin bys for these
             self.relevant[self.id] = item['f']
             return 
        # unfinished tasks or scheduled events
        if 's' in item:
            if 'r' in item or '+' in item:
                # repeating
                if item['itemtype'] == '-':
                    if 'o' in item and item['o'] == 's':
                        # FIXME
                        pass
                    else:
                        # keep or restart
                        return item['s']




    def _update_all(self):
        for cmd in self.commands:
            print(f'processing {cmd}')
            cmd()


    def process_item(self, item):
        item = item
        self.id = item.eid
        if self.id in self.created:
            # exiting
            self._update_all()
        else:
            # new
            self._update_created()
            self._update_all()


if __name__ == '__main__':
    print('\n\n')
    setup_logging(1)
    import doctest
    my_views = Views()
    my_views.load_TinyDB()

    # for item in my_views.items:
    #     try:
    #         print(item.eid, item['itemtype'])
    #         print(timestamp_from_eid(item.eid))
    #         print(item_details(item))
    #         print()
    #     except Exception as e:
    #         print('\nexception:', e)
    #         pprint(item)



    doctest.testmod()



