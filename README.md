# etm: event and task manager
*Last modified: Wed Feb 13, 2019 12:44PM EST*

#### TOC
<!-- vim-markdown-toc GFM -->

* [Getting started](#getting-started)
    * [Simple reminders](#simple-reminders)
    * [Reminders that repeat](#reminders-that-repeat)
    * [Editing](#editing)
    * [Installation](#installation)
* [Item Types](#item-types)
    * [event](#event)
    * [task](#task)
    * [record](#record)
    * [inbox](#inbox)
* [notices](#notices)
    * [beginning soon](#beginning-soon)
    * [past due](#past-due)
    * [waiting](#waiting)
    * [finished](#finished)
* [at keys](#at-keys)
    * [`@a` and `@b` notices](#a-and-b-notices)
    * [`@+` repetition](#-repetition)
    * [`@x` expansions](#x-expansions)
* [amp keys](#amp-keys)
    * [for use with @ j](#for-use-with--j)
    * [for use with @ r](#for-use-with--r)
* [The TinyDB Data Store](#the-tinydb-data-store)
    * [Dates, Times and Intervals](#dates-times-and-intervals)
    * [The relevant datetime of an item](#the-relevant-datetime-of-an-item)
* [Views](#views)
    * [Agenda](#agenda)
        * [Schedule](#schedule)
        * [Busy](#busy)
    * [Relevant](#relevant)
    * [Next](#next)
    * [Index](#index)
    * [History](#history)
    * [Tags](#tags)
    * [Query](#query)
* [Work Flow](#work-flow)
    * [Editing an existing item](#editing-an-existing-item)
    * [Creating a new item](#creating-a-new-item)
* [Command Shortcut Keys](#command-shortcut-keys)

<!-- vim-markdown-toc -->

# [Getting started](#toc) 

*etm* offers a simple way to manage your events, tasks and other reminders. Rather than filling out fields in a form to create or edit reminders, a simple text-based format is used in which an item begins with a *type character* followed by a brief summary of the item and then, perhaps, by one or more `@key value` pairs to specify other attributes of the reminder.

Here are some examples:

## [Simple reminders](#toc)

* A reminder (task) to pick up milk. 

		- pick up milk
* Append the [l]ocation "errands" to the milk task. (Undated tasks are displayed grouped by their locations.) 

		- pick up milk @l errands
* A sales meeting (an event) [s]tarting next Monday at 9:00am and [e]xtending for one hour.

        * sales meeting @s mon 9a @e 1h 
* The sales meeting with a default [a]lert 5 minutes before start of the meeting:

        * sales meeting @s mon 9a @e 1h @a 5
* Prepare a report (a task) for the sales meeting with a [b]eginning soon notice starting 3 days before the meeting:

        - prepare report @s mon 9a @b 3
* A record of 35 minutes spent yesterday working on the report:

        % report preparation @s -1 @e 35
* An inbox reminder that the time and location for the lunch meeting have not been confirmed:

		! lunch with Burk @s tue ? @e 90m @l ? 

* Build a dog house (a task) by breaking the task down into component [j]obs:

		- Build dog house @j pick up materials @j cut pieces @j assemble
		  @j sand @j paint

* Join the etm discussion group (a task) [s]tarting on the first day of the next month. Because of the @g goto link, pressing *g* when the item is selected in the gui would open the link using the system default application which, in this case, would be the default browser:

        - join the etm discussion group @s +1/1
          @g http://groups.google.com/group/eventandtaskmanager/topics

## [Reminders that repeat](#toc)

* Get a haircut (a task) on the 24th of the current month and then [r]epeatedly at (d)aily [i]ntervals of (14) days and, [o]n completion, (r)estart from the completion date:

        - get haircut @s 24 @r d &i 14 @o r

* Payday (an event) on the last week day of each month. The `&s -1` part of the entry extracts the last date which is both a weekday and falls within the last three days of the month):

        * payday @s 1/1 @r m &w MO, TU, WE, TH, FR &m -1, -2, -3 &s -1

* Take a prescribed medication daily (a reminder) [s]tarting today and [r]epeating (d)aily at [h]ours 10am, 2pm, 6pm and 10pm [u]ntil (12am on) the fourth day from today. Trigger the default [a]lert zero minutes before each reminder:

        * take Rx @s +0 @r d &h 10, 14, 18, 22 &u +4 @a 0

* Move the water sprinkler (a reminder) every thirty mi[n]utes on Sunday afternoons using the default alert zero minutes before each reminder:

        * Move sprinkler @s 1 @r n &i 30 &w SU &h 14, 15, 16, 17 @a 0

    To limit the sprinkler movement reminders to the [M]onths of April through September each year, append `&M 4, 5, 6, 7, 8, 9` to the @r entry.

* Presidential election day (an occasion) every four years on the first Tuesday after a Monday in November:

        ^ Presidential Election Day @s 2012-11-06
          @r y &i 4 &M 11 &m 2, 3, 4, 5, 6, 7, 8 &w TU

See [item Types](#item-types) for details about the four item types and [`@`keys](#keys) for details about possible attributes.

## [Editing](#toc) ##

Etm offers several conveniences when creating or modifying an item.

* Fuzzy parsing of dates and date times. Supposing it is currently Wed, Feb 13 2019:
    * `@s 2` would be interpreted as the date Feb 2, 2019.
    * `@s 2p` would be interpreted as the datetime 2pm on Feb 13, 2019 in the local timezone.
    * `@s 2p fri` would be interpreted as the datetime 2pm Fri, Feb 15 2019 in the local timezone.
    * `@s 2p fri @z US/Pacific` would be interpreted as the datetime 2pm Fri, Feb 15 2019 in the Pacific timezone.
* Automatic completion for elements you have used before including @z (timezone), @c (calendar), @t (tags), @i (index), @l (location), @n (attendees) and @x (expansion). E.g. when entering `@z `, you can choose from any timezone you have previously used. 





## [Installation](#toc) ##

Python >= 3.6.0 is required.

1) Create a directory for etm and its supporting files:

		$ mkdir ~/.etm
1) Change to this directory, create and activate a virtual environment for etm:

		$ cd ~/.etm
		$ python3 -m venv env
		$ . env/bin/activate
1)  Activating the virtual environment in the last step typically changes the system prompt from something like `$` to something like `(env) $`. You can then install etm and its dependencies with the single command:

		(env) $ pip install etm_mv
	and later update to the latest version with

		(env) $ pip install -U etm_mv
1) etm can now be started with the command

		(env) $ ./etm 

Installing etm in this virtual environment makes it possible to remove etm and all its dependencies by simply deleting this directory. 


# [Item Types](#toc)

## [event](#toc)

Type character: **\***

An event is something that happens at a particular date or datetime without any action from the user. Christmas, for example, is an event that happens whether or not the user does anything about it.


- The `@s` entry is required and can be specified either as a date or as a datetime. It is interpreted as the starting date or datetime of the event. 
- If `@s` is a date, the event is regarded as an *occasion* or *all-day* event. Such occasions are displayed first on the relevant date. 
- If `@s` is a datetime, an `@e` entry is allowed and is interpreted as the extent or duration of the event - the end of the event is then given implicitly by starting datetime plus the extent and this period is treated as busy time. 

Corresponds to VEVENT in the vcalendar specification.

## [task](#toc)

Type character: **-**

A task is something that requires action from the user and lasts, so to speak, until the task is completed and marked finished. Filing a tax return, for example, is a task. 

- The `@s` entry is optional and, if given, is interpreted as the date or datetime at which the task is due. 
    - Tasks with an `@s` datetime entry are regarded as pastdue after the datetime and are displayed in *Agenda View* on the relevant date according to the starting time. 
    - Tasks with `@s` date entry are regarded as pastdue after the due date and are displayed in *Agenda View* on the due date after all items with datetimes.
    - Tasks that are pastdue are also displayed in *Agenda View* on the current date using the type character `<` with an indication of the number of days that the task is past due.
- Tasks without an `@s` entry are to be completed when possible and are sometimes called *todos*. They are regarded as *next* items in the *Getting Things Done* terminology and are displayed in *Next View* grouped by `@l` (location/context).
- Jobs
    - Tasks, both with and without `@s` entries can have component jobs using `@j` entries.  A task with jobs thus replaces the old task group.
    - For tasks with an `@s` entry, jobs can have an `&s` entry to set the due date/datetime for the job. It can be entered as a timeperiod relative to  the starting datetime (+ before or - after) for the task or as date/datetime. However entered, the value of `&s` is stored as a relative timeperiod with zero minutes as the default when `&s` is not entered.
    - For tasks with an `@s` entry, jobs can also have `&a`, alert, and `&b`, beginning soon, notices. The entry for `&a` is given as a time period relative to `&s` (+ before or - after) and the entry for `&b` is a positive integer number of days before the starting date/time to begin displaying "beginning soon" notices. The entry for `@s` in the task becomes the default for `&s` in each job.  E.g., with

            - beginning soon example @s 1/30/2018
                @j job A &s 5d &b 10
                @j job B &b 5

        Beginning soon notices would begin on Jan 15 for job A (due Jan 25) and on January 25 for job B (due Jan 30).
    - Prerequisites
        - Automatically assigned. The default is to suppose that jobs must be completed sequentially in the order in which they are listed. E.g., with

                - automatically assigned
                    @j job A
                    @j job B
                    @j job C
                    @j job D

            `job A` has no prerequisites but is a prerequisite for `job B` which, in turn, is a prerequisite for `job C` which, finally, is a prerequisite for `job D`. 
        - Manually assigned.  Job prequisites can also be assigned manually using entries for `&i` (id) and `&p`, (comma separated list of ids of immediate prequisites). E.g., with

                - manually assigned
                    @j job a &i a
                    @j job b &i b &p a
                    @j job c &i c &p a
                    @j job d &i d &p b, c

            `job a` has no prequisites but is a prerequisite for both `job b` and `job c` which are both prerequisites for `job d`. The order in which the jobs are listed is irrelevant in this case. 
    - Tasks with jobs are displayed by job using a combination of the task and job summaries with a type character indicating the status of the job. E.g.,  

            ✓ manually assigned [2/1/1]: job a
            - manually assigned [2/1/1]: job b
            - manually assigned [2/1/1]: job c
            + manually assigned [2/1/1]: job d

        would indicate that `job a` is *finished*, `job b`  and `job c` are *available* (have no unfinished prerequistites) and that `job d` is *waiting* (has one or more unfinished prerequisties). The status indicator in square brackets indicates the numbers of available, waiting and finished jobs in the task, respectively.

- An entry for `@e` can be given with or without an `@s` entry and is interpreted as the estimated time required to complete the task.
- When a job is finished, the "done" datetime is recorded in an `&f` entry in the job. When the last job in a task is finished or when a task without jobs is finished a similar entry in the task itself using `@f done`. If there are jobs, then the `&f` entries are removed from the jobs. 
- Another step is taken for repeating tasks with as yet unfinished future repetitions. When the task or last job in the current repetition is completed, the `@s` entry is updated using the setting for `@o` to show the next due datetime and the `@f` entry is removed and appended to the list of completions in `@h`. A user configuration setting determines the number of most recent completion records retained for repeating tasks with 3 as the default.  
- When the last instance of a repeating task is finished, `@f` will contain the datetime of the last completion and `@h` the list of prior completions.
- A task, repeating or not, will have an  `@f` entry if and only if the task has been completed.

Corresponds to VTODO in the vcalendar specification.

## [record](#toc)

Type character: **%**

A record of something that the user wants to remember. The userid and password for a website would be an example. A journal entry for vacation day is another example. 

- The `@s` is optional and, if given, is interpreted as the datetime to which the record applies. 
- Records without `@s` entries might be used to record personal information such as account numbers, recipies or other such information not associated with a particular datetime.
- Records with `@s` entries associate the record with the datetime given by `@s`. A vacation log entry, for example, might record the highlights of the day given by `@s`.
- Records with both `@s` and `@e` entries associate the record with the expenditure of the time given by `@e` ending at the datetime given by `@s`. Such records are equivalent to the old *action* item type. Records missing either an `@s` or an `@e` entry are equivalent to the old *note* item type. A built-in report groups and totals times for such "actions" by month and then index entry.

Corresponds to VJOURNAL in the vcalendar specification.

## [inbox](#toc)

Type character: **!**

An inbox item can be regarded as a task that is always due on the current date. E.g., you have created an event to remind you of a lunch meeting but need to confirm the time. Just record it using `!` instead of `*` and the entry  will appear highlighted in the agenda view on the current date until you confirm the starting time. 

Corresponds to VTODO in the vcalendar specification.

# [notices](#toc)

These are generated automatically by *etm*.

## [beginning soon](#toc)

Type character: **>**

For unfinished tasks and other items with `@b` entries, when the starting date given by `@s` is within `@b` days of the current date, a warning that the item is beginning soon appears on the current date together with the item summary and the number of days remaining.

## [past due](#toc)

Type character: **<**

When a task is past due, a warning that the task is past due appears on the current date together with the item summary and the number of days past due. 

## [waiting](#toc)

Type character: **+**

When a task job has one or more unfinished prerequisites, it is displayed using **+** rather than **-**.

## [finished](#toc)

Type character: **✓**

When a task or job is finished, it is displayed on the finished date using **✓** rather than **-**. 

# [at keys](#toc)

`@` followed by a key from the list below and a value appropriate to the key is used to apply attributes to an item. E.g.,

	@s mon 9a

would specify the the starting datetime for the item is 9am on the Monday following the current date.

    +: include: list of datetimes to include,
    -: exclude: list of datetimes to exclude from rrule,
    a: alert (list of + or - periods: list of commands),
    b: beginby: integer (number of days),
    c: calendar: string,
    d: description: string,
    e: extent: period,
    f: finished: datetime,
    g: goto: string (url or filepath),
    h: history: (for repeating tasks, a list of the most recent completion datetimes)
    i: index: colon delimited string,
    j: job summary: string, optionally followed by job &key entries
    l: location/context: string,
    m: mask: string stored in obfuscated form,
    n: attendees: list of 'name <emailaddress>' strings 
    o: overdue: character from (r)estart, (s)kip or (k)eep),
    p: priority: integer,
    r: repetition frequency: character from (y)early, (m)onthly, (w)eekly,  
       (d)aily, (h)ourly or mi(n)utely, optionally followed by repetition
       &key entries
    s: starting: date or datetime,
    t: tags: list of strings,
    x: expansion key: string,
    z: timezone: string,

## [`@a` and `@b` notices](#toc) 

* Alerts
    - a: alert: (list of + (before) or - (after) periods relative to @s: cmd)
    - positive: triggered before dtstart, relevant for dtstart on or after the current time
    - negative: triggered after dtstart, relevant for dtstart on or before the current time
    - each command is a key from options['alerts']

* Beginbys: relevant for dtstart after today

For repeating items, alerts and beginbys are only triggered for unfinished tasks and, when the task is repeating, only for the first unfinished instance. Similarly, pastdue notices for repeating tasks are only triggered for the first unfinished instance. 

An entry without `@r` but with `@s` and `@+` entries will generate instances corresponding to the entered `@s` and to each of the entries in `@+`. 

With an email alert, the item summary is used as the subject and the description as the body of the email. 

## [`@+` repetition](#toc)

*Simple repetition* is supported using a combination of `@s` and `@+` entries. E.g., 

			* my event @s 2018-02-15 3p @+ 2018-03-02 4p, 2018-03-12 9a

would repeat at 3pm on Feb 15, 4pm on Mar 2 and 9am on Mar 12. Note that there is no `@r` entry and that the datetimes from `@s` and from `@+` are combined. With an `@r` entry, on the other hand, only datetimes from the recurrence rule that fall on or after the `@s` entry are used. This replaces and simplifies the old `@r l`, list only, repetition frequency.

## [`@x` expansions](#toc)

The `@x`, *expansion key*, entry is used to specify a key for options to be extracted from the etm configuration settings. E.g., suppose your configuration setting has the following entry for *expansions*:

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

would expand to the following when saved

      * Conflict and Cooperation @s 1/25/2018 9:35am @e 1h15m @a 10m, 3m: d 
        @l Math-Physics Bldg @i Work:Teaching

The `@e`, `@a`, `@l` and `@i` entries from `class` have become the defaults for the event but the default for `@l` has been overridden by the explicit entry.

Note that changing the entry for `expansions` in your configuration settings will only affect items created/modified after the change. When an item is saved, the `@x` entry is replaced by its expansion. 

# [amp keys](#toc)

These keys are only used with `@j` (job) and `@r` (repetition) entries.

## [for use with @ j](#toc)
      a: alert: (list of + (before) or - (after) periods relative to &s: cmd [args])
      b: beginby: integer number of days before &s
      d: description: string
      e: extent: period
      f: finish: datetime
      l: location/context: string
      m: mask: string
      i: job unique id (string)
      p: prerequisites (comma separated list of ids of immediate
         prereqs)
      s: start/due: period relative to @s entry (default 0m)

## [for use with @ r](#toc)
      c: count: integer number of repetitions 
      e: easter: number of days before (-), on (0) or after (+) Easter
      h: hour: list of integers in 0 ... 23
      i: interval: positive integer to apply to frequency, e.g., with
         @r m &i 3, repetition would occur every 3 months
      m: monthday: list of integers 1 ... 31
      M: month number: list of integers in 1 ... 12
      n: minute: list of integers in 0 ... 59
      s: set position: integer
      u: until: datetime 
      w: weekday: list from SU, MO, ..., SA possibly prepended with 
         a positive or negative integer
      W: week number: list of integers in (1, ..., 53)

It is an error in dateutil to specify both `&c` and `&u` since providing both would at best be redundant. A distinction between using `@c` and `@u` is worth noting and can be illustrated with an example. Suppose an item starts at 10am on a Monday and repeats daily using either count, `&c 5`, or until, `&u fri 10a`.  Both will create repetitions for 10am on each of the weekdays from Monday through Friday. The distinction arises if you later decide to delete one of the instances, say the one falling on Wednesday. With *count*, you would then have instances falling on Monday, Tuesday, Thursday, Friday *and Saturday* to satisfy the requirement for a count of five instances. With *until*, you would have only the four instances on Monday, Tuesday, Thursday and Friday to satisfy the requirement that the last instance falls on or before 10am Friday.


# [The TinyDB Data Store](#toc)

All etm item data is stored in a single, *JSON* file using the python data store *TinyDB*. This is a plain text file that is human-readable, but not easily human-editable.  It can be backed up and/or queried using external tools as well as etm itself. Here is an illustrative record:

		  "32": {
		   "c": "shared",
		   "itemtype": "*",
		   "r": [
			{
			 "M": "3",
			 "r": "y",
			 "w": "{W}:2SU"
			}
		   ],
		   "s": "{D}:20100314",
		   "summary": "Daylight saving time begins",
		   "created": "{T}:20160812T2348A"
		  },

    which corresponds to creating the following entry on August 12, 2016 at 23:48 UTC:

        * Daylight saving time begins @s 2010-03-14 @r y &M 3 &w 2SU @c shared

- The unique identifier, `32`, is created automatically by *TinyDB*.
- Two timestamps are automatically created for items: *created*, corresponding to the moment the item was created and, if the item has subsequently been changed, *modified* corresponding to the moment the item was last changed. 

## [Dates, Times and Intervals](#toc)

*Aware* datetime objects have information about the timezone that applies to the object. *Naive* datetimes and dates are missing such timezone information. Aware and naive objects are thus like 'apples and oranges' and cannot be compared. Similarly, dates and datetimes are not comparable. Etm takes care of all the details of dealing with these issues and they need not concern the user.

Why provide for both aware and naive objects? Since naive objects have no timezone information they "float". A reminder to take your meds at 10am and 4pm that uses a *naive* starting datetime will display the reminder at 10am and 4pm in whatever timezone you happen to be. On the other hand, a reminder to phone your friend in Los Angeles at 2pm that uses an *aware* starting datetime with US/Pacific as the timezone, will display the reminder in whatever timezone you happen to be at the local time corresponding to 2pm US/Pacific.

- Dates (necessarily naive) and datetimes (both naive and aware) are suppored along with intervals (analagous to python timedeltas).
- Storage: 
    - Special storage classes have been added to etm's instance of *TinyDB* for date, datetime and interval storage. *Pendulum* date,  datetime and interval objects used by etm are automatically encoded (serialized) as strings when stored in *TinyDB* and then automatically decoded as date, datetime and interval objects when retrieved by etm. 
	- Date serializtions begin with `{D}:` and continue with the `YYYYMMMDD` format of the date. E.g., `{D}:20161023`.
	- Datetime serializations begin with `{T}:` and continue with the `YYYYMMDDTHHmm` format of the datetime. Preserving the *naive* or *aware* state of a datetime object is accomplished by appending either an *N* (naive) or an *A* (aware) to the serialized string. 
	  E.g., `{T}:20181215T2200A`
    - Aware datetimes are converted to UTC when encoded and are converted to the local time when decoded.
    - Naive dates and datetimes are not converted when encoded. When decoded, dates are converted to a datetime corresponding to midnight on the given date and then, along with naive datetimes, given the local timezone.
	- Interval serializations begin with `{I}:` and continue with a string representation of the interval. E.g., `{I}:2h30m`.
- Fuzzy parsing of dates and datetimes is suppored. Examples supposing that it is currently Wed, Jan 4, 2018 and that the local timezone is US/Eastern:
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

		With both a **date** and a **time** specified and with `float` as the timezone, this would be interpreted as `Fri, Jan 5, 2018 2pm`, in whatever happens to be the local timezone, and would be serialized as `{T}:20180105T1400N`. Note the appended `N` to indicate that this is a naive datetime and that the datetime has not been converted.

	- The assumption here is that when a user enters a date, a date is what the user wants. When both a date and time are given, what the user wants is a datetime and, most probably, one based on the local timezone. Less probably, one based on a different timezone and that requires the additon of the `@z` and the timezone. Still less probably, one that floats and this requires the addition of the `@z` and `float`.
	- When an item with an aware `@s` entry repeats, the hour of the repetition instance *ignores* daylight savings time changes. E.g., with

				@s Fri Jan 26 2018 2pm @r m -1FR @z US/Eastern
		the first three repetitions would all be at 2pm even though the first two are EST and the third is EDT: 

				Fri Jan 26 2018 2:00PM
				Fri Feb 23 2018 2:00PM
				Fri Mar 30 2018 2:00PM
- Display:
    - Naive dates are displayed without conversion and without a starting time. 
    - Naive datetimes are displayed without conversion.
    - Aware datetimes are converted to the current local timezone. E.g., in the US/Eastern timezone, `fri 2p` would display as starting at 2pm on Jan 5 if the computer is still in the Eastern timezone but would display as starting at 11am if the computer had been moved to the Pacific timezone. Similarly, `@s fri 2p @z US/Pacific` would display as starting at 5pm if the computer were in the Eastern timezone.
    - When *editing* an item with an aware datetime, the datetime is displayed in the timezone specified in `@z`. 
    - Datetimes are rounded to the nearest minute for display.

## [The relevant datetime of an item](#toc)

Used in search and index views.

- Finished tasks: the datetime given in `@f`.
- Finished jobs in unfinished tasks: the datetime given in `&f`.
- Inbox entries: the current date.
- Records and unfinished tasks without an `@s` entry: *None*
- Other items with `@s` entries:
    - Non-repeating events, unfinished tasks and records: the datetime given in `@s`. 
    - Unfinished jobs: the datetime given in `&s`.
    - Repeating events: the datetime of the first instance falling on or after the current date or, if none, the datetime of the last instance. 
    - Repeating unfinished tasks with `@o r` (restart) or `@o k` (keep - the default): the datetime given in `@s`. This datetime is automatically updated when an instance is completed to the due datetime of the next instance.
    - Repeating unfinished tasks with `@o s` (skip): the datetime of the first instance falling on or after the current date. 

# [Views](#toc)

View shortcut keys: a)genda, h)istory, i)ndex, n)ext, q)uery and t)ags.

The recommended terminal size is a minimum of 30 rows by 60 columns. 

## [Agenda](#toc)

The weekly *Agenda - Schedule* and *Agenda - Busy* views are synchronized so that switching from one of these views to another always displays the same week. Pressing "a" activates agenda view and, once active, toggles between schedule and busy. 

### [Schedule](#toc)

- Scheduled items, grouped and sorted by week and day

						 2018 Week 7: Feb 12 - 18
		  Mon Feb 12
			* Safety Meeting                         3:30-5pm
		  Wed Feb 14
			* Valentine's Day
			* Ball machine                           10-11am
			* Valentine's dinner                   6:30-9:30pm
		  Thu Feb 15
			* cleaners                               10:30am
			* Manish                                  2-4pm
			* Pottery Speaker's  Reception            6-8pm
		  Fri Feb 16
			* Tennis                                9:30-11am
			* Lunch with Burk                      12:30-2:30pm
		  Sun Feb 18
			* Ride to Angies                         9am-1pm


- The first line shows the selected week.
- Subsequent lines show scheduled items grouped and sorted by date and time.
- Weeks are displayed sequentially. If there is nothing to display for the week, then the display would show "Nothing scheduled". 
- Starting from the top, the display for a day includes the following:
    - All day events (date rather than datetime starting time), if any.
    - *For the current date (today) only*:
        - Inbox entries, if any, highlighted using the inbox color.
        - Pastdue tasks, if any, with the number of days that have passed since the task was due using the display character `<` and highlighted using the pastdue color. 
        - Beginning soon notices, if any, with the number of days remaining until the starting date of the item using the display character `>` and highlighted using the beginning soon color.
        > Note that the items included for the current date are those from the old *agenda* view.
    - Datetime events, notes, records and unfinished tasks sorted by `@s` together with finished tasks sorted by `@f` with the starting time  displayed in the 2nd column. For events with *extent*, the ending time is also displayed. For tasks or records with *extent*, the extent period is also displayed. 
    - Date only tasks.
    - Date only records.

### [Busy](#toc)

- Hours in the day that are partially or wholly "busy" are filled using the character `#`.
- Hours in which a conflict occurs are filled with the charaters `###`.


                           2018 Week 50: Dec 10 - 16
                   Mo 10  Tu 11  We 12  Th 13  Fr 14  Sa 15  Su 16
                   -----------------------------------------------
            12am     .      .      .      .      .      .      .
                     .      .      .      .      .      .      .
                     .      .      .      .      .      .      .
                     .      .      .      .      .      .      .
                     .      .      .      .      .      .      .
                     .      .      .      .      .      .      .
             6am     .      .      .      .      .      .      .
                     .      .      .      .      .      .      .
                     .      .      .      .      .      .      .
                     .      .      .      .      #      .      .
                     .      .      .      .      #      .      .
                     .      .      #      .      .      .      .
            12pm     .      #      #      .      #      .      .
                     .      #      .      .     ###     .      .
                     .      #      .      #      #      .      .
                     .      .      .      #      .      .      .
                     .      .      .      .      .      .      .
                     .      .      .      .      .      .      .
             6pm     .      .      #      #      .      .      #
                     .      .      #      #      .      .      #
                     .      .      #      #      .      .      #
                     .      .      .      #      .      #      #
                     .      .      .      .      .      #      .
                     .      .      .      .      .      .      .
                   -----------------------------------------------
           total     0     180    180    300    210    120    180


## [Relevant](#toc)

All items with datetimes ordered by relevant datetime and grouped by year, week and week day. Displays item type, summary and relevant datetime. 

## [Next](#toc)

- Unfinished tasks and jobs that are undated (without `@s` entries) grouped and sorted by *location* and then *priority*. 
- As tasks and jobs are finished, they are removed from this view and added to *Done* using the completion datetime.

## [Index](#toc)

- All items, grouped and sorted by their *index* entries and then their 
  *relevant datetime*. 
- Items without `@i` entries are listed last under *~none*.


## [History](#toc)

- All items, sorted by the created (c) and last modified (m) datetimes, most recent first.

		 * Cassells for dinner                       2018-12-22 c
		 * Squires for dinner                        2018-12-22 m
		 * Jamie and Kelley with Ellen               2018-12-22 m
		 * Will and Max for dinner                   2018-12-22 c
		 ✓ Friday schedule                           2018-12-22 c
		 * Service Experts                           2018-12-22 m
		 * Mensa Lite                                2018-12-22 c
		 * Tennis?                                   2018-12-22 c
		 * Jamie & YuLing UA2333                     2018-12-22 c
		 * Service Experts                           2018-12-21 c
		 * Jamie and Kelley with Ellen               2018-12-18 c

## [Tags](#toc)

Tagged items grouped and sorted by tag.

## [Query](#toc)

Analagous to the old custom view. Used to issue queries against the data store and display the results. 

# [Work Flow](#toc)

## [Editing an existing item](#toc)

- Pressing Return with an item selected shows details:

		- Tuesday schedule @s 2018-12-17 @z US/Eastern
		@f 2018-12-19 2:17pm
		@c dag

		---
		doc_id:  1199
		created: 2018-12-21 5:25pm
        modified: none

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
        |   *: event       -: task          %: record              |
        |   ?: someday     !: inbox                                |

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
