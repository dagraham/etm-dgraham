import pendulum
from pendulum import parse
from model import timestamp_from_id, fmt_week, setup_logging, serialization, item_details, item_instances, beg_ends, fmt_extent, format_interval, getMonthWeeks, set_summary
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

# set up 2 character weekday name abbreviations 
WA = {}
today = pendulum.today()
day = today.end_of('week')  # Sunday
for i in range(7):
    # 0 -> Su will, 1 -> Mo and so forth
    WA[i] = day.add(days=i).format('ddd')[:2]
print(WA)


# Mo 22  Tu 23  We 24  Th 25  Fr 26  Sa 27  Su 28  
busy_header_template = """\
     {WA[1]} {DD[1]}  {WA[2]} {DD[2]}  {WA[3]} {DD[3]}  {WA[4]} {DD[4]}  {WA[5]} {DD[5]}  {WA[6]} {DD[6]}  {WA[0]} {DD[0]} 
"""

# each view in views: (row, eid) where row = ((sort), (path), (columns))

#      Mo 22  Tu 23  We 24  Th 25  Fr 26  Sa 27  Su 28  
#      -----------------------------------------------  
#  12a   .      .      .      .      .      .      . 
#        .      .      .      .      .      .      . 
#        .      .      .      .      .      .      . 
#        .      .      .      .      .      .      . 
#        .      .      .      .      .      .      . 
#        .      .      .      .      .      .      . 
#   6a   .      .      .      .      .      .      . 
#        .      .      .      .      .      .      . 
#        #      .      #      .      #      #      . 
#        #      .      #      .      #      #      . 
#        .      #      .      .      .      #      . 
#        .      #      .      #      .      #      # 
#  12p   #      .      .      #      .      #      # 
#        #      .      .     XXX     .      #      # 
#        .      .      .      #      .      .      # 
#        .      .      .      .      .      .      # 
#        #      .      .      .      .      .      . 
#        #      .      .      .      .      .      . 
#   6p   .      .      #      .      .      .      . 
#        #      .      #      .      .      .      . 
#        #      .      #      .      .      .      . 
#        #      .      .      .      .      .      . 
#        .      .      .      .      .      .      . 
#  12a   .      .      .      .      .      .      . 
#      -----------------------------------------------  
#total  320    120    210    180     90    320    250 


