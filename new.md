# Data

## Item Types

Six item types are used: `*`, `-`, `~`, `%`, `?`  and `!`.

### `*`: event

- The old `^`, *occasion*,  item type is eliminated. The functionality is 
  replaced by using a *date* entry rather than a *datetime* in an event. See 
  *Dates and Date Times* below.

- Stored as an *event* when exporting to *ical*.

### `-`: task

- The optional `@s` entry records the datetime at which the task is due or 
  should be completed. Tasks with an `@s` entry are regarded as pastdue after 
  this datetime. Tasks without an `@s` entry are to be completed when possible 
  and are regarded as *next* items in the *Getting Things Done* method. A 
  special *next* view is devoted to these tasks where they are organized by 
  their `@l`, *location*, entries.

- The old `+`, *task group*, item type is eliminated. The functionality is 
  replaced by the ability to add job entries, `@j`, to any task.

- The old `%`, *delegated*, item type is eliminated. 

- The old `@c`, *context*, for tasks has been merged into *location*, `@l`. 
  The `@c` entry is now used to denote the *calendar* to which the item 
  belongs.

- Stored as a *todo* when exporting to *ical*.

### `~`: action

- The `@s` entry records the datetime at which the action was *finished*.

- The `@m`, *moment*, entry (actions only) has the format `active timeperiod[, 
  paused timeperiod]`. This entry records the time spent working on the action 
  and, optionally, the time period that work on the action was 
  suspended/paused.

- Using an etm *timer* to record an action entry:

    - Select the item or job to which the action is to be applied.

    - Press the start key to start the timer.

    - Press the pause/restart key as often as desired.

    - Press the finish key to finish and record the action entry.

      - The `@s` entry will record the moment at which the timer was finished.

      - The `@m` entry will record the accumulated time periods during which 
        the timer was active and paused.

      - The summary and `@i`, index, entries for the action will be those of 
        the selected item. 

- One or more timers can be active at the same time but only one can be 
  running - the rest will be paused.

- A special *actions* view displays action totals grouped by month and 
  organized by their index entries. This view is intended to provide a 
  conventient summary and could be used for time billing. Totals are obtained 
  by rounding up individual action totals using a configuration setting, e.g., 
  the nearest 1/4 hour before aggregating.

- Stored as a *journal* entry when exporting to *ical*.

### `%`: journal entry

- This is equivalent to the old *note* item type. 

- Stored as a *journal* entry when exporting to *ical*.

### `?`: someday maybe

- Unchanged. 

- Stored as a *journal* entry when exporting to *ical*.

### `!`: inbox

- Unchanged but for the change in the type character from `$` to `!`.

- Stored as a *journal* entry when exporting to *ical*.

## Storage

- All etm data is stored in a single, *json* file using the python data store 
  *TinyDB*. This is a plain text file that is human-readable, but not 
  human-editable.  It can be backed up and/or queried using external tools as 
  well as etm itself.

- Two timestamps are automatically created for each item in the data store, one corresponding to the moment (microsecond) the item was created and the other to the moment the item was last modified. A new *all* view in etm  displays all items and allows sorting by either timestamp. The default is to show oldest first for created timestamps and newest first for last modified timestamps. The creation timestamp is used as the unique identifier for the item in the data store.


- The heirarchial organization that was provided by file paths is provided by 
  the *index* entry, `@i`, which takes a colon delimited string. E.g., the 
  entry `@i plant:tree:oak` would store the item in the *index* view under:
      - plant
          - tree
              - oak

  The default for `@i` is *None*. Note that `@i` replaces the functionality of  the old `@k`, *keyword*.

- The organization that was provided by calendars is provided by the 
  *calendar* entry, `@c`. A default value for calendar specified in 
  preferences is assigned to an item when an explicit value is not provided. 

- Note that reorganization requires only changing an `@i` or an `@c` entry and 
  not moving files and directories. Further, *TinyDB* permits database queries 
  that would, e.g., allow changing all `@i plant:tree:oak` entries to `@i 
  plant:tree:maple`.

## Dates and Date Times

