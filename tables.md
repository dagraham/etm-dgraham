# Tables


Tables are associated with views and thus should have all elements ready for 
presentation, e.g., datetimes in formatted as local timezone representations 
of the UTC times in the database.

All tables should be indexed by CID, the creation datetime uuid.

## Items

items (every item has these)
  *item_id:     item.eid (int)  
  type:    item['itemtype'] in '*', '-', '%', '?', '!'
  summary: item['summary'] (string)
  calendar: item['calendar'] (string) 
  cdt:     item.eid truncated after minutes (datetime) 
  mdt:     item['modified'] (datetime)


Week and Month
scheduled
  *start_dt:     @s/@z date or datetime
  item_id: REFERENCES items

finished
  *finished_dt:     @s/@z date or datetime
  item_id: REFERENCES items

pastdue
  *due_dt:
  item_id: REFERENCES items

  query: if due_dt < today: show (today - due_dt).days 

beginning
  *starting_dt:
  *begin_dt: 
  item_id: REFERENCES items

  query: if begin_dt <= today: show (starting_dt - today).days


indices: (one item to )
  *index_id:
  index_name: colon delimited string
  item_id: REFERENCES items

tags 
  *tag_id: 
  *tag_name:

item_tags (many to many bridge)
  item_id: REFERENCES items
  tag_id:  REFERENCES tags


item


THINK ABOUT VIEWS!!!






















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
