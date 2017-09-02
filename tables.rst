Tables
********

All
====

Used for history view

::

  CID: uuid from creation time
  MID: last modified time stamp
  CLT: formatted local time representation of CID
  MLT: formatted local time representation of MID
  RLT: formatted local time representation of relevant time or null
  SUMMARY: summary entery
  ENTRY: string representation of entire entry
  CALENDAR: value of @c or default
  TIMEZONE: value of @z or default
  OTHER: expansion of @x value or null
    expansion is 'missing' if value not given in config)


Dates
=====

Used for week and month views

YearWeek
~~~~~~~~~

::

  YEARWEEKDAY: YYYYWWD integer four digit year, two digit week number, e.g.,
    201735
  WLT: formatted local time representation of week, .e.g,
    Week 35: Aug 28 - Sep 3, 2017 


::

  CID: uuid
  * The following are local time representations
  YEARWEEK: YYYYWK integer four digit year and two digit week number
  WEEKDAY: Integer week day number, with Monday == 0
  HOURMIN: HHMM integer 24 hour and minute representation
  DLT: formatted local time representation of date, e.g, Mon Aug 28
  TLT: formatted local time represntation of time, e.g, 11:30
