# What's New

## Item Types

### `*`: event

- The *occasion* item type is eliminated. The functionality is replaced by 
  using a *date only* entry in an event.

### `-`: task

- The *task group* item type is eliminated. The functionality is replaced by 
  the ability to add job entries, `@j`, to any task.

### `%`: journal entry

- This replaces the old *note* item type.

### `?`: someday maybe

### `!`: inbox

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
      datetimes. E.g., `fri 2p` would be stored as
      `20180105T1900A` and `fri 2p, US/Pacific`
      would be stored as `20180105T2200A`. 

- Display:

    - Naive dates are displayed as is but without the midnight starting 
      time. All-day events (occasions) go first in the daily display and 
      all-day tasks and journal entries go last.

    - Naive datetimes are displayed as is, i.e., are interpreted as local 
      datetimes without conversion.

    - Aware datetimes are converted to the current local timezone.

## Actions

- The *action* item type is eliminated. The functionality is replaced and 
  enhanced by the ability to add an entry for `@m` (moment) to any item 
  including undated tasks.

- The format for the `@m` entry is `@m timestamp; active time period[; paused 
  timeperiod]`. The format for `timestamp` is the same as for `@s`. Items can 
  have one or more `@m` entries.

- The timer workflow:

    - Select the item to which the `@m` entry is to be appended.

    - Press the hot key to start the timer.

    - Press the hot key to pause/restart the timer as often as desired.

    - Press the hot key to finish and record the `@m` entry using the 
      timestamp at which the timer was finished and the accumulated time 
      periods during which the timer was active and paused. Note that the 
      starting time is approximately given by the timestamp minus the active 
      and paused periods which are rounded up to the nearest minute.

- Action reports can be broken down, e.g., by the month of the timestamp and 
  the index entry, `@i`, of the item. 


