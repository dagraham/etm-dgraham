# Tables


Tables are associated with views and thus should have all elements ready for 
presentation, e.g., datetimes in formatted as local timezone representations 
of the UTC times in the database.

All tables should be indexed by CID, the creation datetime uuid.

## Items


Used for history view

::

  CID: uuid index from creation datetime
  CLT: formatted local datetime representation of CID
  MLT: formatted local datetime representation of MID
  RLT: formatted local datetime representation of relevant datetime or null
  SUMMARY: summary entery
  ENTRY: string representation of entire entry for detail view
  CALENDAR: value of @c or default
  TIMEZONE: value of @z or default
  OTHER: expansion of @x value or null
    expansion is 'missing' if value not given in config)


## Dates


Used for week and month views

YearWeekDay
~~~~~~~~~~~

::

  YYYYWWD: year-week-day -> local timezone formatted representation
    day 0 (Mo) - 6 (Su), 7 (entire week)
  Examples:
    2017352 -> Wed Aug 30, 2017
    2017357 -> Week 35: Aug 28 - Sep 3, 2017 

::

  CID: uuid
  * The following are local time representations
  YEARWEEK: YYYYWK integer four digit year and two digit week number
  WEEKDAY: Integer week day number, with Monday == 0
  HOURMIN: HHMM integer 24 hour and minute representation
  DLT: formatted local time representation of date, e.g, Mon Aug 28
  TLT: formatted local time represntation of <D-w>time, e.g, 11:30am
