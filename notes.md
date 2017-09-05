# etm-mvc


# TODO


# Defaults

When displaying an item in details view, any applicable defaults will be 
displayed in a *Defaults* section below the entry. 

## default timezone: for @z

When a value for @s includes a time as well as date and thus could be aware 
and no explicit entry has been given for @z, then this value will be used to 
convert the entry to UTC for the database entry. When only a date or `@z 
float` is entered, then the date/time is regarded as naive and stored in the 
database along with `@z float`.

When displaying datetimes that are aware, i.e., without an @z float entry, the 
datetime is interpreted as UTC and converted to a local time representation 
using the current `default_timezone`. Datetimes with @z float are interpreted 
as local times and are not converted. 

When editing such an item, the @z entry is not displayed unless the value is 
`float`.

When entering an explicit value for @z, tab completion will offer the value of 
default timezone,  other values of @z that have previously been used and 
`float`.


## default calendar: for @c

When an item is created without an explicit entry for @c, this value is 
recorded in the database entry.

When editing such an item, the @c entry is not displayed unless the value 
of`default_calendar` has changed and no longer agrees with the recorded value 
of @c. 

When entering an explicit value for @c, tab completion will offer the value 
of`default_calendar` along with any other values of @c that have previously 
been used.


# Date & Time

## Possibilities

Note for parsing datetime - make the default one second after midnight.

    parse_default = datetime.now().replace(hour=0, minute=0, second=1, 
    microsecond=0)

    def etm parse(s):
        res = parser.parse(s, default=parse_default)
        if (res.hour, res.minute, res.second, res.microsecond) == (0, 0, 1, 0):
            return res.date()
        else:
            return res

- No `@s` entry is provided: undated, only allowed for "-" items. `@z` not 
  allowed. 
- An entry for `@s` is provided
  - Either `@z` is not provided or `@z float` is provided
    - `@s` date-only (one second after midnight): naive, `@z float` recorded to database
    - `@s` date-time (not one second after midnight): aware with `default_timezone`
  - An entry for `@z` is provided with an actual timezone (not `float`)
    - `@s` date-only (one second after midnight): aware - midnight in provided timezone
    - `@s` date-time (not one second after midnight): aware - the specified time in the provided timezone

## Tab Completion for @z

- list of time zones for tab completion. The first item is treated as the 
  local timezone. 

When a date has been specified in @s, @z float becomes the implicit default. 
No @z entry is allowed.

When a time has been added, @z is allowed and the tab completion offers the 
list followed by float.


## Storage

- timestamps for creation and modification datetimes are integers representing 
  UTC datetimes
- date-only are stored as naive date objects with @z float
- date-times are stored as naive datetime objects
  - aware datetimes are first converted to UTC and then stored as naive 
    datetimes. The original timezone information is stored in @z.
  - naive datetimes are left unchanged with @z float
- repeating items
  - first = date or datetime (naive or UTC aware) of first instance
  - last
    - if finitely repeating: (&u or &t) date or datetime of last instance
    - otherwise: none

## Retrieval

Starting with the current local timezone, `ltz`

- items with @z float (naive dates and datetimes) are left unchanged
- integer timestamps are parsed and converted to `ltz` time
- items with @z != float are converted to `ltz` time

Week view rows are sorted and grouped by:

- (year, week_number)
- weekday_number (Monday = 0)
- sort type:
  - -1: all day events
  - HHMM: event, task or journal scheduled for HHMM
  - 2400: all day task
  - 2401: journal entry

# Types

## `*` event

- date-only:
  - all-day occasion, naive, no @a, @z or @e, not treated as busy time
  - sort: 0 (put these first in day in week view and month (day) view)
- date-time:
  - without @z or with @z float: naive
  - otherwise: non-naive
  - busy time from @s to @s + @e
  - sort: HHMM (with timed items in week and month day views)

## `-` task

- undated, no @s, @z, @a, @b
- date-only: all-day, naive - no @z, no @a, pastdue after date
  - sort: 2400 (after timed items in week and month day views)
- datetime:
  - without with @z float: naive
  - otherwise: non-naive, pastdue after datetime
  - @e optional extent (estimated time to complete) - default 0m
  - sort: HHMM (with other timed items in week view)
- repeated tasks: only save last completion date?
- tasks can have @j job entries - equivalent to old group tasks

## `#` journal

- @s required, date or datetime (naive or aware)
- with @e: equivalent to old action
- without: equivalent to old note
- sort:
  - datetime: HHMM
  - dateonly: 2401 (put these last in day)

## `?` someday maybe

## `!` inbox

# Views

## Agenda View

- Now: inbox or pastdue items - only if they exist
- Today: scheduled items or  "nothing scheduled"
- Tomorrow: scheduled items or "nothing scheduled"
- Soon: begin-by items - only if scheduled and don't appear in today or 
  tomorrow
- Next: undated tasks - only if they exist. Group by location
- Someday: someday items - only if they exist


## Week View

- Period: year-weeks in current week + 12 weeks before + 39 weeks after
- Dates and datetimes with @z float left as is; aware datetimes converted from 
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
    |      |                                                   |
    |   31 |   31      1      2      3      4      5      6    |
    |      |                                                   |
    |   32 |    7      8      9     10     11     12     13    |
    |      |                                                   |
    |   33 |   14     15     16     17     18     19     20    |
    |      |                                                   |
    |   34 |   21     22     23     24    [25]    26     27    |
    |      |                                                   |
    |   35 |   28     29     30     31      1      2      3    |
    |      |                                                   |
    |   36 |    4      5      6      7      8      9     10    |
    |      |                                                   |
    |                                                          |
    |  Fri Aug 25                                              |
    |  -----------                                             |
    |  items for Aug 25 or Nothing Scheduled                   |
    |                                                          |
    |                                                          |
    |                                                          |
    |                                                          |
    |                                                          |
    +----------------------------------------------------------+
    | 2:54pm Wed Aug 23 US/Eastern                             |
    +----------------------------------------------------------+


### Keys

- Up/Down keys: previous/next week (row)
- Left/Right keys: previous/next day (column)
- Shift Left/Right keys: previous/next month
- Return: show Week View for selected week

### Colors


Let E denote the total number of hours of extent scheduled for day

- black: E = 0
- #00f: E <= 1 (dark blue)
- #60f: E <= 2
- #80f: E <= 3
- #a0f: E <= 4
- #d0f: E <= 5
- #f0f: E <= 6
- #f0d: E <= 7
- #f0a: E <= 8
- #f08: E <= 9
- #f06: E <= 10
- #f00: E > 10 (bright red)


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
=============

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
      'q': "queue: date-time",
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

- `F1`: help
- `a`: agenda view
- `w`: week view
- `m`: month view
- `t`: tags view
- `i`: index view
- `h`: history view

- `n`: create new item
