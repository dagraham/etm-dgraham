# etm-mvc

event summary:
* ev
------------------------------------------------------------
Enter the summary for the event followed, optionally, by
@key and value pairs


event @keys:
* ev @
------------------------------------------------------------
Required: @s
Allowed: @c, @d, @e, @g, @i, @l, @m, @s, @t, @v, @b, @r, @e,
@a, @+, @-


starting date or datetime?
* ev @s 2p fri
------------------------------------------------------------
starting: Fri Nov 17 2:00PM EST
The datetime entry for @s will be interpreted as an aware
datetime in the current local timezone. Append a comma and
then 'float' to make the datetime floating (naive) or a
specific timezone, e.g., 'US/Pacific', to use that timezone
instead of the local one.

extent (timeperiod)?
* ev @s fri 2p @e
------------------------------------------------------------
considering: ''

extent (timeperiod)?
* ev @s fri 2p @e 90m
------------------------------------------------------------
extent: 1 hour 30 minutes

index (colon delimited string)?
* ev @i plant:tree:oak
------------------------------------------------------------
index: level 0 -> plant, level 1 -> tree, level 2 -> oak


# TODO

note: !, # and ? cannot repeat

states

has item type

  *
    required: s
    available: undated

  - 
    available: s, f, j + undated

  #
    available: s + undated

  ?
    available: s + Undated

  !
    available: s + undated


  ...

has s and not in #, ?, !

  date: allowed b + r + undated
  datetime: date + a + e

has r

  allowed: +, - 



editing_at

012345678901234567890123456789012345678901234567890123456789
* summary @s fri 2p @e 90m @r m &w -1fr @z US/Pacific @d
          |         |      |            |             |
          10        20     27           40            54

Start
    ask: item type: * (event), - (task), ...?
        entry: *
            ask: event summary?
                entry: my event
                reply: list of required at_keys

event
    @s required
        date-only: no @z, @e, @a
        date-time:
            default @z localtz and aware
            requires @z float for naive

# States

- selecting item type
  - top: 'type char for new item?'
  - bot: list of type chars and descriptions

- entering summary
  - top: '<item type> summary: <current value of summary'
  - bot: 

- entered '@'
  - top: '@-key?'
  - bot: list of available @-keys and descriptions

- entered '@<key>'
  - top: '@<key> current expansion of the entry'
  - bot: explanation


Examples:

  entry: @s fri
  top: @s Fri Sep 22
  bot: An all-day, floating event for the specified date in whatever happens 
  to be the local timezone. 

  entry: @s fri 2p
  top: @s Fri Sep 22 2:00pm EDT
  bot: Without an entry for @z, the local timezone is used. Add '@z float' to 
  make the start time floating (naive) or, e.g., '@z US/Pacific' to specific 
  an explicit timezone.


errors?

complete?


    * 
        @s (starting date/time) is required for events

    - 
        @s (starting date/time) is optional for tasks. Tasks with @s entries 
        appear in agenda, week and month views. Tasks without @s entries appear 
        in next view


    * event
        *a aware datetime @s date + time w/o @z or with @z not float
            assumed until @s finished
        *d date-only  - @s date w/o time
            allowed
        *n naive datetune - @s date + time + @z float
            allowed

    - task
        -a aware datetime @s date + time w/o @z or with @z not float
            assumed until @s finished
        -d date-only  - @s date w/o time
            allowed
        -n naive datetune - @s date + time + @z float
            allowed
        -u undated - no @s






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

## `^` occasion

- date-only - time ignored:
  - stored as naive, starting at midnight without @e
  - sort: 0 (put these first in day, week and month (day) view)

## `*` event

- date-time:
  - with float: naive
  - otherwise: aware
  - busy time from @s to @s + @e
  - sort: HHMM (with timed items in week day and month day views)

## `-` task

- undated, no @s, @a, @b
- datetime:
  - with float: naive
  - otherwise: aware, pastdue after midnight on the date of the starting datetime
  - @e optional extent (estimated time to complete) - default 0m
  - sort: HHMM (with other timed items in day)
- repeated tasks: only save last completion date?
- tasks can have @j job entries - equivalent to old group tasks
  - &s starting time - @s is required and provides default; saved as a timedelta relative to @s
  - &l location, @l provides default
  - &i unique id
  - &p list of immediate prerequisite unique ids

## `#` journal

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

## today (all day views)

Today - Fri Dec 29
  ^ Occasion - if any
  ! Inbox - if any
  -/+ Pastdue - if any        days past due
  > Beginning soon - if any   days until beginning
  */- timed events, tasks and journal entries by starting time
  + Date only tasks - if any

## Agenda View

- Inbox: inbox items - only if they exist
- Now: pastdue items - only if they exist
- Soon: beginning soon items - only if they exist
- Day 1 Today: scheduled items or  "nothing scheduled"
- Day 2 Tomorrow if there are scheduled items
- ditto for Day 3 ... Day n

If inbox, now, or soon, display "A" highlighted in status bar

## Next View

undated tasks - grouped by location or None 


## Someday View

someday items


## Week View

- Period: year-weeks in current week + 12 weeks before + 39 weeks after
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

## Busy View

    +----------------------------------------------------------+
    | Week 40: Mo Oct 2 - Sun Oct 8, 2017                      |
    +----------------------------------------------------------+
    |   Hr     Mo     Tu     We     Th     Fr     Su     Su    |
    |  ----+-------------------------------------------------  |
    |  12a |                                                   |
    |      |                                                   |
    |      |                                                   |
    |      |                                                   |
    |      |                                                   |
    |      |                                                   |
    |   6a |                                                   |
    |      |                                                   |
    |      |   #                                               |
    |      |   #                                               |
    |      |                                                   |
    |      |                                                   |
    |  12p |   #                                               |
    |      |   #                                               |
    |      |                                                   |
    |      |                                                   |
    |      |   #                                               |
    |      |   #                                               |
    |   6p |                                                   |
    |      |   #                                               |
    |      |   #                                               |
    |      |   #                                               |
    |      |                                                   |
    |      |                                                   |
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

- `F1`: help
- `a`: agenda view
- `w`: week view
- `m`: month view
- `t`: tags view
- `i`: index view
- `h`: history view

- `n`: create new item
