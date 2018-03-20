 #! /usr/bin/env python3
# Last Edited: Mon 05 Feb 2018 09:59 EST
import json
import pendulum
from pendulum import parse
pendulum.set_formatter('alternative')

# from dateutil.tz import gettz, tzutc, tzlocal

# from model import ONEWEEK, ONEDAY, ONEHOUR, ONEMINUTE
from model import  set_summary 
from model import item_instances
from model import fmt_extent, format_interval, fmt_week
from model import TimeIt
from model import load_tinydb

testing = True
# testing = False

pendulum.set_formatter('alternative')

short_dt_fmt = "YYYY-MM-DD HH:mm"

ETMFMT = "YYYYMMDDTHHmm"

# set up 2 character weekday name abbreviations 
# pendulum.set_locale('fr')
WA = {}
today = pendulum.today()
day = today.end_of('week')  # Sunday
for i in range(1, 8):
    # 1 -> Mo, ...,  7 -> Su
    WA[i] = day.add(days=i).format('ddd')[:2]

ampm = True
LL = {}
for hour in range(24):
    if hour % 6 == 0:
        if ampm:
            suffix = 'am' if hour < 12 else 'pm'
            if hour == 0:
                hr = 12
            elif hour <= 12:
                hr = hour
            elif hour > 12:
                hr = hour - 12
            LL[hour] = f"{hr}{suffix}".rjust(6, ' ')
        else:
            LL[hour] = f"{hour}h".rjust(6, ' ')
    else:
        LL[hour] = '-'.rjust(6, ' ')

# each view in views: (row, eid) where row = ((sort), (path), (columns))


busy_template = """\
         {WA[1]} {DD[1]}  {WA[2]} {DD[2]}  {WA[3]} {DD[3]}  {WA[4]} {DD[4]}  {WA[5]} {DD[5]}  {WA[6]} {DD[6]}  {WA[7]} {DD[7]} 
         -----------------------------------------------  
{l[0]}   {h[0][1]}  {h[0][2]}  {h[0][3]}  {h[0][4]}  {h[0][5]}  {h[0][6]}  {h[0][7]}
{l[1]}   {h[1][1]}  {h[1][2]}  {h[1][3]}  {h[1][4]}  {h[1][5]}  {h[1][6]}  {h[1][7]}
{l[2]}   {h[2][1]}  {h[2][2]}  {h[2][3]}  {h[2][4]}  {h[2][5]}  {h[2][6]}  {h[2][7]}
{l[3]}   {h[3][1]}  {h[3][2]}  {h[3][3]}  {h[3][4]}  {h[3][5]}  {h[3][6]}  {h[3][7]}
{l[4]}   {h[4][1]}  {h[4][2]}  {h[4][3]}  {h[4][4]}  {h[4][5]}  {h[4][6]}  {h[4][7]}
{l[5]}   {h[5][1]}  {h[5][2]}  {h[5][3]}  {h[5][4]}  {h[5][5]}  {h[5][6]}  {h[5][7]}
{l[6]}   {h[6][1]}  {h[6][2]}  {h[6][3]}  {h[6][4]}  {h[6][5]}  {h[6][6]}  {h[6][7]}
{l[7]}   {h[7][1]}  {h[7][2]}  {h[7][3]}  {h[7][4]}  {h[7][5]}  {h[7][6]}  {h[7][7]}
{l[8]}   {h[8][1]}  {h[8][2]}  {h[8][3]}  {h[8][4]}  {h[8][5]}  {h[8][6]}  {h[8][7]}
{l[9]}   {h[9][1]}  {h[9][2]}  {h[9][3]}  {h[9][4]}  {h[9][5]}  {h[9][6]}  {h[9][7]}
{l[10]}   {h[10][1]}  {h[10][2]}  {h[10][3]}  {h[10][4]}  {h[10][5]}  {h[10][6]}  {h[10][7]}
{l[11]}   {h[11][1]}  {h[11][2]}  {h[11][3]}  {h[11][4]}  {h[11][5]}  {h[11][6]}  {h[11][7]}
{l[12]}   {h[12][1]}  {h[12][2]}  {h[12][3]}  {h[12][4]}  {h[12][5]}  {h[12][6]}  {h[12][7]}
{l[13]}   {h[13][1]}  {h[13][2]}  {h[13][3]}  {h[13][4]}  {h[13][5]}  {h[13][6]}  {h[13][7]}
{l[14]}   {h[14][1]}  {h[14][2]}  {h[14][3]}  {h[14][4]}  {h[14][5]}  {h[14][6]}  {h[14][7]}
{l[15]}   {h[15][1]}  {h[15][2]}  {h[15][3]}  {h[15][4]}  {h[15][5]}  {h[15][6]}  {h[15][7]}
{l[16]}   {h[16][1]}  {h[16][2]}  {h[16][3]}  {h[16][4]}  {h[16][5]}  {h[16][6]}  {h[16][7]}
{l[17]}   {h[17][1]}  {h[17][2]}  {h[17][3]}  {h[17][4]}  {h[17][5]}  {h[17][6]}  {h[17][7]}
{l[18]}   {h[18][1]}  {h[18][2]}  {h[18][3]}  {h[18][4]}  {h[18][5]}  {h[18][6]}  {h[18][7]}
{l[19]}   {h[19][1]}  {h[19][2]}  {h[19][3]}  {h[19][4]}  {h[19][5]}  {h[19][6]}  {h[19][7]}
{l[20]}   {h[20][1]}  {h[20][2]}  {h[20][3]}  {h[20][4]}  {h[20][5]}  {h[20][6]}  {h[20][7]}
{l[21]}   {h[21][1]}  {h[21][2]}  {h[21][3]}  {h[21][4]}  {h[21][5]}  {h[21][6]}  {h[21][7]}
{l[22]}   {h[22][1]}  {h[22][2]}  {h[22][3]}  {h[22][4]}  {h[22][5]}  {h[22][6]}  {h[22][7]}
{l[23]}   {h[23][1]}  {h[23][2]}  {h[23][3]}  {h[23][4]}  {h[23][5]}  {h[23][6]}  {h[23][7]}
         -----------------------------------------------  
{t[0]}   {t[1]}  {t[2]}  {t[3]}  {t[4]}  {t[5]}  {t[6]}  {t[7]}
"""
# l .rjust(6, ' ')
# h & t .center(5, ' ')

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
    {'total': 180, 9: '  #  ', 10: '  #  ', 11: '  #  '}
    >>> busy_conf_day([(540, 620), (600, 720), (660, 700)])
    {'total': 180, 9: '  #  ', 10: ' ### ', 11: ' ### '}
    >>> busy_conf_day([(540, 620), (620, 720), (700, 720)])
    {'total': 180, 9: '  #  ', 10: '  #  ', 11: ' ### '}
    >>> busy_conf_day([])
    {'total': 0}
    >>> busy_conf_day([(0, 1439)])
    {0: '  #  ', 'total': 1439, 1: '  #  ', 2: '  #  ', 3: '  #  ', 4: '  #  ', 5: '  #  ', 6: '  #  ', 7: '  #  ', 8: '  #  ', 9: '  #  ', 10: '  #  ', 11: '  #  ', 12: '  #  ', 13: '  #  ', 14: '  #  ', 15: '  #  ', 16: '  #  ', 17: '  #  ', 18: '  #  ', 19: '  #  ', 20: '  #  ', 21: '  #  ', 22: '  #  ', 23: '  #  '}
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
    for i in range(24):
        if i in busy_hours:
            h[i] = '#'.center(5, ' ')
        elif i in conf_hours:
            h[i] = '###'.center(5, ' ')
        # else:
        #     h[i] = '.'.center(3, ' ')
        h['total'] = total
    return h

