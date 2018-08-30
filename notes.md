# Notes for etm
**Last modified: Wed Aug 29, 2018 02:05PM EDT**

# Qt/QML

## Main/View Window

### Menus

* View Selection
  * Agenda
  * Busy
  * Done
  * Monthly?
  * Next
  * Someday (make someday a location for viewing in next?)
  * Index
  * History (3 columns: summary, date-created, date-modified)
  * Tags

  * Query?
  * Set Filter
  * Set Outline Level



# Design

## Requirements

* Create a new item
* Modify an existing item
  - edit
    + instance?
  - reschedule
  - schedule new  

* View items
  - Dated/synchronized
    + Agenda
    + Busy
    + Done
    + Monthly
  - Next
  - Someday
  - Index
  - History
    + Orignally created
    + Last modified
* Jump to 
* Search (Outline views will support filtering)
* Issue querries
* Get help information 

## Classes

* Edit
  - process/validate item string
  - create/update Item
* Item: 
  - record (update if id passed) 
  - filter method
  - search method 
  - get alerts
  - get begins 
* View Base Class
  - set topbar
  - set statusbar
  - set mainpanel (override)
  - 

## Decorators?

      class ItemDecorator(Item):
          def __init__(self, item): 
            super(ItemDecorator, self).__init__() 
            self.item = item

      class Dated(ItemDecorator): 

          def get_alerts(self):
              pass

          def get_begins(self);
              pass

      dated_item = Dated(Item())

# ToDo

## Issues

* FIXME: modifying a repeated item with @- entries that don't fit the new rule

## Refactor

* controller -> model
* view -> controller & edit
* urwid/urview -> view

## Defaults/Extractions

## Completions

## Jobs

* only show for relevant instance
* completions in done for task
* unfinished instances in weeks (or next)

* &s entries are intervals subtracted (+) or added (-) to @s - default 0m
* &b entries apply to &s
* &a entries apply to &s 

* def finish()...
  * when pressing F, how do I know which job is relevant?
		* use the job id?
	* take care of finishing a job and, if last_completed, the task itself


## First Run

allow creation of ~/.etm-mvc ?
* yes
  * create ~/.etm-mvc
	* create database with default/illustrative entries
	* create default options
* no
	* load empty database into memory
	* load default options
	* display warning about memory storage


## sort and color codes

* 1 Inbox (inbox color)
* 2 Pastdue (pastdue color)
* 3 Begins (begins color)
* Date only
	* 0 event (event color) before datetimes
	* 5 task or available job (task color) after datetimes
	* 6 waiting job (task color) after datetimes
	* 7 action (action color) 
	* 8 note (note color)
* 4 Datetime (sort by starting time)
	* event  (event color)
	* task or available job  (task color)
	* waiting job (waiting color)
	* note  (note color)
* Undated
  * task (task color)
	* note (note color)
	* 9 someday (someday color)

colors for these codes:
* 0 event
* 1 inbox
* 2 pastdue
* 3 begin
* 4 (sort code for datetime times - no color)
* 5 task or available job
* 6 waiting job
* 7 action
* 8 note
* 9 someday

types = [
		'ev',  # event
		'ib',  # inbox
		'td',  # pastdue (for a task group, only jobs can be past due)
		'by',  # beginby
		'ta',  # available task or job 
		'tw',  # job scheduled and waiting 
		'ac',  # action
		'nt',  # note 
		'so',  # someday
		]

type2Num = {key: val for val, key in enumerate(types)}
num2Type = {key: val for key, val in enumerate(types)}

## Busy

busy {year_week: {day_of_week: busy_bar}}

## alerts

[
  [(i1, i2, ...), cmd, args],

]

2nd column event


multiday?

from starting and ending date times
pairs = []
beg = starting
end = ending
while end.date > beg.date:
  end = beg.end_of('day')
  pairs.append(beg, end)
  beg = beg.start_of('day').add(days=1)
pairs.append(beg, end)


## Data Migration

* export to json from etmtk
* script to process entries in the exported yaml file and create corresponding TinyDB items.
  * for items with 's', also until in rrule
    * with 'z' => aware datetime using 'z'
    * without 'z' => naive datetime
  * timestamps (f, h, ...) FIXME
    * aware using local timezone