- The time zone entry, `@z`, is eliminated. 

- Dates (naive) and datetimes (both naive and aware) are suppored. 

- The format for the `@s` entry is `date [time][, TimeZone|float]`. In the 
  following entries for `@s` suppose that it is currently Wed, Jan 4, 2018 and 
  that the local timezone is US/Eastern.

    - Naive date, e.g., `@s fri`.  Interpreted as `Fri, Jan 5, 2018`. Without 
      a time, this schedules an all-day, floating (naive) item for the 
      specified date in whatever happens to be the local timezone.

    - Aware date-time, e.g, `@s fri 2p`. Interpreted as `Fri, Jan 5, 2018 2pm 
      EST`. With a time, this schedules an item starting at the specified 
      date-time in the current timezone (US/Eastern).

    - Aware date-time, e.g., `@s fri 2p, US/Pacific`. Interpreted as `Fri, Jan 
      5 2018 5pm EST`. Note that 2pm PST is equivalent to 5pm EST.

    - Naive date-time, e.g., `@s fri 2p, float`. Interpreted as `Fri, Jan 5, 
      1018 2pm` in whatever happens to be the local time zone.

- Storage format: `YYYYMMDDTHHMM(N|A)` where `N` is naive and `A` is aware

    - Naive dates are stored as naive datetimes that begin at midnight on the 
      relevant date. E.g., `@s fri` would be stored as `20180105T0000N`.

    - Naive datetimes are stored as is. E.g., `fri 2p, float` would be stored 
      as `20180105T1400N`.

    - Aware datetimes are first converted to UTC and then stored as aware 
      datetimes. E.g., when the current timezone is US/Eastern, `fri 2p` would 
      be stored as `20180105T1900A` and `fri 2p, US/Pacific` would be stored 
      as `20180105T2200A`. 

    - The creation and last-modified timestamps are aware, UTC datetimes. 
      E.g., the the id for an item created  `2016-06-24 08:14:11:601637 UTC` 
      would be `20160624081411601637`. 

- Display:

    - Naive dates are displayed without conversion and without the midnight 
      starting time. All-day events (occasions) go first in the daily display 
      before all the datetime items and all-day tasks and journal entries go 
      last.

    - Naive datetimes are displayed without conversion, i.e., are interpreted 
      as local datetimes without conversion.

    - Aware datetimes are converted to the current local timezone. E.g., in 
      the US/Eastern timezone, `fri 2p` would display as beginning at 2pm on 
      Jan 5 if the computer is still in the Eastern timezone but would display 
      as starting at 11am if the computer had been moved to the Pacific 
      timezone. Similarly, `fri 2p, US/Pacific` would display as starting at 
      5pm if the computer were in the Eastern timezone.

    - Timestamps are converted to the local timezone and then rounded to the 
      nearest minute for display.

## Jobs

- Tasks, both with and without `@s` entries can have component job entries, 
  `@j`.  A task with jobs thus replaces the old task group.

- For tasks with an `@s` entry, jobs can have an `&s` entry to set the due 
  date/datetime for the job. It can be entered as a timeperiod relative to  
  the starting datetime (+ before or - after) for the task or as 
  date/datetime. However entered, the value of `&s` is stored as a relative 
  timeperiod with zero minutes as the default.

- For tasks with an `@s` entry, jobs can also have `&a`, alert, and `&b` begin 
  notices. The entry for `&a` is given as a time period relative to `&s` (+ 
  before or - after) and the entry for `&b` is a positive integer number of 
  days before the starting date/time to begin displaying "beginning soon" 
  notices. Entries for `@a` and `@b` in the task become the defaults for `&a` 
  and `&b`, respectively.

- Job prerequisites, by default, are determined automatically by the order in 
  which jobs are listed. E.g., with

          - automatically assigned prerequites
              @j job A
              @j job B
              @j job C

    `job A` has no prerequisites but is a prerequisite for `job B`. Similarly, `job B` is a prerequisite for `job C`. I.e., the default is to suppose that jobs must be completed sequentially in the order in which they are listed.

    Alternatively, job prequisites can be assigned manually using entries for 
    `&i` (id) and `&p`, (comma separated list of ids of immediate 
    prequisites). E.g., with

          - manually assigned prerequistes
            @j job a &i a
            @j job b &i b
            @j job c &i 3 &p a, b

    Neither `job a` nor `job b` has any prerequisites but both `job a` and `job b` are prerequistes for `job c`. Note that the order in which the jobs are listed is ignored in this case. 