busy_template = """
     {WA[1]} {DD[1]}  {WA[2]} {DD[2]}  {WA[3]} {DD[3]}  {WA[4]} {DD[4]}  {WA[5]} {DD[5]}  {WA[6]} {DD[6]}  {WA[0]} {DD[0]} 
       -----------------------------------------------  
{l[0]}  {h[0][1]}  {h[0][2]}  {h[0][3]}  {h[0][4]}  {h[0][5]}  {h[0][6]}  {h[0][7]}
{l[1]}  {h[1][1]}  {h[1][2]}  {h[1][3]}  {h[1][4]}  {h[1][5]}  {h[1][6]}  {h[1][7]}
{l[2]}  {h[2][1]}  {h[2][2]}  {h[2][3]}  {h[2][4]}  {h[2][5]}  {h[2][6]}  {h[2][7]}
{l[3]}  {h[3][1]}  {h[3][2]}  {h[3][3]}  {h[3][4]}  {h[3][5]}  {h[3][6]}  {h[3][7]}
{l[4]}  {h[4][1]}  {h[4][2]}  {h[4][3]}  {h[4][4]}  {h[4][5]}  {h[4][6]}  {h[4][7]}
{l[5]}  {h[5][1]}  {h[5][2]}  {h[5][3]}  {h[5][4]}  {h[5][5]}  {h[5][6]}  {h[5][7]}
{l[6]}  {h[6][1]}  {h[6][2]}  {h[6][3]}  {h[6][4]}  {h[6][5]}  {h[6][6]}  {h[6][7]}
{l[7]}  {h[7][1]}  {h[7][2]}  {h[7][3]}  {h[7][4]}  {h[7][5]}  {h[7][6]}  {h[7][7]}
{l[8]}  {h[8][1]}  {h[8][2]}  {h[8][3]}  {h[8][4]}  {h[8][5]}  {h[8][6]}  {h[8][7]}
{l[9]}  {h[9][1]}  {h[9][2]}  {h[9][3]}  {h[9][4]}  {h[9][5]}  {h[9][6]}  {h[9][7]}
{l[10]}  {h[10][1]}  {h[10][2]}  {h[10][3]}  {h[10][4]}  {h[10][5]}  {h[10][6]}  {h[10][7]}
{l[11]}  {h[11][1]}  {h[11][2]}  {h[11][3]}  {h[11][4]}  {h[11][5]}  {h[11][6]}  {h[11][7]}
{l[12]}  {h[12][1]}  {h[12][2]}  {h[12][3]}  {h[12][4]}  {h[12][5]}  {h[12][6]}  {h[12][7]}
{l[13]}  {h[13][1]}  {h[13][2]}  {h[13][3]}  {h[13][4]}  {h[13][5]}  {h[13][6]}  {h[13][7]}
{l[14]}  {h[14][1]}  {h[14][2]}  {h[14][3]}  {h[14][4]}  {h[14][5]}  {h[14][6]}  {h[14][7]}
{l[15]}  {h[15][1]}  {h[15][2]}  {h[15][3]}  {h[15][4]}  {h[15][5]}  {h[15][6]}  {h[15][7]}
{l[16]}  {h[16][1]}  {h[16][2]}  {h[16][3]}  {h[16][4]}  {h[16][5]}  {h[16][6]}  {h[16][7]}
{l[17]}  {h[17][1]}  {h[17][2]}  {h[17][3]}  {h[17][4]}  {h[17][5]}  {h[17][6]}  {h[17][7]}
{l[18]}  {h[18][1]}  {h[18][2]}  {h[18][3]}  {h[18][4]}  {h[18][5]}  {h[18][6]}  {h[18][7]}
{l[19]}  {h[19][1]}  {h[19][2]}  {h[19][3]}  {h[19][4]}  {h[19][5]}  {h[19][6]}  {h[19][7]}
{l[20]}  {h[20][1]}  {h[20][2]}  {h[20][3]}  {h[20][4]}  {h[20][5]}  {h[20][6]}  {h[20][7]}
{l[21]}  {h[21][1]}  {h[21][2]}  {h[21][3]}  {h[21][4]}  {h[21][5]}  {h[21][6]}  {h[21][7]}
{l[22]}  {h[22][1]}  {h[22][2]}  {h[22][3]}  {h[22][4]}  {h[22][5]}  {h[22][6]}  {h[22][7]}
{l[23]}  {h[23][1]}  {h[23][2]}  {h[23][3]}  {h[23][4]}  {h[23][5]}  {h[23][6]}  {h[23][7]}
       -----------------------------------------------  
{l[24]}  {t[1]}  {t[2]}  {t[3]}  {t[4]}  {t[5]}  {t[6]}  {t[7]}
"""
# l .rjust(6, ' ')
# h & t .center(3, ' ')

def busy_conf_minutes(lofp):
    """
    lofp is a list of tuples of (begin_minute, end_minute) busy times, e.g., [(b1, e1) , (b2, e2), ...]. By construction bi > ei. By sort, bi >= bi+1. Suppose we have
    [(540, 600), (600, 720)]
    >>> busy_conf_minutes([(540, 600)])
    ([(540, 600)], [], 60)
    >>> busy_conf_minutes([(540, 600), (600, 720)])
    ([(540, 600), (600, 720)], [], 180)
    >>> busy_conf_minutes([(540, 620), (600, 720), (660, 700)])
    ([(540, 600), (620, 660), (700, 720)], [(600, 620), (660, 700)], 180)
    """
    lofp.sort()
    busy_minutes = []
    conf_minutes = []
    if not lofp:
        return ([], [], 0)
    (b, e) = lofp.pop(0)
    while lofp:
        (B, E) = lofp.pop(0)
        if e <= B:  # no conflict
            busy_minutes.append((b, e))
            b = B
            e = E
        else:  # B < e
            busy_minutes.append((b, B))
            if e <= E:
                conf_minutes.append((B, e))
                b = e
                e = E
            else:  # E < e
                conf_minutes.append((B, E))
                b = E
                e = e
    busy_minutes.append((b, e))
    total_minutes = 0
    for (b, e) in busy_minutes + conf_minutes:
        total_minutes += e - b
    return busy_minutes, conf_minutes, total_minutes