What do I need in the hash

* For scheduled items
  * created and modified timestamps
  * entry for details and edit
  * things that duplicate entry
    * itemtype
    * summary
    * rrulestr - RRULE
    * is rrulestr - RDATE needed? It is a string and repeats the datetime 
    * @s datetime
    * @e for 2nd column display
    * @c 
    * @t for tags
    * @i for index
    * @h for done, as a list of datetimes
    * @b for begin
    * @a for alerts

* ??? Maybe store all the components but not the entry and create entry on the fly using jinja2 ???



## Refactor Views

* MainView / Menu
* View
  * WeekView (selected week class variable)
    * Agenda
    * Busy
    * Done
    * Month 

# Saved

- `$`: action 

  - Requires entries for `@s`, the datetime the action began, `@e`, the time spent actively working on the action, and `@f`, the datetime the action ended. 

  - An etm *timer* can be used to record an action:

      - Select the item (task, event, ...) to which the action is to be applied.
      - Press the start key to start the timer.
      - Press the pause/restart key as often as desired.
      - Press the finish key to finish and record the new action.
      - The `@s` entry will record the moment at which the timer was first started, `@e` the accumulated time period during which the timer was active and `@f` the moment at which the timer was finished. 
      - The summary for the action and the value for `@i` will be those of the selected item. 
      - One or more timers can be active at the same time but only one can be running - the rest will be paused.

  - The item containing `@m` entries is displayed in the normal way. Additionally, each `@m` is also displayed using the display character `$` on the day and time that the action was finished and the summary from the item itself.
  - Displaying the details for an action will show the details for the item itself with all its `@m` entries.
  - Deleting a selected action will remove the associated `@m` entry.
  - Rescheduling a selected action will change the datetime finished component to the new datetime, leave the active timeperiod component unchanged and adjust the starting datetime to preserve the difference between staring datetime and the new finished datetime.


- The old *action* item type has been eliminated and its functionality has been replaced by the ability to use the `@m`, *memo* entry in *any* item to record time spent using the format `@m datetime started, timeperiod active,  datetime finished`. Such items need not have an `@s` entry.

    - An etm *timer* can be used to record an `@m` action entry:

        - Select the item (task, event, ...) to which the action is to be applied.
        - Press the start key to start the timer.
        - Press the pause/restart key as often as desired.
        - Press the finish key to finish and record the new action.
        - The `@m` entry will record the moment at which the timer was first started, the accumulated time period during which the timer was active and the moment at which the timer was finished.
        - One or more timers can be active at the same time but only one can be running - the rest will be paused.

    - Items can have multiple `@m` entries. 
    - The item containing `@m` entries is displayed in the normal way. Additionally, each `@m` is also displayed using the display character `$` on the day and time that the action was finished and the summary from the item itself.
    - Displaying the details for an action will show the details for the item itself with all its `@m` entries.
    - Deleting a selected action will remove the associated `@m` entry.
    - Rescheduling a selected action will change the datetime finished component to the new datetime, leave the active timeperiod component unchanged and adjust the starting datetime to preserve the difference between staring datetime and the new finished datetime.

# TODO

## States

* View
  * leaf (item) selected: Item & Tools
  * node selected: Tools
* Details
* Editing
* Query
* Dialog (responding to prompt)

* Timer Active
  * Running
  * Paused