class Views(object):
    """

    """
    # TODO: 

    def __init__(self):
        # lists in views only need to be updated on month change or item add/modify/remove
        self.views = dict(
                index_view = [],
                created_view = [], 
                modified_view = [],
                weeks_view = [],
                done_view = [],
                alerts = [],  
                tags_view = [],
                next_view = [],
                someday_view = [],
                instances = [],
                busy = [], 
                relevant = [],  
                )
        self.items = {}

        self.commands = dict(
                update_index = self._update_index_view,
                update_created = self._update_created_view,
                update_modified = self._update_modified_view,
                update_weeks = self._update_weeks,
                update_dones = self._update_dones,
                update_alerts = self._update_alerts,
                update_tags = self._update_tags_view,
                update_next = self._update_next_view,
                update_someday = self._update_someday_view,
                )

        # set 2 character weekday name abbreviations

        self.yearmonth = None
        self.beg_dt = self.end_dt = None
        # total months for week views = 1 + bef + aft
        self.bef_months = 5
        self.aft_months = 18
        self.modified = False
        self.todays_alerts = []
        self.completions = {}
        for c in ['i', 'c', 't', 'z']:
            self.completions[c] = set([])
        self.maybe_refresh()

    def day_of_week(self, dt):
        """
        Make Sundays day 7
        """
        return dt.day_of_week if dt.day_of_week > 0 else 7

    def fmt_weekday(self, dt):
        """
        Format the day and append (Today) if dt.date() is today.
        """
        today = " (Today)" if dt.date() == self.today else ""
        return f"{dt.format('ddd MMM D')}{today}"

    def dt_from_year_week_day(self, yw, d):
        """
        Return datetime from ((year, week_of_year), day_of_week)
        """
        return parse(f"{yw[0]}-W{str(yw[1]).zfill(2)}-{d}")


    def maybe_refresh(self):
        """
        If the current month has changed, reset the begin and end dates for the period to include the current month, the preceeding 5 months and the subsequent 18 months. Adjust the dates to include 6 complete weeks for each of the 24 months.
        """
        self.today = today = pendulum.today()
        # self.now = now = pendulum.now('Factory')
        yearmonth = (today.year, today.month)
        if yearmonth != self.yearmonth:
            # update year month - this will run on init since self.yearmonth is None
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
            # load the TinyDB database from file (or memory?)
            self.load_TinyDB()
            self.load_views()
            self.modified = True
        if today != self.today:
            self.today = today
            self.modified = True
        if self.modified:
            self._update_relevant()
            self._todays_begins()
            self._todays_pastdues()
            self._todays_alerts()
            self.sort_views()

    def sort_views(self):
        for view in self.views:
            if isinstance(self.views[view], list):
                try:
                    self.views[view].sort()
                except Exception as e:
                    print(e)
                    print(view)
                    print(self.views[view])
        # write views to permit viewing - not needed otherwise
        with open('views.json', 'w') as jo:
            json.dump(self.views, jo, indent=1, sort_keys=True)


    def nothing_secheduled(self):
        pass

    def load_TinyDB(self):
        """
        Populate the views 
        """
        tt = TimeIt(1, label="load_TinyDB")
        self.items = load_tinydb()
        tt.stop()

    def load_views(self):
        tt = TimeIt(1, "load_views")
        for item in self.items:
            for c in self.completions:
                if c in item:
                    if c == 't':
                        for tag in item['t']:
                            tag = tag.strip()
                            if tag:
                                self.completions['t'].add(tag)
                    else:
                        self.completions[c].add(item[c])
            for cmd in self.commands:
                self.commands[cmd](item)
        tt.stop()


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

    def _update_dones(self, item):
        dts = []
        if item['itemtype'] not in ['-', '~']:
            return 
        if 'f' not in item and 'h' not in item:
            return
        if item['itemtype'] == '-':
            char = 'x'
        else:
            char = '~'

        if 'f' in item:
            dts.append(item['f'])
        if 'h' in item:
            dts.extend(item['h'])
        if dts:
            rows = []
            for dt in dts:
                if type(dt) == pendulum.pendulum.Date:
                    dt = pendulum.create(year=dt.year, month=dt.month, day=dt.day, hour=0, minute=0, tz=None)
                if not self.beg_dt <= dt <= self.end_dt:
                    continue
                if dt.hour == dt.minute == 0:
                    rhc = ""
                else:
                    if ampm:
                        rhc = dt.format("h:mmA").lower()
                    else:
                        rhc = dt.format("H:mm")
                day_of_week = self.day_of_week(dt)
                sort = (dt.year, dt.week_of_year, day_of_week, dt.hour, dt.minute)
                path = (sort[:2], sort[2])
                cols = (f"{char} {item['summary']}", rhc)
                rows.append((sort, path, cols))
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
        if item['itemtype'] == '!':
            day_of_week = self.day_of_week(self.today)
            sort = (self.today.year, self.today.week_of_year, day_of_week, 2)
            # path = (fmt_week(self.today), self.today.format('ddd MMM D'))
            path = (sort[:2], sort[2])
            cols = (f"! {item['summary']}")
            rows = ((sort, path, cols))
            self._update_rows('weeks_view', rows, item.doc_id)
            return
        if (item['itemtype'] == '-'  and 's' not in item):
            self.views['next_view'].append(item.doc_id)
            return
        if item['itemtype'] == '?' or 's' not in item:
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

            # hack to make sunday day 7
            day_of_week = self.day_of_week(beg)
            sort = (beg.year, beg.week_of_year, day_of_week, sort_code, beg.hour, beg.minute)
            # path = (fmt_week(beg), beg.format('ddd MMM D'))
            path = (sort[:2], sort[2])
            cols = (f"{item['itemtype']} {summary}", rhc)
            rows.append((sort, path, cols))
            if item['itemtype'] == "*" and end:
                beg_min = beg.hour*60 + beg.minute
                end_min = end.hour*60 + end.minute
                tmp = ((beg.year, beg.week_of_year), day_of_week,  (beg_min, end_min))
                busy.append(tmp)
            # self.views['weeks'].setdefault(path[0], []).append((path[1], item.eid))
        self._update_rows('weeks_view', rows, item.eid)
        overdue = 'r' not in item or ('o' in item and item['o'] != 's')
        instance_rows = [(x.format(ETMFMT), item['itemtype'], 'b' in item, 'f' in item, overdue) for x in instances]
        self._update_rows('busy', busy, item.eid)
        self._update_rows('instances', instance_rows, item.eid)

    def get_busy_week(self, year_week):
        """

        """
        tt = TimeIt(1, "get_busy_week")
        # get monthdays for the week
        mon = self.dt_from_year_week_day((year_week[0], year_week[1]), 1)
        week_fmt = fmt_week(mon)
        DD = {}
        for i in range(7):
            DD[i+1] = mon.add(days=i).format("D").ljust(2, ' ')
        # get (day_of_week, list of beg_end tups) for the week
        h = {}
        t = {0: 'total'.rjust(6, ' ')}
        for weekday in range(1, 8):
            t[weekday] = '0'.center(5, ' ')

        for hour in range(24):
            h.setdefault(hour, {})
            for weekday in range(1, 8):
                h[hour][weekday] = '  .  '
        busy_tups = [(x[0][1], x[0][2]) for x in self.views['busy'] if x[0][0] == year_week]
        if busy_tups: 
            busy = {}
            for tup in busy_tups:
                busy.setdefault(tup[0], []).append(tup[1])
            for weekday in range(1, 8):
                lofp = busy.get(weekday, [])
                hours = busy_conf_day(lofp)
                t[weekday] = str(hours['total']).center(5, ' ')
                for hour in range(24):
                    if hour in hours:
                        h[hour][weekday] = hours[hour]
        tt.stop()
        return week_fmt, busy_template.format(WA=WA, DD=DD, t=t, h=h, l=LL)


    def get_done_week(self, year_week):
        """

        """
        tt = TimeIt(1, "get_done_week")
        # get monthdays for the week
        mon = self.dt_from_year_week_day((year_week[0], year_week[1]), 1)
        week_fmt = fmt_week(mon)
        tmp = [x for x in self.views['done_view'] if (x[0][0][0], x[0][0][1]) == year_week]
        ret = []
        for ((sort, path, cols), id) in tmp:
            path = list(path)
            dt = self.dt_from_year_week_day(path[0], path[1])
            path = (fmt_week(dt), self.fmt_weekday(dt))
            ret.append(((sort, path, cols), id))
        tt.stop()
        return ret


    def get_agenda_week(self, year_week):
        """

        """
        tt = TimeIt(1, "get_agenda_week")
        # get monthdays for the week
        mon = self.dt_from_year_week_day((year_week[0], year_week[1]), 1)
        week_fmt = fmt_week(mon)
        tmp = [x for x in self.views['weeks_view'] if (x[0][0][0], x[0][0][1]) == year_week]
        ret = []
        for ((sort, path, cols), id) in tmp:
            path = list(path)
            dt = self.dt_from_year_week_day(path[0], path[1])
            path = (fmt_week(dt), self.fmt_weekday(dt))
            ret.append(((sort, path, cols), id))
        tt.stop()
        return ret

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
        tt = TimeIt(1, "_todays_alerts")
        alerts = []
        today = self.today.format(ETMFMT)
        tomorrow = self.today.add(days=1).format(ETMFMT)
        for alert in self.views['alerts']:
            if today <= alert[0][0] < tomorrow:
                print(today, alert[0][0], tomorrow)
                alerts.append(alert)
        self.todays_alerts = alerts
        tt.stop()


    def _todays_begins(self):
        tt = TimeIt(1, label="_todays_begins")
        today = self.today.format(ETMFMT)
        beg_instances = [x for x in self.views['relevant'] if x[0][2] == 'begin']
        rows = []

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

                day_of_week = self.day_of_week(self.today)
                sort = (self.today.year, self.today.week_of_year, day_of_week, 4, self.today.hour, self.today.minute)
                # path = (fmt_week(self.today), self.today.format('ddd MMM D'))
                path = (sort[:2], sort[2])
                cols = (f">  {summary}", f"{days}d")
                rows = ((sort, path, cols))
                self._update_rows('weeks_view', rows, id)
        tt.stop()


    def _todays_pastdues(self):
        tt = TimeIt(1, label="_todays_pastdues")
        pd_instances = [x for x in self.views['relevant'] if x[0][2] == 'pastdue']
        rows = []

        for instance in pd_instances:
            id = instance[-1]
            item = self.items.get(eid=id)

            due = instance[0][0]
            due_dt = parse(due)
            days = (self.today - due_dt).days

            summary = set_summary(item['summary'], due)
            day_of_week = self.day_of_week(self.today)
            sort = (self.today.year, self.today.week_of_year, day_of_week, 3, self.today.hour, self.today.minute)
            path = (sort[:2], sort[2])
            cols = (f"<  {summary}", f"{days}d")
            rows = ((sort, path, cols))
            self._update_rows('weeks_view', rows, id)
        tt.stop()

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
    import doctest
    from pprint import pprint
    doctest.testmod()

