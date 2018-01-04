# What's New

## Item Types

### `*`: event

### `-`: task

### `%`: journal entry

### `?`: someday maybe

### `!`: inbox

## Dates and Date Times

- The time zone key, `@z`, is eliminated. 

- The format for the `@s` entry is `date [time][, TimeZone|float]`. Dates 
  (naive) and datetimes (both naive and aware) are suppored. In the following 
  entries for `@s` suppose that it is currently Wed, Jan 4, 2018 and that the 
  local timezone is US/Eastern.

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