Menu 
    File 
        New 
            Item                                   Shift-N 
        Timer 
            Start action timer                     Shift-A 
            Finish action timer                    Shift-T 
            Toggle current timer                      I 
            Cancel action timer                    Shift-I 
            Countdown timer                           Z 
        Open 
            Configuration file ...                 Shift-C 
            Preferences                            Shift-P 
        ---- 
        Quit                                         F8 
    View 
        Agenda                                        A 
        Busy                                          B 
        Done                                          D 
        Index                                         I 
        Next                                          N 
        History-Modified                              M
        History-Originated                            O
        Someday                                       S 
        Query                                         Q 
        Tags                                          T
        ---- 
        Set outline filter                          Ctrl-F 
        Clear outline filter                     Shift-Ctrl-F
        Outline level                                 L 
        Set outline depth                             O 
        Toggle finished                               X 
    Item 
        Copy                                       Shift-C 
        Delete                                     Shift-D 
        Edit                                       Shift-E 
        Finish                                     Shift-F 
        Open link                                  Shift-G 
        Reschedule                                 Shift-R 
        Schedule new                               Shift-S 
    Tools 
        Home                                         Home 
        Jump to date                                  J 
        ---- 
        Show remaining alerts for today            Shift-A 
        Date and time calculator                   Shift-D 
        Yearly calendar                            Shift-Y 
        ---- 
        Show outline as text                       Shift-O 
        Print outline                              Shift-P 
        Export to iCal                             Shift-X 
    Custom 
        Create and display selected report          Return 
        Export report in text format ...            Ctrl-T 
        Export report in csv format ...             Ctrl-X 
        Save changes to report specifications       Ctrl-W 
        Expand report list                           Down 
    Help 
        Search 
        Shortcuts                                     ? 
        User manual                                   F1 
        About                                         F2 
        Check for update                              F3 
Edit 
    Show completions                              Ctrl-Space 
    Cancel                                          Escape 
    Save and Close                                  Ctrl-S 

## Display Patterns

Entry: nothing
Prompt: item type character?
Help: list of type characters

Entry: type character and perhaps some of the summary
Prompt: item summary and @ key options?
Help: summary help
      Enter @ to see a list of available options

Entry: type char, summary and @
Prompt: @key?
Help: List of available @keys

### @keys with fuzzy parsing such as @s

Entry: ... @s
Prompt: starting date or datetime?
Help: currently: current expansion 
      help info

### @keys with & parts such as @r

Entry: ... @r
Prompt: repetition frequency?
Help: Possible entries are characters from: (y)early, ...

Entry: ... @r m
Prompt: repetition rule &key options?
Help: currently
      Enter & to see a list of available options

Entry: ... @r m &w

Entry: ... @j
Prompt: job summary?
Help: Enter the summary for the 


012345678901234567890123456789012345678901234567890123456789

# Defaults

When displaying an item in details view, any applicable defaults will be 
displayed in a *Defaults* section below the entry. 


## default calendar: for @c

When an item is created without an explicit entry for @c, this value is 
recorded in the database entry.

When editing such an item, the @c entry is not displayed unless the value 
of`default_calendar` has changed and no longer agrees with the recorded value 
of @c. 

When entering an explicit value for @c, tab completion will offer the value 
of`default_calendar` along with any other values of @c that have previously 
been used.

## calendar sets

Suppose I have calendars DAG and ERP. Then I could have calendar sets:

Dan: DAG
Ellen: ERP
Family: DAG, ERP

# Date & Time

    The string to be parsed will have the format 'datetime string' followed, 
    optionally by a comma and a tz specification. Return a date object if the 
    parsed datetime is exactly midnight. Otherwise return a naive datetime 
    object if tz == 'float' or an aware datetime object using tzlocal if tz is 
    None and otherwise using the proviced tz.

## Storage

Using date and datetime storage extensions in tinydb

class DatetimeCacheTable(SmartCacheTable):

    Use a readable, integer timestamp as the id - unique and stores the 
    creation datetime - instead of consecutive integers. E.g., the the id for 
    an item created 2016-06-24 08:14:11:601637 would be 20160624081411601637.

class PendulumDateTimeSerializer(Serializer):

    This class handles both aware and 'factory' pendulum objects. 

    Encoding: If obj.tzinfo.abbrev is '-00' (tz=Factory), it is interpreted as 
    naive, serialized without conversion and an 'N' is appended. Otherwise it 
    is interpreted as aware, converted to UTC and an 'A' is appended. 
    Decoding: If the serialization ends with 'A', the pendulum object is 
    treated as 'UTC' and converted to localtime. Otherwise, the object is 
    treated as 'Factory' and no conversion is performed. Note: 'A' datetimes
    are aware and 'N' datetimes are naive.

    This serialization discards both seconds and microseconds but preserves 
    hours and minutes.

class PendulumDateSerializer(Serializer):

    This class handles pendulum date objects.