def busy_conf_day(lofp):
    """
    >>> busy_conf_day([(540, 600), (600, 720)])
    {'total': 180, 9: ' # ', 10: ' # ', 11: ' # '}
    >>> busy_conf_day([(540, 620), (600, 720), (660, 700)])
    {'total': 180, 9: ' # ', 10: '###', 11: '###'}
    >>> busy_conf_day([(540, 620), (620, 720), (700, 720)])
    {'total': 180, 9: ' # ', 10: ' # ', 11: '###'}
    >>> busy_conf_day([])
    {'total': 0}
    """

    busy_ranges, conf_ranges, total = busy_conf_minutes(lofp)
    busy_hours = []
    conf_hours = []

    for (b, e) in conf_ranges:
        h_b = b // 60
        h_e = e // 60
        if e % 60: h_e += 1
        for i in range(h_b, h_e):
            if i not in conf_hours:
                # print("adding", i, "to conf")
                conf_hours.append(i)

    for (b, e) in busy_ranges:
        h_b = b // 60
        h_e = e // 60
        if e % 60: h_e += 1
        for i in range(h_b, h_e):
            if i not in conf_hours and i not in busy_hours:
                # print("adding", i, "to busy")
                busy_hours.append(i)
    h = {} 
    for i in range(23):
        if i in busy_hours:
            h[i] = '#'.center(3, ' ')
        elif i in conf_hours:
            h[i] = '###'
        # else:
        #     h[i] = '.'.center(3, ' ')
        h['total'] = total
    return h

# def busy_bar(lofp):
#     """
#     >>> busy_bar([(540, 600), (600, 720)])
#     {'total': 180, 9: ' # ', 10: ' # ', 11: ' # '}
#     >>> busy_bar([(540, 620), (600, 720), (660, 700)])
#     {'total': 180, 9: ' # ', 10: '###', 11: '###'}
#     >>> busy_bar([(540, 620), (620, 720), (700, 720)])
#     {'total': 180, 9: ' # ', 10: ' # ', 11: '###'}

#     """
#     busy_hours, conf_hours, total_minutes = busy_conf_hours(lofp)
#     h = {} 
#     for i in range(23):
#         if i in busy_hours:
#             h[i] = '#'.center(3, ' ')
#         elif i in conf_hours:
#             h[i] = '###'
#         # else:
#         #     h[i] = '.'.center(3, ' ')
#         h['total'] = total_minutes
#     return h


