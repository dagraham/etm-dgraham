import pendulum
from model import timestamp_from_eid, fmt_week
pendulum.set_formatter('alternative')

short_dt_fmt = "YYYY-MM-DD HH:mm"

# each view in views: (row, eid) where row = ((sort), (path), (columns))

class Views(object):

    def __init__(self):
        self.views = dict(
                created_view = [],   # row for id not changed with updates to that item
                index_view = [],
                modified_view = [],
                tags_view = [],
                agenda_view = [],
                next_view = [],
                someday_view = []
                )
        self.relevant = {}  # id -> dt
        self.begins =  []   # (beg_dt, start_dt, id)
        self.created = {}   # id -> dt

        self.commands = dict(
                update_index = self._update_index_view,
                update_modified = self._update_modified_view,
                update_tags = self._update_tags_view,
                update_done = self._update_done_view,
                update_busy = self._update_busy_view,
                )


    def _insert_rows(self, view, list_of_rows):
        for row in list_of_rows:
            self.views[view].append((row, self.id))
        self.views[view].sort()

    def _remove_rows(self, view):
        """
        Remove all rows from view corresponding to the given id. This shouldn't affect the sort.
        """
        self.views[view] = [x for x in self.views[view] if x[-1] != self.id]

    def _update_rows(self, view, list_of_rows):
        self._remove_rows(view)
        self._insert_rows(view, list_of_rows)

    def _update_created_view(self):
        created = timestamp_from_eid(self.item.eid)
        self.created[id] = created
        self._update_rows(
                'created_view',
                [
                    ( created, (), (f"{self.item['itemtype']} {self.item['summary']}", created.format(short_dt_fmt)))
                    ]
                )

    def _update_index_view(self):
        tup = self.item.get('index', '~').split(':')
        self._update_rows(
                'index_view', 
                [
                    (tup, tup, (f"{self.item['itemtype']} {self.item['summary']}"))
                    ]
                )

    def _update_modified_view(self):
        if 'modified' in self.item:
            modified = item['modified']
            self._update_rows(
                    'modified_view',
                    [
                        ( modified, (), (f"{self.item['itemtype']} {self.item['summary']}", modified.format(short_dt_fmt))
                        )
                        ]
                    )

    def _update_tags_view(self):
        if 't' in self.item:
            rows = []
            tags = [x.strip() for x in self.item['t']]
            for tag in tags:
                rows.append((tag, tag, (f"{self.item['itemtype']} {self.item['summary']}")))
            self._update_rows('tags_view', rows)

    def _update_done_view(self):
        dts = []
        if 'f' in self.item:
            dts.append(self.item['f'])
        if 'h' in self.item:
            dts.extend(self.item['h'])
        if dts:
            rows = []
            for dt in dts:
                rows.append((dt, (fmt_week(dt), dt.format('ddd MMM 2')),  (f"{self.item['itemtype']} {self.item['summary']}", dt.format("H:mm"))))
            self._update_rows('done_view', rows)

    def _update_busy_view(self):
        pass


    def _update_weeks(self):
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
        if (self.item['itemtype'] in ['?', '!', '~'] 
                or 'f' in self.item 
                or 's' not in self.item
                ):
            return
        # if @r in item get instances from rrulestr
        # elif @+ get instances from @s and @+
        # else @s is the only instance
        # note: tasks with jobs will contribute several rows for each instance
        # note: multiday events will contribute several rows for each instance


    def _refresh(self):
        # finished tasks
        if self.item['itemtype'] in ['?', '!']:
            return
        if "f" in self.item and self.item['f']:
            # this includes finished, undated tasks and actions
            # no past dues or begin bys for these
             self.relevant[self.id] = self.item['f']
             return 
        # unfinished tasks or scheduled events
        if 's' in self.item:
            if 'r' in self.item or '+' in self.item:
                # repeating
                if self.item['itemtype'] == '-':
                    if 'o' in self.item and self.item['o'] == 's':
                        # FIXME
                        pass
                    else:
                        # keep or restart
                        return self.item['s']




    def _update_all(self):
        for cmd in self.commands:
            print(f'processing {cmd}')
            cmd()


    def process_item(self, item):
        self.item = item
        self.id = item.eid
        if self.id in self.created:
            # exiting
            self._update_all()
        else:
            # new
            self._update_created()
            self._update_all()