class PendulumIntervalSerializer(Serializer):

    This class handles pendulum interval (timedelta) objects.


## Retrieval

Starting with the current local timezone, `ltz`

- items with float (naive dates and datetimes) are left unchanged
- integer timestamps are parsed and converted to `ltz` time
- items with != float are converted to `ltz` time

Week view rows are sorted and grouped by:

- (year, week_number)
- weekday_number (Monday = 0)
- sort type:
  - -1: all day events
  - HHMM: event, task or journal scheduled for HHMM
  - 2400: all day task
  - 2401: journal entry

# Types

## effort & reports

Maybe add an @key to tasks (events, notes?) 

  @x datetime timer stopped, time active, time paused

  timer
    - select item
    - begin timer (prompt for account)
      pause/restart/save or discard

      reports broken down by index

## `*` event

- date-only:
  - stored as naive, starting at midnight
  - sort: 0 (put these first in day, week and month (day) view)
  - display with type character '^'

- date-time:
  - with float: naive
  - otherwise: aware
  - busy time from @s to @s + @e
  - sort: HHMM (with timed items in week day and month day views)

## `-` task

- undated, no @s, @a, @b

- date-only:
  - stored as naive, starting at midnight
  - sort: 2400, after all timed items but before untimed journal entries

- datetime:
  - with float: naive
  - otherwise: aware, pastdue after midnight on the date of the starting datetime
  - @e optional extent (estimated time to complete) - default 0m
  - sort: HHMM (with other timed items in day)

- repeated tasks: only save last completion date?
- tasks can have @j job entries - equivalent to old group tasks
  - &s starting time - @s is required and provides default; saved as a timedelta relative to @s
  - &l location, @l provides default
  - &u unique identifier
  - &p list of immediate prerequisite unique ids

- display characters:
    - available
    # waiting
    x done

-  job display:
  task summary: job summary (m/n)

## `%` journal

- undated, no @s, @a, @b

- date-only: all-day, naive
  - sort: 2401 (after timed items in week and month day views)

- datetime:
  - without or with float: naive
  - otherwise: non-naive
  - sort: HHMM (with other timed items in week view)

- with @e: equivalent to old action
- without: equivalent to old note

## `?` someday maybe

- @s, @a, @b ignored

## `!` inbox

- @s, @a, @b ignored

# Views

## What's needed

### Issues

- Aware / Naive
	- TinyDB
		- Dates are naive
		- Datetimes can be naive or aware
	- period begin and end are aware local time


* views in which an item contributes a single row:
  * index
  * history-created
  * history-modified
  * index
  * someday

* views in which each instance contributes a single row
  * agenda
  * busy
  * done
  * month
  * next (tasks with jobs contribute one row for each job)

For single row views

    items: id -> | type | summary | c_dt | m_dt | index | 

Tag view
    tags: id -> | tags |

    rows = []
    for id in tags:
        for tag in tags[id]:
            row.append(stuff from items[id], tag)

Scheduled views (Agenda, Month)
    instances: id -> | datetimes |
    rows = []
    for id in instances:
        for dt in instances[id]:
            row.append(stuff from item[id], dt)



For tags
    id -> tags

For 

id -> [instances in beg-end interval]
only events and tasks repeat
for events instances correspond to datetimes in interval
for tasks instances correspond to history datetimes and unfinished instances in interval



views: view -> list of rows

views = {
  'weekly': weekview_rows,
  'index': index_row,
  'history_created': row,
  'history_modified': 
}

* A hash: id -> list of tuples where each tuple as a means for sorting, a path tuple to describe the path to the displayed node and a columns tuple to describe what is to be displayed in columns 1 and 2 for the node.

* In the etm-urwid each view was a list of lists with each list element = [sort_tuple, path_tuple, columns_tuple]

Methods

- Set/update header and footer
- Set view

- Home (spacebar)



## week and month views 

- Today
  ^ Occasion - if any
  ! Inbox - if any
  -/+ Pastdue - if any        days past due
  > Beginning soon - if any   days until beginning

  */- timed events, tasks and journal entries by starting time or Nothing Scheduled
    - always show Today and jump to this item on Show Today
    - Note Inbox, Pastdue and Soon only appear in Today 

  + Date only tasks - if any
  # Date only journal entries - if any

