# What's New

## Item Types

### `*`: event

- The *occasion* item type is eliminated. The functionality is replaced by 
  using a *date only* entry in an event.

### `-`: task

- The *task group* item type is eliminated. The functionality is replaced by 
  the ability to add job entries, `@j`, to any task.

- The old *context* for tasks has been merged into *location*, `@l`. 

### `%`: journal entry

- This replaces the old *note* item type.

### `?`: someday maybe

### `!`: inbox 

## Data Storage

- All etm data is stored in a single, *json* file using the python data store 
  *TinyDB*. This file is a human-readable, but not necessarily editable, plain 
  text file that can be backed up and/or examined using external tools as well 
  as etm itself.

- Two timestamps are automatically created for each item in the data store, 
  one corresponding to the moment the item was created and the other to the 
  moment the item was last modified. A new *timestamp view* in etm allows 
  sorting by either timestamp. The default is oldest first for created 
  timestamps and newest first for last modified timestamps. Note that all 
  items appear in this view since all items have these two timestamps. 

- The heirarchial organization that was provided by file paths is provided by 
  the *index* entry. `@i`, which takes a colon delimited string. E.g., the 
  entry `@i plant:tree:oak` would store the item in the index view under:
      - plant
          - tree
              - oak

- The organization that was provided by calendars is provided by the 
  *calendar* entry, `@c`. A default value for calendar specified in 
  preferences is assigned to an item when an explicit value is not provided. 
  E.g., my default calendar is `dag`. I also use `erp` for my wife and `joint` 
  for items we share.

- Note that reorganization require only changing an `@i` or an `@c` entry and 
  not moving files and directories.

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

- Storage format: `YYYYMMDDTHHMM(N|A)`

    - Naive dates are stored as naive datetimes that begin at midnight on the 
      relevant date. E.g., `@s fri` would be stored as `20180105T0000N`.

    - Naive datetimes are stored as is. E.g., `fri 2p, float` would be stored 
      as `20180105T1400N`.

    - Aware datetimes are first converted to UTC and then stored as aware 
      datetimes. E.g., when the current timezone is US/Eastern,<t_úX> `fri 
      2p` would be stored as `20180105T1900A` and `fri 2p, US/Pacific` would 
      be stored as `20180105T2200A`. 

- Display:

    - Naive dates are displayed as is but without the midnight starting time. 
      All-day events (occasions) go first in the daily display before all the 
      datetime items and and all-day tasks and journal entries go last.

    - Naive datetimes are displayed as is, i.e., are interpreted as local 
      datetimes without conversion.

    - Aware datetimes are converted to the current local timezone. E.g., in 
      the US/Eastern timezone, `fri 2p` would display as beginning at 2pm on 
      Jan 5 if the computer is still in the Eastern timezone but would display 
      as starting at 11am if the computer had been moved to the Pacific 
      timezone. Similarly, `fri 2p, US/Pacific` would display as starting at 
      5pm if the computer were in the Eastern timezone.

## Actions

- The *action* item type is eliminated. The functionality is replaced and 
  enhanced by the ability to add an entry for `@m` (moment) to any item 
  including undated tasks and an entry for `&m` to any task job entry, `@j`. 

- The format for both `@m` and `&m` entries is a comma separated list of
  `@m timestamp; active time period[; paused timeperiod]` tuples. The format 
  for `timestamp` is the same as for `@s`. 

- The timer workflow:

    - Select the item to which the `@m` entry is to be appended.

    - Press the hot key to start the timer.

    - Press the hot key to pause/restart the timer as often as desired.

    - Press the hot key to finish and record the `@m` entry using the 
      timestamp at which the timer was finished and the accumulated time 
      periods during which the timer was active and paused. Note that the 
      starting time is approximately given by the timestamp minus the active 
      and paused periods which are rounded up to the nearest minute.

- One or more timers can be active at the same time but only one can be 
  running - the rest will be paused.

- Action reports can be broken down, e.g., by the month of the timestamp and 
  the index entry, `@i`, of the item. Note that each `@m` entry in an item 
  *inherits* all of the other attributes of the item as well.

## Jobs and Prerequisites

- Tasks, both with and without `@s` entries can have component job entries, 
  `@j`.  A task with jobs thus replaces the old task group.

- For tasks with an `@s` entry jobs can, optionally, have an `&s` entry to set 
  the due date/datetime for the job. It can be entered as a timeperiod 
  relative to (+ before or - after) the starting datetime for the task or as 
  date/datetime. In either case, the value of `&e` is stored as a relative 
  timeperiod.

- Job prerequisites, by default, are determined automatically by the order in 
  which jobs are listed. E.g., with

  ```- sequential jobs
       @j job A
       @j job B
       @j job C
  ```

  `job A` has no prerequisites itself but is a prerequisite for both
  `job B` and `job C`. Similarly, `job B` is a prerequisite for `job C`.