class Views(object):
    """
    TODO


    """


    def __init__(self):
        self.views = dict(
                created_view = [],   # row for id not changed with updates to that item
                index_view = [],
                modified_view = [],
                tags_view = [],
                weeks_view = [],
                agenda_view = [],
                next_view = [],
                someday_view = [],
                done_view = [],
                alerts = [],  
                instances = [],
                begins = [],    # (beg_dt, end_dt, id)
                busy = [],    # (beg_dt, end_dt, id)
                pastdues = [],  # (due_dt, id)
                inbox = [],
                relevant = [],  # (relevant_dt, id)
                )
        self.items = {}
        self.busy_view = {}

        self.commands = dict(
                update_index = self._update_index_view,
                update_created = self._update_created_view,
                update_modified = self._update_modified_view,
                update_weeks = self._update_weeks,
                # update_relevant = self._update_relevant,
                update_alerts = self._update_alerts,
                update_tags = self._update_tags_view,
                update_done = self._update_done_view,
                update_next = self._update_next_view,
                update_someday = self._update_someday_view,
                )

        # set 2 character weekday name abbreviations

        self.yearmonth = None
        self.beg_dt = self.end_dt = None
        self.bef_months = 5
        self.aft_months = 18
        self.modified = False
        self.todays_alerts = []
        self.maybe_refresh()


    def maybe_refresh(self):
        """
        If the current month has changed, reset the begin and end dates for the period to include the current month, the preceeding 5 months and the subsequent 18 months. Adjust the dates to include 6 complete weeks for each of the 24 months.
        """
        self.today = today = pendulum.today()
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
            self.load_views()
            self._update_agenda()

            self.modified = True
        if today != self.today:
            self.today = today
            self._update_agenda()
            self.modified = True
        if self.modified:
            self._update_relevant()
            self._update_begins()
            self._update_busy_view()
            self._update_pastdues()
            self._todays_alerts()
            self.save_views()

    def save_views(self):
        for view in self.views:
            if isinstance(self.views[view], list):
                try:
                    self.views[view].sort()
                except Exception as e:
                    print(e)
                    print(view)
                    print(self.views[view])
        with open('views.json', 'w') as jo:
            json.dump(self.views, jo, indent=1, sort_keys=True)


    def nothing_secheduled(self):
        pass

    def load_TinyDB(self):
        """
        Populate the views 
        """
        self.items = TinyDB('db.json', storage=serialization, default_table='items', indent=1, ensure_ascii=False)

    def load_views(self):
        for item in self.items:
            for cmd in self.commands:
                self.commands[cmd](item)


    def _add_rows(self, view, list_of_rows, id):
        if not isinstance(list_of_rows, list):
            list_of_rows = [list_of_rows]
        for row in list_of_rows:
            self.views[view].append((row, id))
        # self.views[view].sort() # FIXME do this after all rows have been added from all items 

    def _remove_rows(self, view, id):
        """
        Remove all rows from view corresponding to the given id. This shouldn't affect the sort.
        """
        self.views[view] = [x for x in self.views[view] if x[-1] != id]

    def _update_rows(self, view, list_of_rows, id):
        if list_of_rows:
            self._add_rows(view, list_of_rows, id)

    def _update_created_view(self, item):
        created = item['created']
        self._update_rows(
                'created_view',
                [
                    ( created.format(ETMFMT), (), (f"{item['itemtype']} {item['summary']}", created.format(short_dt_fmt))
                        )
                    ],
                item.doc_id
                )

    def _update_modified_view(self, item):
        if 'modified' in item:
            modified = item['modified']
            self._update_rows(
                    'modified_view',
                    [
                        ( modified.format(ETMFMT), (), (f"{item['itemtype']} {item['summary']}", modified.format(short_dt_fmt))
                        )
                        ],
                item.doc_id
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

    def _update_tags_view(self, item):
        if 't' in item:
            rows = []
            tags = [x.strip() for x in item['t'] if x.strip()]
            if tags:
                for tag in tags:
                    rows.append((tag, tag, (f"{item['itemtype']} {item['summary']}")))
                self._update_rows('tags_view', rows, item.eid)

    def _update_next_view(self, item):
        if 'f' in item:
            return
        if item['itemtype'] == '-' and 's' not in item:
            loc = item.get('l', "~")
            row = (loc, loc, (f"- {item['summary']}"))
            self._update_rows('next_view', row, item.eid)

    def _update_someday_view(self, item):
        if item['itemtype'] == '?':
            if 'modified' in item:
                dt = item['modified']
            else:
                dt = item['created']
            row = (dt.format(ETMFMT), (), (f"? {item['summary']}", 
                dt.format(short_dt_fmt)))
            self._update_rows('someday_view', row, item.eid)

    def _update_done_view(self, item):
        dts = []
        if item['itemtype'] == '-':
            char = 'x'
        else:
            char = item['itemtype']

        if 'f' in item:
            dts.append(item['f'])
        if 'h' in item:
            dts.extend(item['h'])
        if dts:
            rows = []
            for dt in dts:
                if type(dt) == pendulum.pendulum.Date:
                    dt = pendulum.create(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, tz=None)
                # FIXME sort should match week_view
                rows.append((dt.format(ETMFMT), (fmt_week(dt), dt.format('ddd MMM D')),  (f"{char} {item['summary']}", dt.format("H:mm"))))
            self._update_rows('done_view', rows, item.eid)

    def _update_relevant(self):
        relevant = None
        hsh = {}
        for ((dt, t, b, f, o), id) in self.views['instances']:
            hsh.setdefault(id, []).append((dt, t, b, f, o))
        for id in hsh:
            status = 'last'
            for (dt, t, b, f, o) in hsh[id]:
                # get the first instance of an unfinished task
                # or the first instance on or after today 
                # or, if none, the last
                today = self.today.format(ETMFMT)
                relevant = dt
                if t == '-':
                    if f:
                        status = 'finished'
                        break
                    elif dt < today:
                        if o:
                            status = 'pastdue'
                            break
                        else:
                            continue
                    else:
                        # not pastdue
                        if b:
                            status = 'begin'
                        else:
                            status = 'available'
                        break
                else:
                    if dt < today:
                        # relevant is the first on or after today
                        continue
                    else:
                        # the first after today
                        if b:
                            status = 'begin'
                        else:
                            status = 'next'
                        break
            self._update_rows('relevant', (relevant, t, status), id)

    def _update_weeks(self, item):
        """
        events and dated unfinished tasks and journal entries 
        sort = (date, type, time)
        path = (year_week, date)
        cols = (display_char summary, ?)
        """
        if (item['itemtype'] in ['?', '!', '~'] 
                or 's' not in item
                ):
            # if item['itemtype'] == '?':
            #     self.someday.append(item.eid)

            # elif item['itemtype'] == '!':
            #     self.inbox.append(item.eid)

            # elif item['itemtype'] == '-':
            #     self.next.append(item.eid)

            return
        rows = []
        instances = []
        busy = []
        # FIXME deal with jobs: skip finished, add available and waiting
        # only for the next instance
        if type(item['s']) == pendulum.pendulum.Date:
            # all day item
            it = item['itemtype']
            if it == '*':
                sort_code = 1
            elif it == '-':
                sort_code = 6
            else:
                sort_code = 7
        else:
            # datetime item
            sort_code = 5
        # set inbox (2), pastdue (3) and begins (4) later

        for (beg, end) in item_instances(item, self.beg_dt, self.end_dt):
            if end is None:
                rhc = ""
            else:
                rhc = fmt_extent(beg, end).center(15, ' ')
            instances.append(beg)
            summary = set_summary(item['summary'], beg)
            # sort = beg.format(ETMFMT)

            sort = (beg.year, beg.week_of_year, beg.day_of_week, sort_code, beg.hour, beg.minute)
            path = (fmt_week(beg), beg.format('ddd MMM D'))
            cols = (f"{item['itemtype']} {summary}", rhc)
            rows.append((sort, path, cols))
            if item['itemtype'] == "*" and end:
                beg_min = beg.hour*60 + beg.minute
                end_min = end.hour*60 + end.minute
                # tmp = (beg.format("YYYYMMDDT0000"), beg_min, end_min)
                tmp = ((beg.year, beg.week_of_year), beg.day_of_week,  (beg_min, end_min))
                busy.append(tmp)
            # self.views['weeks'].setdefault(path[0], []).append((path[1], item.eid))
        self._update_rows('weeks_view', rows, item.eid)
        overdue = 'r' not in item or ('o' in item and item['o'] != 's')
        instance_rows = [(x.format(ETMFMT), item['itemtype'], 'b' in item, 'f' in item, overdue) for x in instances]
        self._update_rows('busy', busy, item.eid)
        self._update_rows('instances', instance_rows, item.eid)

    def _update_busy_view(self):
        """

        """
        begends = {}
        for row in self.views['busy']:
            year_week, day, begend = row[0]
            begends.setdefault(year_week, {})
            begends[year_week].setdefault(day, []).append(begend)
        busy = {}
        for year_week in begends:
            busy.setdefault(year_week, {})
            for day in begends[year_week]:
                lofp = begends[year_week][day]
                busy[year_week][day] = busy_conf_day(lofp)

        active = self.end_dt - self.beg_dt
        # print(self.beg_dt, self.end_dt, active)
        # week: 1 Monday ... 6 Saturday, 0 Sunday
        weekdays = [1, 2, 3, 4, 5, 6, 0]
        for week in active.range('weeks'):
            # print(week.year, week.week_of_year, week.day_of_week)
            year_week = (week.year, week.week_of_year)
            if year_week in busy:
                for week_day in weekdays:
                    if week_day in busy[year_week]:
                        # things are scheduled
                        pass


    def _update_agenda(self):
        this_week = fmt_week(self.today)
        this_day = self.today.format("ddd MMM D")
        this_week_instances = [x for x in self.views['weeks_view'] if x[0][1][0] == this_week]
        this_day_instances = [x for x in this_week_instances if x[0][1][1] == this_day]
        # this_week_instances = self.views['weeks'].get(this_week, [])
        # this_day_instances = [x for x in this_week_instances if x[0] == this_day]
        if not this_day_instances:
            row = (self.today.format(ETMFMT), (this_week, this_day), ("Nothing scheduled", ""))
            self._update_rows('weeks_view', row, "")
            self.modified = True


        # mws = getMonthWeeks(self.today, self.bef_months, self.aft_months)
        # for mw in mws:
        #     key = f"{mw[0]}-{str(mw[1]).zfill(2)}"
        #     if key not in self.views['weeks']:
        #         print("missing week:", key)
        #         self.views['weeks'][key]["0"] = "Nothing scheduled"


    def _update_alerts(self, item):
        if 'a' not in item:
            return
        if 's' not in item:
            return
        alerts = []
        for alert in item['a']:
            cmd = alert[1]
            args = ""
            if len(alert) > 2 and alert[2]: 
                args = alert[2:]
            for td in alert[0]:
                dt = item['s']-td
                if dt < self.today:
                    continue
                if args:
                    alerts.append(
                            (
                                dt.format(ETMFMT),
                                cmd,
                                args,
                                format_interval(td),
                                item['summary'],
                                )
                            )
                else:
                    alerts.append(
                            (dt.format(ETMFMT),
                                cmd,
                                format_interval(td),
                                item['summary'],
                                )
                            )
        self._update_rows('alerts', alerts, item.eid)

    def _todays_alerts(self):
        alerts = []
        today = self.today.format(ETMFMT)
        tomorrow = self.today.add(days=1).format(ETMFMT)
        for alert in self.views['alerts']:
            if today <= alert[0][0] < tomorrow:
                print(today, alert[0][0], tomorrow)
                alerts.append(alert)
        self.todays_alerts = alerts


    def _update_begins(self):
        beg_instances = [x for x in self.views['relevant'] if x[0][2] == 'begin']
        rows = []

        today = self.today.format(ETMFMT)
        for instance in beg_instances:
            id = instance[-1]
            item = self.items.get(eid=id)
            end_begin = beg = instance[0][0]
            beg_dt = parse(beg)
            # the begin interval runs from b days before beg to beg
            start_begin = (beg_dt - pendulum.interval(days=item['b'])).format("YYYYMMDDT0000")
            if start_begin <= today < end_begin:
                days = (beg_dt - self.today).days
                summary = set_summary(item['summary'], beg_dt)
                sort = (self.today.year, self.today.week_of_year, self.today.day_of_week, 4, self.today.hour, self.today.minute)
                path = (fmt_week(self.today), self.today.format('ddd MMM D'))
                cols = (f">  {summary}", f"{days}d")
                rows = ((sort, path, cols))
                self._update_rows('weeks_view', rows, id)


    def _update_pastdues(self):
        pd_instances = [x for x in self.views['relevant'] if x[0][2] == 'pastdue']
        rows = []

        today = self.today.format(ETMFMT)
        for instance in pd_instances:
            id = instance[-1]
            item = self.items.get(eid=id)

            due = instance[0][0]
            due_dt = parse(due)
            days = (self.today - due_dt).days


            summary = set_summary(item['summary'], due)
            sort = (self.today.year, self.today.week_of_year, self.today.day_of_week, 3, self.today.hour, self.today.minute)

            path = (fmt_week(self.today), self.today.format('ddd MMM D'))
            cols = (f"<  {summary}", f"{days}d")
            rows = ((sort, path, cols))
            tmp = (today, days)
            self._update_rows('weeks_view', rows, id)





    def _update_all(self):
        for cmd in self.commands:
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

a =   " 1 "
b =   " 2 "
c =   " 3 "
d =   " 4 "
print(f"""
      |  This     is     a    test |
      |  {a}      {b}   {c}    {d} |
        """)