- Dates other than today
  ^ Occasion - if any

  */- timed events, tasks and journal entries by starting time, if any

  + Date only tasks - if any
  + Date only journal entries - if any

## Next View

undated tasks - grouped by location or None 


## Someday View

someday items

## Week View

### New 2018-07-25

- Period (using Pendulum >= 2.0.2) weeks in current month + weeks in 5 prior months + weeks in 12 subsequent months
  - begin: now.start_of('month').subtract(months=5).start_of('week')
  - end: now.start_of('month').add(months=12).add(weeks=5).end_of('week')

- Date range, **first** to **last** for dated items
  - Non repeating
    - first = @s
    - last = @s
  - Repeating
    - first = @s
    - last = last instance or None if repeating forever



- Period: year-weeks in current week + 12 weeks before + 39 weeks after
- Period: year-weeks in current week + 25 weeks before + 52 weeks after
- Period: year-weeks in current month + 5 months before + 12 months after 
- Dates and datetimes with float left as is; aware datetimes converted from 
  UTC to local time zone with the timezone information then removed.
- sort tuple: (year-week, weekday number, type)
- Each dated item stores *first* instance and *last* instance or, *none* for 
  repeated items without stopping dates.
- add_item(id):
  - for each instance of id in period:
    - add row to weeks[week_num]
    - add week_num to ids[id]
  - if *first* before period:
    - add id to before
  - if *last* is none or falls after period:
    - add id to after
- Startup:
  - for id in all items:
    - add(id)
- If we want a week before or after period, we need only process the before or 
  after ids.
- Remove item id:
  - for each week_num in ids[id]:
    - remove rows for id in weeks[week_num]
  - remove id, if necessary, from before and after
- Add item id:
  - execute steps for item above 
- Remove and then add when updating an item

### Keys

- Up/Down keys: previous/next day
- Left/Right keys: previous/next week
- Return: expand/collapse day/item


## Month View

    +----------------------------------------------------------+
    | August 2017                                              |
    +----------------------------------------------------------+
    |                                                          |
    |   Wk     Mo     Tu     We     Th     Fr     Su     Su    |
    |  ----+-------------------------------------------------  |
    |      |  ----                                             |
    |   31 |  |31|     1      2      3      4      5      6    |
    |      |  ----                                             |
    |      |                                                   |
    |   32 |    7      8      9     10     11     12     13    |
    |      |                                                   |
    |      |                                                   |
    |   33 |   14     15     16     17     18     19     20    |
    |      |                                                   |
    |      |                                                   |
    |   34 |   21     22     23     24    [25]    26     27    |
    |      |                                                   |
    |      |                                                   |
    |   35 |   28     29     30     31      1      2      3    |
    |      |                                                   |
    |      |                                                   |
    |   36 |    4      5      6      7      8      9     10    |
    |      |                                                   |
    |      |                                                   |
    |                                                          |
    |                                                          |
    |                                                          |
    +----------------------------------------------------------+
    | 2:54pm Wed Aug 23 EDT                                    |
    +----------------------------------------------------------+

## Busy View

    +----------------------------------------------------------+
    | Week 40: Mo Oct 2 - Sun Oct 8, 2017                      |
    +----------------------------------------------------------+
    |   Hr     Mo     Tu     We     Th     Fr     Sa     Su    |
    |  ----+-------------------------------------------------  |
    |  12a |                                                   |
    |      |                                                   |
    |      |                                                   |
    |      |                                                   |
    |      |                                                   |
    |      |                                                   |
    |   6a |                                                   |
    |      |                                                   |
    |      |   #             #             #      #            |
    |      |   #             #             #      #            |
    |      |           #                          #            |
    |      |           #            #             #     #      |
    |  12p |   #                    #             #     #      |
    |      |   #                    #             #     #      |
    |      |                                            #      |
    |      |                                            #      |
    |      |   #                                               |
    |      |   #                                               |
    |   6p |                 #                                 |
    |      |   #             #                                 |
    |      |   #             #                                 |
    |      |   #                                               |
    |      |                                                   |
    |      |                                                   |
    +----------------------------------------------------------+
    | 2:54pm Wed Aug 23 EDT                                    |
    +----------------------------------------------------------+