- Tasks with jobs are displayed by job using a combination of the task and job 
  summaries with a type character indicating the status of the job. E.g.,

          x manually assigned prerequisites: job a
          - manually assigned prerequisites: job b
          + manually assigned prerequisites: job c

  would indicate that job a has been completed, job b is available (has no 
  unfinished prerequistites) and that job c is waiting (has unfinished 
  prerequisties). 

# Views

## Day View

- Scheduled items grouped by week.

- Top title bar shows selected week, e.g.,

        Week 2: Jan 8 - 14, 2018                            F1:Help

- Bottom status bar shows current time, next alarm and the number of remaining 
  alarms:

        8:49am Thu Jan 11                                 10:30am+2

- Main panel shows scheduled items grouped by date, e.g., 

        - Mon Jan 8
          ...
        - Tue Jan 9
          ...
        - Wed Jan 10 - Yesterday
          ...
        - Thu Jan 11 - Today
          ...
        - Fri Jan 12 - Tomorrow
          ...
        - Sat Jan 13
          ...
        - Sun Jan 14
          ...

- A listing for the current date is always displayed. If nothing is scheduled, 
  then 'Nothing scheduled' is displayed. Otherwise, starting from the top, the 
  display includes the following:

    - All day events (occasions), if any, using the display character `^`

    - Inbox entries, if any

    - Pastdue tasks, if any, with the number of days that have passed since 
      the task was due

    - Beginning soon notices, if any, with the number of days remaining until 
      the starting date of the item using the display character `>`

    - Scheduled events, journal entries, actions and unfinished tasks for 
      today sorted by starting time with the starting time and, for events,  
      the ending time. Tasks completed today are sorted by the completion 
      time.

    - Unfinished all day tasks, if any

    - All day journal entries, if any

    Note that the listing for *today* replaces the old *agenda* view.

- For dates other than *today*, the date is only displayed in the list for the 
  week if there are scheduled items. When there are, starting from the top, 
  the display includes the following:

    - All day events (occasions), if any, using the display character `^`

    - Scheduled events, journal entries, actions and unfinished tasks sorted 
      by starting time with the starting time and, for events, the ending 
      time. Tasks completed on the date are sorted by the completion time.

    - Unfinished, all day tasks, if any

    - All day journal entries, if any

- Weeks are displayed sequentially. If there is nothing to display for the 
  week, then the main panel of the display would show "Nothing scheduled". 
  E.g, 

        Week 3: Jan 15 - 21, 2018                           F1:Help
          Nothing scheduled

  For the current week, the display would show "Nothing scheduled" under the 
  current date. E.g.,

        Week 2: Jan 8 - 14, 2018                            F1:Help
        - Thu Jan 11 - Today
          Nothing scheduled

## Next View

- Unfinished tasks without due datetimes grouped and sorted by *location* 
  and/or *priority*

- Note that finished tasks are displayed in *Day View* using the completion 
  datetime.

## Someday View

- Someday items grouped and sorted by creation datetime

## Tag View

- Tagged items grouped and sorted by tag

## Index View

- All items, grouped and sorted by *index*

## History View

- All items, grouped and sorted by the datetime created (oldest first) or the 
  datetime last modified (newest first)

## Finished View

- Finished tasks grouped and sorted by the completed datetime. Now is the time 
  for 

## Action View

- Actions grouped, sorted and aggregated by month and index. E.g., supposing 
  that indices have the format `client:project:action`, then the display for a 
  month might appear as follows:

        January, 2018
           6.5h) Client A
              2h) Project 1
                 2h) Action a
              4.5h) Project 2
                 1.5h) Action b
                 3h) Action c
           9h) Client B
              ...
