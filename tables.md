<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Tables](#tables)
  - [Items](#items)
  - [Dates](#dates)
    - [YearWeekDay lookup](#yearweekday-lookup)
    - [tinydb storage for `@s` and `@z`](#tinydb-storage-for-s-and-z)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Tables


Tables are associated with views and thus should have all elements ready for 
presentation, e.g., datetimes in formatted as local timezone representations 
of the UTC times in the database.

All tables should be indexed by CID, the creation datetime uuid.

## Items


Used for history view

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

### YearWeekDay lookup

    YYYYWWD: year-week-day -> local timezone formatted representation
      day 0 (Mo) - 6 (Su), 7 (entire week)
    Examples:
      2017352 -> Wed Aug 30, 2017
      2017357 -> Week 35: Aug 28 - Sep 3, 2017 

### tinydb storage for `@s` and `@z`


- date-only: `s: date`; `z: Null`
- date-time naive: `s: date-time`; `z: Null`
- date-time aware:`s: date-time`; `z: 'US/Eastern'` 