### Keys

- Up/Down keys: previous/next week (row)
- Left/Right keys: previous/next day (column)
- Shift Left/Right keys: previous/next month
- Return: show Week View for selected week


### Colors

Let E denote the total number of hours of extent scheduled for day

- blk:  E  =  0 (black)
- #00f: E <=  1 (dark blue)
- #60f: E <=  2
- #80f: E <=  3
- #a0f: E <=  4
- #d0f: E <=  5
- #f0f: E <=  6
- #f0d: E <=  7
- #f0a: E <=  8
- #f08: E <=  9
- #f06: E <= 10
- #f00: E >  10 (bright red)


## Index View

All items, grouped and sorted by `@i index` entries. Items without such 
entries are listed last under `none`.

## History View

All items by created datetime or by last modified datetime. Grouped by date 
and sorted by time in `local_timezone`. 


## Tag View


Items with `@t tag` entries sorted and grouped by tag.

## Details view

Details for the selected item. 

## Edit view

- Top bar: status

  - new item

    - new event

      - new event for Mon, Sep 4

        - new event for 9am, Mon Sep 4

          - new event for 9am-10:30am Mon, Sep 4

- Entry area where typing occurs

- Prompt, boxed area immediately below entry as in bpython-urwid

# @ and & Keys

    type_keys = {
        "*": "event",
        "-": "task",
        "#": "journal",
        "?": "someday",
        "!": "inbox",
    }

    at_keys = {
      '+': "include: list of date-times",
      '-': "exclude: list of date-times",
      'a': "alert: time-period: cmd, optional args*",
      'b': "beginby: integer number of days",
      'c': "calendar: string",
      'd': "description: string",
      'e': "extent: timeperiod",
      'f': "finish: datetime",
      'g': "goto: url or filepath",
      'i': "index: colon delimited string - basis for index view",
      'j': "job summary: string",
      'l': "location: string",
      'm': "memo: string",
      'o': "overdue: r)restart, s)kip or k)eep",
      'p': "priority: 1 (highest), ..., 9, 0 (lowest)",
      'r': "frequency: y, m, w, d, h, n, e",
      's': "start: date or date-time",
      't': "tags: list of strings",
      'v': "value: defaults key",
      'z': "timezone: string",
    }

    amp_keys = {
        'r': {
            'E': "easter: number of days before (-), on (0)\n      or after (+) Easter",
            'h': "hour: list of integers in 0 ... 23",
            'i': "interval: positive integer",
            'M': "month: list of integers in 1 ... 12",
            'm': "monthday: list of integers 1 ... 31",
            'n': "minute: list of integers in 0 ... 59",
            's': "set position: integer",
            't': "total number of repretitions: integer",
            'u': "until: datetime",
            'w': "weekday: list from SU, MO, ..., SA",
        },

        'j': {
            'a': "alert: timeperiod: command, args*",
            'b': "beginby: integer number of days",
            'd': "description: string",
            'e': "extent: timeperiod",
            'f': "finish: datetime",
            'l': "location: string",
            'p': "prerequisites: comma separated list of uids of immediate 
            prereqs",
            's': "start/due: timeperiod before task start",
            'u': "uid: unique identifier: integer or string",
        },
    }

# Key Bindings

## View Mode keys

      menu1 = [
          "-- VIEWS ------------------------------------------ ",
          "a: agenda        n: next           t: tags          ",
          "b: busy          s: someday        f: set filter    ",
          "d: done          i: index          l: set level     ",
          "m: month         h: history        c: set calendars ",
          ]

      menu2 = [
          "-- SELECTED ITEM ---------------------------------- ",
          "E: edit          R: reschedule     K: klone item    ",
          "D: delete        S: schedule new   T: start timer   ",
          "F: finish        O: open link      X: export ical   ",
          ]

      menu3 = [
          "-- TOOLS ------------------------------------------ ",
          "N: new item      Q: query          F2: date calc    ",
          "J: jump to date  C: copy view      F3: yearly       ",
          "A: alerts        P: preferences    F8: quit         ",
      ]
