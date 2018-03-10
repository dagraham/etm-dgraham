import pendulum
from model import timestamp_from_eid, fmt_week, setup_logging, serialization, item_details, item_instances, fmt_week, beg_ends, format_interval, getMonthWeeks
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
                weeks = {},
                agenda_view = [],
                next_view = [],
                someday_view = [],
                done_view = [],
                alerts = [],  
                begins = [],    # dt -> list of ids
                relevant = {},  # id -> list of dts
                )
        self.items = {}
        self.begins =  []   # (beg_dt, end_dt, id)

        self.commands = dict(
                update_index = self._update_index_view,
                update_created = self._update_created_view,
                update_modified = self._update_modified_view,
                update_weeks = self._update_weeks,
                update_alerts = self._update_alerts,
                update_begins = self._update_begins,
                update_tags = self._update_tags_view,
                update_done = self._update_done_view,
                update_busy = self._update_busy_view,
                )
        self.today = None
        self.yearmonth = None
        self.beg_dt = self.end_dt = None
        self.bef_months = 5
        self.aft_months = 18
        self.maybe_refresh()

    def maybe_refresh(self):
        """
        If the current month has changed, reset the begin and end dates for the period to include the current month, the preceeding 5 months and the subsequent 18 months. Adjust the dates to include 6 complete weeks for each of the 24 months.
        """
        self.today = today = pendulum.today('Factory')
        # self.now = now = pendulum.now('Factory')
        yearmonth = (today.year, today.month)
        if yearmonth != self.yearmonth:
            # update year month
            self.yearmonth = yearmonth
            # get the first day of the current month
            n_beg = pendulum.create(year=yearmonth[0], month=yearmonth[1], day=1, hour=0, minute=0, second=0, microsecond=0)
            # get the first day of the month bef_months before
            b = n_beg.subtract(months=self.bef_months)
            # get the first day of the month aft_months after
            e = n_beg.add(months=self.aft_months)
            # get 12am Monday of the first week in the begin month
            self.beg_dt = b.subtract(days=b.weekday())
            # to include 6 weeks, get 12am Monday of the 6th week
            # after the first week in the end month
            e = e.subtract(days=e.weekday())
            self.end_dt = e.add(weeks=6)
            self.load_TinyDB()
            self._update_agenda()
        if today != self.today:
            self.today = today
            self._update_agenda()


    def nothing_secheduled(self):
        pass

    def load_TinyDB(self):
        """
        Populate the views 
        """
        self.items = TinyDB('db.json', storage=serialization, default_table='items', indent=1, ensure_ascii=False)
        for item in self.items:
            for cmd in self.commands:
                self.commands[cmd](item)
        for view in self.views:
            if isinstance(self.views[view], list):
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
                    ( item.eid, (), (f"{item['itemtype']} {item['summary']}", created.format(short_dt_fmt)))
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
            tags = [x.strip() for x in item['t'] if x.strip()]
            if tags:
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
        """
        if 'f' in item:
            fin = item['f']
            if type(fin) == pendulum.pendulum.Date:
                # change to datetime at midnight on the same date
                fin = pendulum.create(year=fin.year, month=fin.month, day=fin.day, hour=0, minute=0, tz=None)
            # self.views['relevant'].setdefault(item.eid, []).append(fin.format(ETMFMT))
            self.views['relevant'][item.eid] = fin.format(ETMFMT)
            return
        if (item['itemtype'] in ['?', '!', '~'] 
                or 's' not in item
                ):
            return
        if type(item['s']) == pendulum.Pendulum and 'e' in item:
            rhc = beg_ends(item['s'], item['e'])[0][1].center(16, ' ')
            # rhc = item['s'].format("h:mmA", formatter="alternative")
        else:
            rhc = ""
        rows = []
        instances = []
        # FIXME deal with jobs: skip finished, add available and waiting
        # only for the next instance
        for dt in item_instances(item, self.beg_dt, self.end_dt):
            instances.append(dt)
            week = (f"{dt.year}-{str(dt.week_of_year).zfill(2)}")
            day = dt.day_of_week
            day = str(day) if day > 0 else "7"
            self.views['weeks'].setdefault(week, {}).update({'fmt': fmt_week(dt)})
            self.views['weeks'][week].setdefault(day, {}).update({'fmt': dt.format('ddd MMM D')})
            self.views['weeks'][week][day].setdefault('items', []).append(
                    (
                        f"{item['itemtype']} {item['summary']}", 
                        rhc,
                        item.eid
                        )
                    )
        for dt in instances:
            # get the first instance on or after today or, if none, the last
            relevant = dt
            if dt >= self.today:
                self.views['relevant'][item.eid] = relevant.format(ETMFMT)
                break


        # note: tasks with jobs will contribute several rows for each instance

    def _update_agenda(self):
        this_week = f"{self.today.year}-{str(self.today.week_of_year).zfill(2)}"
        this_day = str(self.today.day_of_week)
        if this_week not in self.views['weeks']:
            self.views['weeks'].setdefault(this_week, {}).update({'fmt': fmt_week(self.today)})
        if this_day not in self.views['weeks'][this_week]: 
            self.views['weeks'][this_week].setdefault(this_day, {}).update({'fmt': f"{self.today.format('ddd MMM D')} (Today)"})
            self.views['weeks'][this_week][this_day].setdefault('items', []).append(
                (
                    "Nothing scheduled", 
                    "",
                    ""
                    )
                )

        mws = getMonthWeeks(self.today, self.bef_months, self.aft_months)
        for mw in mws:
            key = f"{mw[0]}-{str(mw[1]).zfill(2)}"
            if key not in self.views['weeks']:
                print("missing week:", key)
                self.views['weeks'][key]["0"] = "Nothing scheduled"

    def _update_relevant(self, item):
        # finished tasks
        if item['itemtype'] in ['?', '!']:
            return
        if "f" in item and item['f']:
            # this includes finished, undated tasks and actions
            # no past dues or begin bys for these
             self.views[relevant][item.eid] = item['f']
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

    def _update_alerts(self, item):
        if 'a' not in item:
            return
        if 's' not in item:
            return
        alerts = []
        for alert in item['a']:
            cmd = alert[1]
            args = alert[2:]
            for td in alert[0]:
                dt = item['s']-td
                if dt < self.today:
                    continue
                alerts.append(
                        (dt.format(ETMFMT),
                            format_interval(td),
                            f"{item['itemtype']} {item['summary']}",
                            cmd,
                            args,
                            )
                        )
        self._update_rows('alerts', alerts, item.eid)

    def _update_begins(self, item):
        if not 'b' in item or item['s'] < self.today:
            return
        end = item['s']
        if type(end) == pendulum.pendulum.Date:
            # change to datetime at midnight on the same date
            end = pendulum.create(year=end.year, month=end.month, day=end.day, hour=0, minute=0, tz=None)
        td = pendulum.interval(days=item['b'])
        beg = end - td
        begins = [
                beg.format(ETMFMT), 
                end.format(ETMFMT), 
                f"{item['itemtype']} {item['summary']}",
                ]
        self._update_rows('begins', [begins], item.eid)





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
    print(my_views.beg_dt, my_views.end_dt)

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



