# What's New

## Item Types

Only 6 item types are used: `*`, `-`, `~`, `%`, `?`  and `!`.

### `*`: event

- The old `^`, *occasion*,  item type is eliminated. The functionality is 
  replaced by using a *date* entry rather than a *datetime* in an event. See 
  *Dates and Date Times* below.

- Stored as an *event* when exporting to *ical*.

### `-`: task

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

### `%`: journal entry

- This replaces the old *note* item type. 

- Stored as a *journal* entry when exporting to *ical*.

### `?`: someday maybe

- Unchanged. 

- Stored as a *journal* entry when exporting to *ical*.

### `!`: inbox

- Unchanged but for the change in the type character from `$` to `!`.

- Stored as a *journal* entry when exporting to *ical*.

## Data Storage

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
      datetimes. E.g., when the current timezone is US/Eastern,<t_�X> `fri 
      2p` would be stored as `20180105T1900A` and `fri 2p, US/Pacific` would 
      be stored as `20180105T2200A`. 

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

## Actions

- The old `~`, *action*,  item type is eliminated. The functionality is 
  replaced and enhanced by the ability to add one or more entries for `@m` 
  (moment) to any item including undated tasks and one or more entries for 
  `&m` to any task job entry, `@j`. 

- The format for both `@m` and `&m` entries is `(@|&)m datetime, active time 
  period[, paused timeperiod]`. 

- Using an etm *timer* to record an moment entry:

    - Select the item or job to which the moment entry is to be appended.

    - Press the start key to start the timer.

    - Press the pause/restart key as often as desired.

    - Press the finish key to finish and record the moment entry using the 
      datetime at which the timer was finished and the accumulated time 
      periods during which the timer was active and paused. 

- One or more timers can be active at the same time but only one can be 
  running - the rest will be paused.

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

  `job A` has no prerequisites but is a prerequisite for `job B`. Similarly, 
  `job B` is a prerequisite for `job C`. I.e., the default is to suppose that 
  jobs must be completed sequentially in the order in which they are listed.

  Alternatively, job prequisites can be assigned manually using entries for 
  `&i` (id) and `&p`, (comma separated list of ids of immediate prequisites). 
  E.g., with

          - manually assigned prerequistes
            @j job a &i a
            @j job b &i b
            @j job c &i 3 &p a, b

  Neither `job a` nor `job b` has any prerequisites but both `job a` and
  `job b` are prerequistes for `job c`. Note that the order in which the jobs 
  are listed is ignored in this case. 

- Tasks with jobs are displayed by job using a combination of the task and job 
  summaries with a type character indicating the status of the job. E.g.,

          x manually assigned prerequisites: job a
          - manually assigned prerequisites: job b
          + manually assigned prerequisites: job c

  would indicate that job a has been completed, job b is available (has no 
  unfinished prerequistites) and that job c is waiting (has unfinished 
  prerequisties). 

## Day View

- Scheduled items grouped by week.

- Title bar shows selected week, e.g.,

        Week 2: Jan 8 - 14, 2018

- Main panel shows scheduled items grouped by date, e.g., 

        Week 2: Jan 8 - 14, 2018
        □ Today - Mon Jan 8
          * Safety Meeting                             3:30pm-5pm
          - trash and recycle                              7am
        □ Tomorrow - Tue Jan 9
          * French night                                7pm-10pm
          - pick up overalls
          - email Drew                                     2pm
        □ Wed Jan 10
          * Dinner at Carolina Club                   6:30pm-9:30pm
        □ Thu Jan 11
          * Air duct cleaning                           9am-12pm
          * Bruce Buley                                 11am-1pm
          * Dinner at Squires                            6pm-9pm
        □ Fri Jan 12
          * Tennis                                     9:30am-11am

         2:49pm Mon Jan 08                                 5:30pm+2

- The old *agenda* view has been eliminated. It's functionality has been 
  incorportated into the day views when viewing the current date.


