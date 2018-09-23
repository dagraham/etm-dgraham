# What's planned for the next etm?
**Last modified: Sat Sep 22, 2018 11:38PM EDT**

# TOC
<!-- vim-markdown-toc GFM -->

* [Goals](#goals)
* [Data](#data)
    * [Item Types](#item-types)
        * [event](#event)
        * [task](#task)
        * [record](#record)
        * [inbox](#inbox)
    * [Notices](#notices)
        * [Beginning Soon](#beginning-soon)
        * [Past Due](#past-due)
        * [Waiting](#waiting)
        * [Finished](#finished)
    * [Expansions](#expansions)
    * [`@`keys](#keys)
    * [`&`keys](#keys-1)
        * [for use with `@j`:](#for-use-with-j)
        * [for use with `@r`:](#for-use-with-r)
    * [TinyDB](#tinydb)
    * [Dates, Times and Periods](#dates-times-and-periods)
    * [The relevant datetime of an item](#the-relevant-datetime-of-an-item)
* [Views](#views)
    * [Weekly](#weekly)
        * [Agenda](#agenda)
        * [Busy](#busy)
        * [Done](#done)
    * [Monthly ](#monthly-)
    * [Next](#next)
    * [Index](#index)
    * [History](#history)
    * [Tags](#tags)
    * [Query](#query)
* [Work Flow](#work-flow)
    * [Editing an existing item](#editing-an-existing-item)
    * [Creating a new item](#creating-a-new-item)
* [Command Shortcut Keys](#command-shortcut-keys)
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

# [Goals](#toc)

- Simplify etm usage. 
    - Reduce the number of item types and make them more flexible. See [Item Types](#item-types).
    - Enhance support for component jobs within tasks. See [Task](#task). 
    - Simplify support for dates and datetimes, both aware and naive. See [Dates, Times and Periods](#dates-times-and-periods). 
    - Similify data entry with automatic suggestions and result previews. See [Work Flow](#work-flow).
- Improve code.
    - Refactor and decouple code using "smart model, thin controller and dumb view" approach in which the model provides an API that can be used by a variety of views including a command line interface.
    - Simplify code, document it and add doc tests - make the code more easilty maintainable. 
    - Speed up performance. Make use of a text-based document store called *TinyDB* that is designed for quick insertions, modifications and retrievals. Make use of stored unique identifiers, to limit view updates to the item actually changed. See [Storage](#storage).
    - Provide a simpler, GUI along with a CLI that allows creating items and reports from the command line. See [Views](#views) for details about the various views.

# [Data](#toc)

## [Item Types](#toc)

### [event](#toc)

Type character: **\***

Corresponds to VEVENT in the vcalendar specification.

- The `@s` entry is required and can be specified either as a date or as a datetime. It is interpreted as the starting date or datetime of the event. 
- If `@s` is a date, the event is regarded as an *occasion* or *all-day* event. Such occasions are displayed first on the relevant date using the display character `^`. 
- If `@s` is a datetime, an `@e` entry is allowed and is interpreted as the extent or duration of the event - the end of the event is then given implicitly by starting datetime plus the extent and this period is treated as busy time.  Events with datetimes are displayed on the relevant date according to the starting time using the display character `*`. 
- **New**: The old *occasion* item type, `^`, has been replaced by the ability to use a date rather than a datetime in `@s`.

### [task](#toc)

Type character: **-**

Corresponds to VTODO in the vcalendar specification.

- The `@s` entry is optional and, if given, is interpreted as the date or datetime at which the task is due. 
    - Tasks with an `@s` datetime entry are regarded as pastdue after the datetime and are displayed in *Agenda View* on the relevant date according to the starting time. 
    - Tasks with `@s` date entry are regarded as pastdue after the due date and are displayed in *Agenda View* on the due date after all items with datetimes.
- Tasks without an `@s` entry are to be completed when possible and are sometimes called *todos*. They are regarded as *next* items in the *Getting Things Done* terminology and are displayed in *Next View* grouped by `@l` (location/context).
- Jobs
    - Tasks, both with and without `@s` entries can have component jobs using `@j` entries.  A task with jobs thus replaces the old task group.
    - For tasks with an `@s` entry, jobs can have an `&s` entry to set the due date/datetime for the job. It can be entered as a timeperiod relative to  the starting datetime (+ before or - after) for the task or as date/datetime. However entered, the value of `&s` is stored as a relative timeperiod with zero minutes as the default.
    - For tasks with an `@s` entry, jobs can also have `&a`, alert, and `&b`, beginning soon, notices. The entry for `&a` is given as a time period relative to `&s` (+ before or - after) and the entry for `&b` is a positive integer number of days before the starting date/time to begin displaying "beginning soon" notices. Entries for `@a` and `@b` in the task become the defaults for `&a` and `&b`, respectively.  E.g., with

            - beginning soon example @s 1/30/2018 @b 10
                @j job A &s 5d
                @j job B 

        Beginning soon notices would begin on Jan 15 for job A (due Jan 25) and on January 20 for job B (due Jan 30).
    - Prerequisites
        - Automatically assigned. The default is to suppose that jobs must be completed sequentially in the order in which they are listed. E.g., with

                - automatically assigned
                    @j job A
                    @j job B
                    @j job C
                    @j job D

            `job A` has no prerequisites but is a prerequisite for `job B` which, in turn, is a prerequisite for `job C` which, finally, is a prerequisite for `job D`. 
        - Manually assigned.  Job prequisites can also be assigned manually using entries for `&n` (name) and `&p`, (comma separated list of names of immediate prequisites). E.g., with

                - manually assigned
                    @j job a &n a
                    @j job b &n b &p a
                    @j job c &n c &p a
                    @j job d &n d &p b, c

            Here `job a` has no prequisites but is a prerequisite for both `job b` and `job c` which are both prerequisites for `job d`. The order in which the jobs are listed is irrelevant in this case. 
    - Tasks with jobs are displayed by job using a combination of the task and job summaries with a type character indicating the status of the job. E.g.,  

            x manually assigned [1/2/1]: job a
            - manually assigned [1/2/1]: job b
            - manually assigned [1/2/1]: job c
            + manually assigned [1/2/1]: job d

        would indicate that `job a` is *finished*, `job b`  and `job c` are *available* (have no unfinished prerequistites) and that `job d` is *waiting* (has one or more unfinished prerequisties). The status indicator in square brackets indicates the numbers of finished, available and waiting jobs in the task, respectively.

- An entry for `@e` can be given with or without an `@s` entry and is interpreted as the estimated time required to complete the task.
- When a job is finished, the "done" datetime is recorded in an `&f` entry in the job and, if there was a due datetime, that is appended using the format `&f done:due`. When the last job in a task is finished or when a task without jobs is finished a similar entry in the task itself using `@f done:due`. If there are jobs, then the `&f` entries are removed from the jobs. 
- Another step is taken for repeating tasks with as yet unfinished future repetitions. When the task or last job in the current repetition is completed, the `@s` entry is updated using the setting for `@o` to show the next due datetime and the `@f` entry is removed and appended to `@h`. A user configuration setting determines the number of most recent done:due records retained.  
- **New** 
	-	The old `@c`, *context*, for tasks has been merged into *location*, `@l`.  
	- The old *task group* item type, `+`, has been replaced by the ability to add job entries, `@j`, to any task. See [Jobs](#jobs) below.
	- The old `%`, *delegated*, item type has been eliminated. Prepending the name of the person to whom a task is delegated to the task summary followed by a colon is recommended for such tasks. Setting a filter corresponding to the person's name would then show all tasks delegated to that person.
    - The old `?` *someday* item type has been eliminated. Setting `@l ~someday` and omitting @s is recommended for such tasks. They will then be displayed last in the next view under *~someday*. [The tilde character, `~`, sorts after alphanumeric characters.]  

### [record](#toc)

Type character: **%**

Corresponds to VJOURNAL in the vcalendar specification.

A combination of the old *note* and *action* item types. 

- The `@s` is optional and, if given, is interpreted as the datetime to which the record applies. 
- Records without `@s` entries might be used to record personal information such as account numbers, recipies or other such information not associated with a particular datetime.
- Records with `@s` entries associate the record with the datetime given by `@s`. A vacation log entry, for example, might record the highlights of the day given by `@s`.
- Records with both `@s` and `@e` entries associate the record with the expenditure of the time given by `@e` ending at the datetime given by `@s`. Such records are equivalent to the old *action* item type. Records missing either an `@s` or an `@e` entry are equivalent to the old *note* item type. An built-in report groups and totals times for such "actions" by month and then index entry.


### [inbox](#toc)

Type character: **!**

Corresponds to VTODO in the vcalendar specification.

An inbox items can be regarded as a task that is always due on the current date. E.g., you have created an event to remind you of a lunch meeting but need to confirm the time. Just record it using `!` instead of `*` and the entry  will appear highlighted in the agenda view on the current date until you confirm the starting time. 

Unchanged but for the change in the type character from `$` to `!` to better reflect the urgency associated with such items.  Inbox items are displayed in dated views on the current date. 

## [Notices](#toc)

### [Beginning Soon](#toc)

Type character: **>**

For items with `@b` entries, when the starting date given by `@s` is within `@b` days of the current date, a warning that the item is beginning soon appears on the current date together with the item summary and the number of days remaining.

### [Past Due](#toc)

Type character: **<**

When a task is past due, a warning that the task is past due appears on the current date together with the item summary and the number of days past due. 

### [Waiting](#toc)

Type character: **+**

When a task job has one or more unfinished prerequisites, it is displayed using **+** rather than **-**.

### [Finished](#toc)

Type character: **x**

When a task or job is finished, it is displayed on the finished date using **x** rather than **-**. 

## [Expansions](#toc)

The old *defaults* item type, `=`, is eliminated. Its functionality is replaced by the `@x`, *expansion key*, entry which is used to specify a key for options to be extracted from the etm configuration settings. E.g., suppose your configuration setting has the following entry for *expansions*:

        expansions = {
          'class': {
            'e': '1h15m',
            'a': '10m, 3m: d',
            'l': 'Social Sciences Bldg',
            'i': 'Work:Teaching'
           },
          'tennis': {
            'e': '1h30m',
            'a': '30m, 15m: d',
            'l': 'Fitness Center',
            'i': 'Personal:Tennis'
           },
          ...
        }

Then entering the item

      * Conflict and Cooperation @s 1/25/2018 9:35am @x class 
        @l Math-Physics Bldg 

is equivalent to entering

      * Conflict and Cooperation @s 1/25/2018 9:35am @e 1h15m @a 10m, 3m: d 
        @l Math-Physics Bldg @i Work:Teaching

The `@e`, `@a`, `@l` and `@i` entries from `class` have become the defaults for the event but the default for `@l` has been overridden by the explicit entry.

Note that changing the entry for `expansions` in your configuration settings will only affect items created/modified after the change. When an item is saved, the `@x` entry is replaced by its expansion. [Is this the correct behavior?]

## [`@`keys](#toc)

    +: include: list of datetimes to include,
    -: exclude: list of datetimes to exclude from rrule,
    a: alert (list of timeperiods[: cmd[, list of cmd args]]),
    b: beginby: integer (number of days),
    c: calendar: string,
    d: description: string,
    e: extent: timeperiod,
    f: finished: datetime,
    g: goto: string (url or filepath),
    h: history: list of (done:due datetimes)
    i: index: colon delimited string,
    j: job summary: string, optionally followed by job &key entries
    l: location/context: string,
    m: memo: string,
    o: overdue: character from (r)estart, (s)kip or (k)eep),
    p: priority: integer,
    r: repetition frequency: character from (y)early, (m)onthly, (w)eekly,  
       (d)aily, (h)ourly or mi(n)utely, optionally followed by repetition
       &key entries
    s: starting: date or datetime,
    t: tags: list of strings,
    x: expansion key: string,
    z: timezone: string,

## [`&`keys](#toc)

These keys are only used with `@j` (job) and `@r` (repetition) entries.

### [for use with `@j`:](#toc)
      a: alert: (list of timeperiods[: cmd[, list of cmd args]])
      b: beginby: integer number of days relative to &s
      d: description: string
      e: extent: timeperiod
      f: finish: datetime
      l: location/context: string
      m: memo: string
      n: job name (string)
      p: prerequisites (comma separated list of job names of immediate
         prereqs)
      s: start/due: timeperiod relative to @s entry (default 0m)

### [for use with `@r`:](#toc)
      c: count: integer number of repetitions 
      d: monthday: list of integers 1 ... 31
      e: easter: number of days before (-), on (0) or after (+) Easter
      h: hour: list of integers in 0 ... 23
      i: interval: positive integer to apply to frequency, e.g., with
         @r m &i 3, repetition would occur every 3 months
      m: month: list of integers in 1 ... 12
      n: minute: list of integers in 0 ... 59
      s: set position: integer
      u: until: datetime 
      w: weekday: list from SU, MO, ..., SA possibly prepended with 
         a positive or negative integer

> Note. It is an error to specify both `&c` and `&u`. A distinction between using `@c` and `@u` is worth noting and can be illustrated with an example. Suppose an item starts at 10am on a Monday  and repeats daily using either count, `&c 5`, or until, `&u fri 10a`.  Both will create repetitions for 10am on each of the weekdays from Monday through Friday. The distinction arises if you later decide to delete one of the instances, say the one falling on Wednesday. With *count*, you would then have instances falling on Monday, Tuesday, Thursday, Friday *and Saturday* to satisfy the requirement for a count of five instances. With *until*, you would have only the four instances on Monday, Tuesday, Thursday and Friday to satisfy the requirement that the last instance falls on or before 10am Friday.


## [TinyDB](#toc)

- All etm item data is stored in a single, *json* file using the python data store *TinyDB*. This is a plain text file that is human-readable, but not easily human-editable.  It can be backed up and/or queried using external tools as well as etm itself. Here is an illustrative record:

        "2756": {
          "c": "shared",
          "created": "20180301T1537A",
          "itemtype": "*",
          "r": [
            {
            "m": "3",
            "r": "y",
            "w": "2SU"
            }
          ],
          "s": "{D}:20180310",
          "summary": "Daylight saving time begins"
          }

    which corresponds to creating the following entry on March 1, 2018 at 15:37 UTC:

        * Daylight saving time begins @s 2018-03-10 @r y &M 3 &w 2SU @c shared

- The unique identifier, `2756`, is created automatically by *TinyDB*.
- Two timestamps are automatically created for items: `created`, corresponding to the moment the item was created and `modified`, if the item is subsequently modified,  corresponding to the moment the item was last modified.  
- **New**
    - A *history* view displays all items and allows sorting by either created or modified. 
	- The hierarchical organization that was provided by file paths and/or `@k keyword` entries is provided by the *index* entry, `@i`, which takes a colon delimited string. E.g., the entry 

			@i plant:tree:oak

		would display the item in the *index* view under:

			- plant
				  - tree
					    - oak

        Similarly, the default action report groups actions (records with both `@s` and `@e` entries) by month and index.

	- The organization that was provided by calendars is provided by the *calendar* entry, `@c`. A default value for calendar specified in preferences is assigned to an item when an explicit value is not provided. 

## [Dates, Times and Periods](#toc)

- Dates (necessarily naive) and datetimes (both naive and aware) are suppored along with durations (pendulum durations which are analagous to python timedeltas).
- Localization is supported using Pendulum, e.g. 

			>>> pendulum.set_locale('fr')
			>>> dt = pendulum.datetime(2018, 8, 4)
			>>> dt.format('dddd D MMMM YYYY')
			'samedi 4 août 2018'
- Storage: 
    - Special storage classes have been added to etm's instance of *TinyDB* for date, datetime and duration storage. *Pendulum* date,  datetime and duration objects used by etm are automatically encoded (serialized) as strings when stored in *TinyDB* and then automatically decoded as date, datetime and duration objects when retrieved by etm. 
    - Preserving the *naive* or *aware* state of the object is accomplished by appending either an *N* or an *A* to the serialized string. 
    - Aware datetimes are converted to UTC when encoded and are converted to the local time when decoded. 
    - Naive dates and datetimes are not converted when encoded. When decoded, dates are converted to midnight and then, along with naive datetimes, are treated as aware in the local timezone.
- Fuzzy parsing of entries is suppored. 
- Examples of fuzzy parsing and serialization supposing that it is currently Wed, Jan 4, 2018 and that the local timezone is US/Eastern:
	- Naive date:

				@s fri

		Interpreted as `Fri, Jan 5, 2018`. With only a **date** specified, this schedules a floating (naive) item for the specified date in whatever happens to be the local timezone and would be serialized as `{D}:20180105`. Note that dates are necessarily naive and thus there is no need to append an `N` to the serialization.
	- Aware datetime in the local timezone:

				@s fri 2p

		Interpreted as `Fri, Jan 5, 2018 2pm EST`. With both a **date** and a **time** specified but without an entry for `@z`, this schedules an item starting at the specified datetime in the **local timezone** (US/Eastern) and would be serialized as `{T}:20180105T1900A`. Note the conversion to UTC time and the appended `A` to indicate that this is an aware datetime.
    - Aware datetime in a different timezone:

				@s fri 2p @z US/Pacific

		With the **timezone** specified, this would be interpreted as `Fri, Jan 5 2018 2pm PST` and would be serialized as `{T}:20180105T2200A`. Again note the conversion to UTC time and the appended `A` to indicate that this is an aware datetime.

		In the local timezone (US/Eastern) this item would be displayed as starting at 5pm EST.
    - Naive datetime:

				@s fri 2p @z float

		With both a **date** and a **time** specified and with `float` as the timezone, this would be interpreted as `Fri, Jan 5, 2018 2pm`, in whatever happens to be the local timezone, and would be serialized as `{T}:20180105T1400N`. Note the appended `N` to indicate that this is a naive datetime.

    The assumption here is that when a user enters a date, a date is what the user wants. When both a date and time are given, what the user wants is a datetime and, most probably, one based on the local timezone. Less probably, one based on a different timezone and that requires the additon of the `@z` and the timezone. Still less probably, one that floats and this requires the addition of the `@z` and `float`.
- Since python cannot compare aware with naive datetimes or dates with datetimes, etm converts everything to aware datetimes in the local timezone of the user. Since aware datetimes are are stored as UTC times, they are converted to the local timezone. Dates are first converted to datetimes using midnight as the time and then treated as aware in the local timezone without conversion. Similarly, naive datetimes are treated as aware in the local timezone without conversion. 
- When an item with an aware `@s` entry repeats, the hour of the repetition instance *ignores* daylight savings time changes. E.g., with

			@s Fri Jan 26 2018 2pm @r m -1FR @z US/Eastern

	the first three repetitions would all be at 2pm even though the first two are EST and the third is EDT: 

			Fri Jan 26 2018 2:00PM
			Fri Feb 23 2018 2:00PM
			Fri Mar 30 2018 2:00PM
- Display:
    - Naive dates are displayed without conversion and without a starting time. 
    - Naive datetimes are displayed without conversion.
    - Aware datetimes are converted to the current local timezone. E.g., in the US/Eastern timezone, `fri 2p` would display as starting at 2pm on Jan 5 if the computer is still in the Eastern timezone but would display as starting at 11am if the computer had been moved to the Pacific timezone. Similarly, `fri 2p, US/Pacific` would display as starting at 5pm if the computer were in the Eastern timezone.
    - Datetimes are rounded to the nearest minute for display.
- **New**
	- *Simple repetition* is supported using a combination of `@s` and `@+` entries. E.g., 

				* my event @s 2018-02-15 3p @+ 2018-03-02 4p, 2018-03-12 9a

		would repeat at 3pm on Feb 15, 4pm on Mar 2 and 9am on Mar 12. Note that there is no `@r` entry and that the datetimes from `@s` and from `@+` are combined. With an `@r` entry, on the other hand, only datetimes from the recurrence rule that fall on or after the `@s` entry are used. This replaces and simplifies the old `@r l`, list only, repetition frequency.

## [The relevant datetime of an item](#toc)

Used, e.g., in index view.

- Non-repeating events and non-repeating unfinished tasks: the datetime given in `@s`. 
- Repeating events: the datetime of the first instance falling on or after today or, if none, the datetime of the last instance. (needs updating)
- Repeating unfinished tasks with `@o r` or `@o k` (the default): the datetime given in `@s`. This datetime is automatically updated when an instance is completed to the due datetime of the next instance.
- Repeating unfinished tasks with `@o s`: the datetime of the first instance falling during or after the current date. (needs updating)
- Finished tasks: the datetime given in `@f`.
- Actions: the datetime given in `@f`.
- Someday entries, inbox enties, undated record entries and undated, unfinished tasks: *None*

# [Views](#toc)

View shortcut keys: a)genda, b)usy, d)one, m)onthly, h)istory, i)ndex, n)ext, q)uery and t)ags. In all views, pressing `l` prompts for the outline expansion level and `f` prompts for a filter to apply to the displayed items.

ASCII art is used in the following to suggest the appearance of the view in the GUI. The recommended terminal size is 30 rows by 60 columns. In the ASCII representations the top bar and status bars each take 3 lines though in each actually takes only 1 line leaving 28 lines for the main panel. Line numbers are shown in the first few views to illustrate this.

## [Weekly](#toc)

*Agenda*, *Busy* and *Done* views are synchronized so that switching from one of these views to another always displays the same week.

### [Agenda](#toc)

- Scheduled items, grouped and sorted by week and day

        +------------------------- top bar --------------------------+  
        | Agenda - Week 3: Jan 15 - 21, 2018                 F1:help |  1
        +------------------------------------------------------------+ 
        | Mon Jan 15                                                 |  2
        |   * Martin Luther King Day                                 |  3
        |   * Lunch with Joe                            12:30-1:30pm |  4
        |   - Revise 1st quarter schedule                 3pm  1h    |  5
        | Thu Jan 18 - Today                                         |  6
        |   < Revise 1st quarter schedule                    3d      |  7
        |   > Duke vs Pitt                                   2d      |  8
        |   * Conference call                            11:30am-1pm |  9
        | Sat Jan 20                                                 | 10 
        |   * Duke vs Pitt                                  4-6pm    | 11
        |   * Dinner                                        7-9pm    | 12
        |                                                            | 13
        |                                                            | 14
        |                                                            | 15
        |                                                            | 16
        |                                                            | 17 
        |                                                            | 18
        |                                                            | 19
        |                                                            | 20
        |                                                            | 21
        |                                                            | 22
        |                                                            | 23
        |                                                            | 24
        |                                                            | 25
        |                                                            | 26
        |                                                            | 27
        |                                                            | 28
        |                                                            | 29
        +------------------------ status bar ------------------------+ 
        | 8:49am Thu Jan 18                                10:30am+1 | 30
        +------------------------------------------------------------+

- The top title bar shows the selected week.
- The main panel shows scheduled items grouped and sorted by date and time.
- Weeks are displayed sequentially. If there is nothing to display for the week, then the main panel of the displayould shows "Nothing scheduled". E.g, 

        Week 2: Jan 8 - 14, 2018                            F1:Help
          Nothing scheduled

    For the current week, the display would show "Nothing scheduled" under the current date. E.g.,

        Week 3: Jan 15 - 21, 2018                           F1:Help
        - Thu Jan 18 - Today
          Nothing scheduled

- Starting from the top, the display for a day includes the following:

    - All day events (occasions), if any, using the display character `^` instead of the event type character `*` and highlighted using the occasion color.
    - *For the current date (today) only*:

        - Inbox entries, if any, highlighted using the inbox color.
        - Pastdue tasks, if any, with the number of days that have passed since the task was due using the display character `<` and highlighted using the pastdue color. 
        - Beginning soon notices, if any, with the number of days remaining until the starting date of the item using the display character `>` and highlighted using the beginning soon color.

        Note that the items included for the current date are those from the old *agenda* view.

    - Scheduled events, notes, actions and unfinished tasks sorted by `@s` which is displayed in the 2nd column. For events with *extent*, the ending time is also displayed. For tasks with *extent*, the extent period is also displayed. Each item is highlighted using the type color for that item.
    - Unfinished all day tasks, if any, highlighted using the task color.
    - All day notes, if any, using the note color.

### [Busy](#toc)

- Hours in the day that are partially or wholly "busy" are filled using the color of the calendar for the relevant item. Shown here with `#`.
- Hours in which a conflict occurs are filled with the overlapping calendar colors of the relevant items. Shown here with `###`.
- Mouse over tool tips show the summary and times for the relevant item.

        +----------------------------------------------------------+
        | Busy - Week 4: Jan 22 - 28, 2018                 F1:help |  1
        +----------------------------------------------------------+
        |        Mon    Tue    Wed    Thu    Fri    Sat    Sun     |  2
        |         22     23     24     25     26     27     28     |  3
        |        -----------------------------------------------   |  4
        |    12a   .      .      .      .      .      .      .     |  5
        |          .      .      .      .      .      .      .     |  6
        |          .      .      .      .      .      .      .     |  7
        |          .      .      .      .      .      .      .     |  8
        |          .      .      .      .      .      .      .     |  9
        |          .      .      .      .      .      .      .     | 10
        |     6a   .      .      .      .      .      .      .     | 11 
        |          .      .      .      .      .      .      .     | 12
        |          #      .      #      .      #      #      .     | 13
        |          #      .      #      .      #      #      .     | 14
        |          .      #      .      .      .      #      .     | 15
        |          .      #      .      #      .      #      #     | 16
        |    12p   #      .      .      #      .      #      #     | 17
        |          #      .      .     ###     .      #      #     | 18
        |          .      .      .      #      .      .      #     | 19
        |          .      .      .      .      .      .      #     | 20
        |          #      .      .      .      .      .      .     | 21
        |          #      .      .      .      .      .      .     | 22
        |     6p   .      .      #      .      .      .      .     | 23
        |          #      .      #      .      .      .      .     | 24
        |          #      .      #      .      .      .      .     | 25
        |          #      .      .      .      .      .      .     | 26
        |          .      .      .      .      .      .      .     | 27
        |    12a   .      .      .      .      .      .      .     | 28
        |                                                          | 29
        +----------------------------------------------------------+
        | 8:49am Thu Jan 18                              10:30am+1 | 30
        +----------------------------------------------------------+


### [Done](#toc)

- Actions and finished tasks grouped and sorted by week and day using the finished datetime
- Actions are displayed with type character `%`, the item summary,  the time finished and the active time period. Finished tasks are displayed with type character `x`, the summary and time finished. E.g., here is a record of time spent working on a task and then marking the task finished:

        +------------------------- top bar ------------------------+
        | Done - Week 3: Jan 15 - 21, 2018                 F1:help |
        +----------------------------------------------------------+
        | Mon Jan 15                                               |
        |   % report summary                          4:29pm   47m |
        |   x report summary                             4:30pm    | 


## [Monthly ](#toc)

- The top pane displays 6 weeks starting with the first week of the selected month.  Month day numbers are colored from dark blue to bright red to indicate the amount of time scheduled.

- Week numbers and month day numbers in the top panel are buttons. Activating a week number switches to *Agenda* view for that week. Activating a date displayes the schedule for that date in the bottom pane using the same format as *Agenda* view. Switching to one of the weekly views will always display the week of the selected date. 

  Dates with busy periods are coded:

    - night: 12am - 6am:    #___
    - morning 6am-12pm:     _#__
    - afternoon 12pm - 6pm: __#_
    - evening 6pm - 12am:   ___#

  These can be combined. E.g., Aug 1 below shows events scheduled for both  morning and evening: `_#_#`.

        +----------------------------------------------------------+
        | Monthly - August 2017                            F1:help |  1
        +----------------------------------------------------------+
        |   Wk    Mon    Tue    Wed    Thu    Fri    Sat    Sun    |  2
        |  ----+-------------------------------------------------  |  3
        |   31 |   31      1      2      3      4      5      6    |  4
        |      |         _#_#                                      |  5
        |      |                                                   |  6
        |   32 |    7      8      9     10     11     12     13    |  7
        |      |                                                   |  8
        |      |                                                   |  9
        |   33 |   14     15     16     17     18     19     20    | 10
        |      |                                                   | 11
        |      |                                                   | 12
        |   34 |   21     22     23     24     25     26     27    | 13
        |      |                                                   | 14
        |      |                                                   | 15
        |   35 |   28    [29]    30     31      1      2      3    | 16
        |      |                                                   | 17
        |      |                                                   | 18
        |   36 |    4      5      6      7      8      9     10    | 19
        |      |                                                   | 20
        +------+---------------------------------------------------+ 21
        | Tue Aug 29 2017                                          | 22
        |   Nothing scheduled                                      | 23
        |                                                          | 24
        |                                                          | 25
        |                                                          | 26 
        |                                                          | 27
        |                                                          | 28
        |                                                          | 29
        +----------------------------------------------------------+
        | 8:49am Thu Jan 18                              10:30am+1 | 30
        +----------------------------------------------------------+


## [Next](#toc)

- Unfinished tasks and jobs that are undated (without `@s` entries) grouped and sorted by *location* and then *priority*. 
- As tasks and jobs are finished, they are removed from this view and added to *Done* using the completion datetime.

## [Index](#toc)

- All items, grouped and sorted by their *index* entries and then *relevant datetime*. 
- Items without `@i` entries are listed last under *None*.

## [History](#toc)


        +------------------------- top bar --------------------------+  
        | History: creation datetime ascending               F1:help |  1
        +------------------------------------------------------------+ 
        | * Martin Luther King Day                       2016-01-02  |  2
        |                                                            |  3
        |                                                            |  4
        |                                                            |  5
        |                                                            |  6
        |                                                            |  7
        |                                                            |  8
        |                                                            |  9
        |                                                            | 10 
        |                                                            | 11
        |                                                            | 12
        |                                                            | 13
        |                                                            | 14
        |                                                            | 15
        |                                                            | 16
        |                                                            | 17 
        |                                                            | 18
        |                                                            | 19
        |                                                            | 20
        |                                                            | 21
        |                                                            | 22
        |                                                            | 23
        |                                                            | 24
        |                                                            | 25
        |                                                            | 26
        |                                                            | 27
        |                                                            | 28
        |                                                            | 29
        +------------------------ status bar ------------------------+ 
        | 8:49am Thu Jan 18                                10:30am+1 | 30
        +------------------------------------------------------------+


- All items, sorted by the datetime created.

- All items, sorted by the datetime last modified.

## [Tags](#toc)

Tagged items grouped and sorted by tag.

## [Query](#toc)

Analagous to the old custom view. Used to issue queries against the data store and display the results. 

# [Work Flow](#toc)

## [Editing an existing item](#toc)

- Pressing Return with an item selected shows details:

        +------------------------ top bar -------------------------+
        | details                                          F1:help |
        +----------------------------------------------------------+
        | - task group @s 2016-06-28 00:00 @b 7 @a 2d: m @a 2d: v  |
        |   @r m &i 1                                              |
        |   @j Job A &s 4w &b 2 &i 1 &a 2d: m &a 2d: v             |
        |   @j Job B &s 2w &b 3 &i 2 &p 1 &a 2d: m &a 2d: v        |
        |   @j Job C &s 0m &b 7 &i 3 &p 2 &a 2d: m &a 2d: v        |
        |                                                          |
        | created:  20160601T1400                                  |
        | modified: 20160601T1400                                  |
        |                                                          |


- When `Shift-E` (edit), `Shift-D` (delete) or `Shift-C` (copy) is pressed and the item is repeating then select the appropriate instances with these check  boxes: 

                +-------------------------------------------+
                |    Which instances?                       |
                |    [] Earlier   [X] Selected   [] Later   | 
                +-------------------------------------------+ 

- When edit or copy is selected, the details of the relevant item is displayed ready for editing. When a new item is created as with copy, it will be displayed as changed.

- Whenever the edited version is different than the saved version:

    - topbar: `editing: unsaved changes`
    - status bar: `^S:save  ^Q:save and close  ^U:undo changes` 
        - Save processes the item, updates the data store and refreshes the display.
        - Undo changes refreshes the display using the current, saved version of the item from the data store.

- When any changes have been saved or undone:

    - topbar: `editing: no unsaved changes`
    - status bar: `^Q:close` 

## [Creating a new item](#toc)

- When creating a new item, the process is the same but for the fact that the initial entry will be empty. 

        +------------------------- top bar ------------------------+
        | editing: new item                                F1:help |
        +----------------------------------------------------------+
        | type character for the new item?                         |
        | > _                                                      |
        | -------------------------------------------------------- |
        | item type characters:                                    |
        |   *: event       -: task          $: action              |
        |   %: note     ?: someday       !: inbox               |

- Editing takes place in the line beginning with the `>` prompt. The current cursor position is shown by the underscore `_`.

- Closing before any changes have been made will cancel the operation and no new item will be created. 

- The main panel reflects any changes as they occur:

        +------------------------ top bar -------------------------+
        | editing: unsaved changes                         F1:help |
        +----------------------------------------------------------+
        | summary for the event?                                   |
        | > * my ev_                                               |
        | -------------------------------------------------------- |
        | Enter the summary for the event followed, optionally, by |
        | @key and value pairs.                                    |

- As editing progresses, the display changes to show information relevant to the current entry. Here are some illustrative screens.

  - Summary entered and an initial `@` but without the key:

        +----------------------------------------------------------+
        | @key?                                                    |
        | > * my event @_                                          |
        | -------------------------------------------------------- |
        | Available @keys:                                         |
        |   Required: @s                                           |
        |   Allowed: @c, @d, @e, @g, @i, @l, @m, @t, @v            |
        |   Requires @s: @a, @b, @+, @r                            |
        |   Requires @r: @-                                        |

  - With `@s fri` entered but without a time

        +----------------------------------------------------------+
        | @s: starting date or datetime?                           |
        | > * my event @s fri_                                     |
        | -------------------------------------------------------- |
        | currently: Fri Jan 19 2018                               |
        | Without a time, this schedules an all-day, floating item |
        | for the specified date in whatever happens to be the     |
        | local timezone.                                          |

  - With `@s fri 2p` entered

        +----------------------------------------------------------+
        | @s: starting date or datetime?                           |
        | > * my event @s fri 2p_                                  |
        | -------------------------------------------------------- |
        | currently: Fri Jan 19 2018 2:00PM EST                    |
        | The datetime will be interpreted as an aware datetime in |
        | the current timezone. Append, e.g., ", US/Pacific" to    |
        | specify a particular timezone or ", float" to specify a  |
        | floating item in whatever happens to be the local        |
        | timezone.                                                |

  - Starting an entry for `@r`:

        +----------------------------------------------------------+
        | @r: repetition frequency?                                |
        | > * my event @s fri 2p @r_                               |
        | -------------------------------------------------------- |
        | A character from: (y)early, (m)onthly, (w)eekly, (d)aily |
        |   (h)ourly, mi(n)utely                                   |


  - With `@r m` entered:

        +----------------------------------------------------------+
        | @r: repetition rule?                                     |
        | > * my event @s fri 2p @r m_                             |
        | -------------------------------------------------------- |
        | currently:                                               |
        |    RRULE:FREQ=MONTHLY                                    |
        |    DTSTART:Fri Jan 19 2018 2:00PM EST                    |
        | The first 3 repetitions on or after DTSTART:             | 
        |    Fri Jan 19 2018 2:00PM                                |
        |    Mon Feb 19 2018 2:00PM                                |
        |    Mon Mar 19 2018 2:00PM                                |
        | All times: America/New_York                              |
        |                                                          |
        | Possible options: &c (count), &E (Easter), &h (hour),    |
        |   &i (interval), &m (monthday), &M (month), &n (minute), |
        |   &s (set position), &u (until), &w (weekday)            |

  - With `@r m &w` entered:

        +----------------------------------------------------------+
        | &w: weekdays?                                            |
        | > * my event @s fri 2p @r m &w_                          |
        | -------------------------------------------------------- |
        | A comma separated list of English weekday abbreviations  |
        | from SU, MO, TU, WE, TH, FR, SA, SU. Prepend an integer  |
        | to specify a particular weekday in the month. E.g., 3WE  | 
        | for the 3rd Wednesay or -1FR for the last Friday in the  |
        | month.                                                   | 

  - With `@r m &w -2FR` entered:

        +----------------------------------------------------------+
        | @r: repetition rule?                                     |
        | > * my event @s fri 2p @r m &w -2fr                      |
        | -------------------------------------------------------- |
        | currently:                                               |
        |    RRULE:FREQ=MONTHLY;BYWEEKDAY=-2FR                     |
        |    DTSTART:Fri Jan 19 2018 2:00PM EST                    |
        | The first 3 repetitions on or after DTSTART:             | 
        |    Fri Jan 19 2018 2:00PM                                |
        |    Fri Feb 16 2018 2:00PM                                |
        |    Fri Mar 23 2018 2:00PM                                |
        | All times: America/New_York                              |


# [Command Shortcut Keys](#toc)

    -- VIEWS ------------------------------------------ 
    a: agenda        n: next           q: query 
    b: busy          t: tags           f: filter view 
    d: done          i: index          l: outline level 
    m: month         h: history        c: calendars 
    -- SELECTED ITEM ---------------------------------- 
    C: copy          F: finish         I: export ical 
    D: delete        R: reschedule     L: open link 
    E: edit          S: schedule new   T: start timer 
    -- TOOLS ------------------------------------------ 
    A: show alerts   P: preferences    F2: date calc 
    J: jump to date                    F3: yearly 
    N: new item      V: view as text   F8: quit 


The key bindings for the various commands are listed above. E.g., press 'a' to open agenda view. In any of the views, 'Enter' toggles the expansion of the selected node or item. In any of the dated views, 'Shift Left' and 'Shift Right' change the period displayed and 'Space' changes the display to the current date.


# [MVC](#toc)

Smart **M**odels, dumb **V**iews and thin **C**ontrollers!

## [Model](#toc)

See [TinyDB](#tinydb) for details about the data store. The Model handles CRUD (create, read, update and delete) operations on the data store as well as preparing data output in useful formats for views. 

There are two basic types of views: items and instances. The distinction arises because repeating items have more than one instance associated with each item - one for each datetime on which the item repeats. Views such as Agenda View show each of these instances on the date and time at which the item repeats. On the other hand, item views show the item itself rather than the instances. History View, for example shows each item along with the datetimes it was created and last modified. 

To support views, the model is responsible for maintaining two tables with data relevant to items and to instances. Both tables store the unique id of the relevant item on each row along with data relevant to the item or instance. When an item is updated, only the relevant rows of these tables need to be changed.

### [Data Store](#toc)  

hash uid -> all item details including: 

- index path 
- typecode
- summary
- created
- modified 
- calendar
- location
- tags tuple
- description

### [Supporting queries](#toc)

- uid -> relevant datetime (updated daily)

- for today
    - inbox: [list of uids of inbox items]
    - beginbys: [list of uids with beg and tdy < rel and rel <= tdy + beg]
    - pastdues: [list of uids of unfinished tasks with rel < tdy]
    - alerts: [list of uids with alerts occuring today]


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

