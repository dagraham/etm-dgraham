# Notes for etm
**Last modified: Sun Feb 10, 2019 08:39AM EST**

# TOC
<!-- vim-markdown-toc GFM -->

* [ToDo](#todo)
    * [Coding](#coding)
    * [Writing](#writing)
    * [States and Transitions](#states-and-transitions)
* [MVC](#mvc)
    * [Model](#model)
        * [Data Store](#data-store)
        * [Supporting queries](#supporting-queries)
        * [Items Tables](#items-tables)
        * [Instances Table](#instances-table)
        * [Item Views](#item-views)
        * [Instance Views](#instance-views)
        * [CRUD](#crud)
        * [API](#api)

<!-- vim-markdown-toc -->

# ToDo

## Coding

* Foundation
    * Incorporate RDict and use for index view
    * View class for view_pt
    * Logging
    * Timing
* To use
    * Create new item
    * Edit exiting item
        * Which instance dialog
    * Finish
    * Alarms
* Whenever
    * Tools
        * Schedule new
        * Reschedule
    * Views
        * index
        * next 
        * tags
        * Query

## Writing

* README -> Getting Started

## States and Transitions

* items (agenda - other views similar but without busy toggle)
    * selection -> (a:busy, enter:details, e:edit, f1:help)
    * no selection -> f1:help

* busy -> a:items 

* help -> f1:items

* details -> (e:edit, enter:items, f1:help)

* edit selected
    * repeating
        * yes -> which
            * instances chosen -> editing
            * cancel -> items
        * no -> editing
* editing
    * check -> editing
    * save -> items
    * cancel -> items

# [MVC](#toc)

Smart **Models**, dumb **Views** and thin **Controllers**!

## [Model](#toc)

See [TinyDB](#tinydb) for details about the data store. The Model handles CRUD (create, read, update and delete) operations on the data store as well as preparing data output in useful formats for views. 

There are two basic types of views: items and instances. The distinction arises because repeating items have more than one instance associated with each item - one for each datetime on which the item repeats. Views such as Agenda View show each of these instances on the date and time at which the item repeats. On the other hand, item views show the item itself rather than the instances. History View, for example shows each item along with the datetimes it was created and last modified. 

To support views, the model is responsible for maintaining two tables with data relevant to items and to instances. Both tables store the unique id of the relevant item on each row along with data relevant to the item or instance. When an item is updated, only the relevant rows of these tables need to be changed.

### [Data Store](#toc)  

TinyDB json file: hash uid -> all item details.

Supporting instances

    # no error checking for data store items 
    id2rset = {}
    for item in items:
        if 's' not in item:
            continue
        # we have a starting time
        dtstart = item['s']           # This will be local time
        doc_id = item.doc_id
        rset = dateutil.rrule.rruleset()
        id2rset[doc_id] = rset
        if 'r' in item:
            # rrule repeating 
            lofh = item['r'] 
            for hsh in lofh:
                freq, kwd = rrule_args(hsh)
                # if there is an &u in here it will be local time, e.g.
                # (2, {'interval': 2, 'until': DateTime(2018, 4, 1, 8, 0,
                #  0, tzinfo=Timezone('US/Eastern'))})
                kwd['dtstart'] = dtstart
                rset.rrule(rrule(freq, **kwd))
        # assuming @+ and @- contain no common elements
        if '+' in item:
            if 'r' not in item:
                # simple repetion
                rset.rdate(dtstart)   # This will be local time
            for dt in item['+']:
                rset.rdate(dt)        # These will be local time
        if '-' in item:
            for dt in item['-']:
                rset.exdate(dt)       # These will be local time

Using

    # by year, week and week day
    instances = []
    for id in id2rset:
        item_dts = id2rset[id].between(aft, bef, include=True)
        for dt in item_dts:
            bisect.insort(instances, [dt.isocalendar(), id])






### [Supporting queries](#toc)

    db = TinyDB(database, default_table='items')
    Item = Query()

items = db.search(Item.rrulestr.exists() & ~ Item.f.exists())



- for today
    - tdy_beg and tdy_end

    - uid -> 
        - reldt (relevant datetime for uid - updated daily)

            items = db.search(Item.s.exists ! Item.f.exists()
            reldt = {}
            for item in items:
                if 'f' in item:
                    reldt[item.doc_id] = item['f']
                elif 'r' in item:

            items = db.search(Item.s.exists()  & ~ Item.f.exists())

    for item in items
        - pastdue: uid.itemtype == task and reldt < tdy_beg 
        - beginning soon: uid has beginby and tdy_end < reldt <= tdy_end + beginby * oneday
        - alerts: [(time, cmd) for (times, cmd) in alerts for time in times if tdy_beg <= reldt - time <= tdy_end]

    - inbox: [list of uids of inbox items]
    - beginbys: [list of uids with beg and tdy < reldt and reldt <= tdy + beg]
    - pastdues: [list of uids of unfinished tasks with reldt < tdy]


### [Items Tables](#toc)

on demand created by query for requested view 

- index
    - index path
    - typecode
    - summary
    - relevant datetime
    - uid
- tags
    - tag
    - typecode
    - summary
    - relevant datetime
    - uid
- location
    - location
    - typecode
    - summary
    - relevant datetime
    - uid
- created
    - created
    - typecode
    - summary
    - relevant datetime
    - uid
- modified
    - modified
    - typecode
    - summary
    - relevant datetime
    - uid


### [Instances Table](#toc)

- columns: 
    - year.week.weekday path
    - typecode 
    - summary
    - start time, end time, interval
    - start minutes, end minutes, total minutes 
    - calendar 
    - index path
    - tags tuple 
    - uid
- update uid: remove all rows matching uid and insert new rows for the updated uid.

Note: use SList from rdict.py for tables.

The model is also responsible for maintaining a reference hash containing the relevant locale representations of dates for use in view headers.

- Dates hash: (year, week) ->
    0. locale representation of week, e.g., Week 35: Aug 27 - Sep 2 2018 
    1. tuple of long weekday locale representations, e.g., Mon Sep 10 2018
    2. tuple of short weekday representations, e.g., Mon 10.

The model is also responsible for providing data appropriate for each view from the relevant table. Unlike the items and instances tables which are updated only when an item changes, data provided for views is generated on-demand. E.g., when the agenda view is asked to display a particular week, 

### [Item Views](#toc)

- Next view

    locations = {}
    for row in filtered_table:
        if row.location:
            tmp = (row.type, row.summary, row.relevant_datetime, row.uid)
            locations.setdefault(row.location, []).add(tmp)

- Index View
    - Use recursive_dict to create tree with index paths and list of items values
- 


### [Instance Views](#toc)

### [CRUD](#toc)

- create
    - create new item from string, insert in data store and retrieve its uid
    - insert new row in the items table for the returned uid and sort table
    - insert new rows in the instances table for the returned uid and sort table
- read:
    - preparation for views: filter appropriate table rows based on calendar, tabs, index, ... and return appropriated sorted
    - items views
        - index view: tree with node paths corresponding to index components and leaves corresponding to  (uid, type, summary, relevant datetime)
        - tab view: hash tab -> (uid, type, summary, relevant datetime)
        - history view: table [uid, type, summary, created, modified]
        - next: hash location -> (uid, type, summary, extent) 
    - instances views
        - Agenda View: filter rows matching (year, week)
            - week header and long formatted days from date reference data for year, week
            - uid, display columns from typecode tuple
        - Busy View: filter rows matching (year, week)
            - week header and short day headers from reference data for year, week
            - uid, display columns from minutes tuple
        - Month: rows matching (year, week) in the six year-weeks for year* and month*. E.g., December, 2017 would include year-weeks (2017, 48), ..., (2017, 52), (2018, 1).
- update uid: 
    - update item matching uid in the data store
    - remove row matching uid in the items table
    - remove rows matching uid in the instances table
    - insert new row in the items table and sort
    - insert new rows in the instances table and sort
- delete uid
    - remove item matching uid from the data store
    - remove row matching uid in the items table
    - remove rows matching uid in the instances table

### [API](#toc)

- create_item(str): creates item corresponding to str, adds it to the data store and updates the instances and items tables 
- update_item(uid, str)
- check_item(str, pos)
- delete_item(uid)
- get_items() -> list of items
- get_item(uid) -> str representation of item corresponding to uid
- get_tags -> hash: tag -> list of items containing tag, sorted by tag
- get_agenda(year, week) -> list of 7 lists of instances, one for each week day, 0 (Mon) - 6 (Sun)
- get
- get_month(year, month) -> nested list of instances for the weekdays in the 6 year-weeks beginning with the week containing the first day in month

