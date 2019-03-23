# etm
<!-- ![event and task manager](https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etmlogo.png) -->
<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etmlogo.png" alt="etm" title="event and task manager" />

*etm* offers a simple way to manage your events, tasks and other reminders. Rather than filling out fields in a form to create or edit reminders, a simple text-based format is used. This is the fourth generation of a project that began in 2009. 

Each reminder in *etm* begins with a *type character* followed by a brief *summary* of the item and then, perhaps, by one or more *@key value* pairs to specify other attributes of the reminder. Mnemonics are used to make the keys easy to remember, e.g, @s for starting datetime, @l for location, @d for description and so forth.

There are 4 types of reminders and associated *type characters*: task (**-**),event (**\***), record (**%**) and inbox (**!**). See [Item Types](#item-types) for details about the four item types and [Options](#options) for details about possible attributes. Here are some examples.

## [Simple reminders](#etm)

* A task (**-**): pick up milk. 

		- pick up milk
* An event (**\***): have lunch with Burk [s]tarting next Tuesday at 12pm and [e]xtending for 90 minutes, i.e., lasting from 12pm until 1:30pm.

        * Lunch with Burk @s tue 12p @e 90m

* A record (**%**): a favorite Churchill quotation that you heard at 2pm today with the quote itself as the [d]escription.

        % Give me a pig - Churchill @s 2p @d Dogs look up at you. Cats look 
          down at you. Give me a pig - they look you in the eye and treat you
          as an equal.
* A task (**-**): build a dog house, with component [j]obs.

		- Build dog house @j pick up materials @j cut pieces @j assemble
		  @j sand @j paint
* Inbox (**!**): meet Alex for coffee Friday. This can be changed to an event when the time is confirmed by replacing the **!** with an **\***.

        ! Coffee with Alex @s fri ? @e 1h

## [Repetition](#etm)

* An appointment (event) for a dental exam and cleaning at 2pm on Feb 5 and then again [@+] at 9am on Sep 3.

        * dental exam and cleaning @s 2p feb 5 2019 @e 45m @+ 9am Sep 3 2019
* Christmas (an all day event) [r]epating (y)early on Dec 25.

        * Christmas @s 2015/12/25 @r y
* Get a haircut (a task) on the 24th of the current month and then [r]epeatedly at (d)aily [i]ntervals of (14) days and, [o]n completion, (r)estart from the last completion date:

        - haircut @s 24 @r d &i 14 @o r
* Take out trash (at task) on Mondays but if the task becomes [o]verdue, (s)kip the pastdue reminders.

        - Take out trash @s mon @r w @o s

* A sales meeting (an event) [r]epeating m)onthly on [w]eekdays that are either the first or third Tuesdays in the month.

        * sales meeting @s tue 9a @e 45m @r m &w 1tu, 3tu

## [More complex repetition](#etm)

* Take a prescribed medication daily [s]tarting at 12am Monday and [r]epeating (d)aily at [h]ours 10am, 2pm, 6pm and 10pm [u]ntil 12am on Friday. 

        * take Rx @s mon @r d &h 10, 14, 18, 22 &u fri
* Move the water sprinkler every thirty minutes (@r n &i 30) between 2pm and 4:30pm (&h 14, 15, 16) on Sundays (&w SU) from April through September (&M 4, 5, 6, 7, 8, 9).

        * Move sprinkler @s sun @r n &i 30 &w SU &h 14, 15, 16, 17 
		  &M 4, 5, 6, 7, 8, 9
* Presidential election day every four years on the first Tuesday after a Monday in November (a Tuesday whose month day falls between 2 and 8).

        * Presidential Election Day @s 2012-11-06
          @r y &i 4 &M 11 &m 2, 3, 4, 5, 6, 7, 8 &w TU
* Good Friday each year 2 days before [E]aster Sunday.

        * Good Friday @s 1/1/2015 @r y @E -2
* Friday tennis at 9:30am in November, December, January and February and at 8am in the other months:

        * Friday tennis @s 2019-01-01 6a @e 90m
          @r m &w fr &M 1, 2, 11, 12 &h 9 &n 30
          @r m &w fr &M 3, 4, 5, 6, 7, 8, 9, 10 &h 8 &n 0

* Payday on the last week day of each month. The &s -1 part of the entry extracts the last (-1) date which is both a weekday and falls within the last three days of the month):

        * payday @s 1/1 @r m &w MO, TU, WE, TH, FR &m -1, -2, -3 &s -1

## [Editing](#etm) ##

<!-- [![etm: creating a new item](http://img.youtube.com/vi/62cps01Rh50/0.jpg)](http://www.youtube.com/watch?v=62cps01Rh50 "creating a new item") -->

Etm offers several conveniences when creating or modifying an item.

* Fuzzy parsing of dates and date times. Supposing it is currently Wed, Feb 13 2019:
    * `@s 2` would be interpreted as the date Feb 2, 2019.
    * `@s 2p` would be interpreted as the datetime 2pm on Wed Feb 13 in the local timezone.
    * `@s 2p fri` would be interpreted as the datetime 2pm Fri, Feb 15 in the local timezone.
    * `@s 2p fri @z US/Pacific` would be interpreted as the datetime 2pm Fri, Feb 15 in the Pacific timezone but would be displayed as the corresponding time in the local timezone.
    * `@s 2p fri @z float` would be interpreted as the naive datetime 2pm Fri, Feb 15 and would be displayed as such in whatever happens to be the local timezone.
* Automatic completion for elements you have used before including @z (timezone), @c (calendar), @t (tags), @i (index), @l (location), @n (attendees) and @x (expansion). E.g. when entering @z, you can choose from any timezone you have previously used. 

# [Details](#etm)

## [Installation/Deinstallation](#etm)

### [Installation](#etm)

<!--  [![etm: installing etm in a virtual environment](http://img.youtube.com/vi/fEPPG82AH7M/0.jpg)](http://www.youtube.com/watch?v=fEPPG82AH7M "installing etm in a virtual environment") -->

Setting up a virtual environment for etm is recommended. The steps for OS/X or linux are illustrated below. For details see [python-virtual-environments-a-primer](https://www.google.com/url?q=https%3A%2F%2Frealpython.com%2Fpython-virtual-environments-a-primer%2F&sa=D&sntz=1&usg=AFQjCNFh7QpJQ4rPCDjZ1eLrV1BRCCpSmw).

Open a terminal and begin by creating a new directory/folder, say `etm-pypi` in your home directory, for the virtual environment:

        $ mkdir ~/etm-pypi
        $ cd ~/etm-pypi
Now continue by creating the virtual environment (python3 is required):

        $ python3 -m venv env
After a few seconds you will have an `./env` directory. Now activate the virtual environment:

        $ source env/bin/activate
The prompt will now change to something containing `(env)` to indicate that the virtual environment is active. Updating pip is now recommended:

        (env) $ pip install -U pip
Note that this invokes `./env/bin/pip`. Once this is finished, use pip to install etm:

        (env) $ pip install -U etm-dgraham
This will install etm and all its requirements in `./env/lib/python3.x/sitepackages` and will also install an executable called `etm` in `./env/bin`.

By the way, the suggested terminal size for etm is 60 (columns) by 32 or more (rows). The default color scheme is best with a dark terminal background. A scheme better suited to light backgrounds can be set in `cfg.yaml`.

Before you start etm, think about where you would like to keep your personal data and configuration files. The default is to use `~/etm-pypi` or whatever directory you created for your virtual environment as your etm *home* directory. If this is not what you want, you can just give the path for whatever directory you would like to use when you start etm, e.g.,

        (env) $ etm ~/Documents/etm

Considerations:

* If more than one person will be using etm on the same computer, you might want to have different *home* directories for each user.
* If you want to use etm on  more than one computer and use Dropbox, you might want to use `~/Dropbox/etm` to have access on each of your computers.

Whatever *home* directory you choose, running etm for the first time will add the following to that folder.

        home/
            backups/
            logs/
            cfg.yaml
            db.json
Here `cfg.yaml` is your user configuration file and `db.json` contains all your etm reminders. The folders `backups/` and `logs/` contain, respectively, the 5 most recent daily backups of your `db.json` and `cfg.yaml` files. The folder `logs` contains the current `etm.log` file and the 5 most recent daily backus.

The file `cfg.yaml` can be edited and the options are documented in the file.

### [Deinstallation](#etm)

If you should ever want to deinstall etm, first deactivate the virtual environment, if necessary, by changing to the virtual environment directory and entering

        (env) $ deactivate

You can now simply delete the virtual environment directory and, if you have additional *home* directories, by deleting each of them. One of the many advantages of the virtual environment is that all installations are local to that environment and removing the directory, removes every trace.

## [Item Types](#etm)

### [event](#etm)

Type character: **\***

An event is something that happens at a particular date or datetime without any action from the user. Christmas, for example, is an event that happens whether or not the user does anything about it.


- The `@s` entry is required and can be specified either as a date or as a datetime. It is interpreted as the starting date or datetime of the event. 
- If `@s` is a date, the event is regarded as an *occasion* or *all-day* event. Such occasions are displayed first on the relevant date. 
- If `@s` is a datetime, an `@e` entry is allowed and is interpreted as the extent or duration of the event - the end of the event is then given implicitly by starting datetime plus the extent and this period is treated as busy time. 

Corresponds to VEVENT in the vcalendar specification.

### [task](#etm)

Type character: **-**

A task is something that requires action from the user and lasts, so to speak, until the task is completed and marked finished. Filing a tax return, for example, is a task. 

- The `@s` entry is optional and, if given, is interpreted as the date or datetime at which the task is due. 
    - Tasks with an `@s` datetime entry are regarded as pastdue after the datetime and are displayed in *Agenda View* on the relevant date according to the starting time. 
    - Tasks with `@s` date entry are regarded as pastdue after the due date and are displayed in *Agenda View* on the due date before all items with datetimes.
    - Tasks that are pastdue are also displayed in *Agenda View* on the current date using the type character `<` with an indication of the number of days that the task is past due.
- Tasks without an `@s` entry are to be completed when possible and are sometimes called *todos*. They are regarded as *next* items in the *Getting Things Done* terminology and are displayed in *Next View* grouped by @l (location/context).
- Jobs
    - Tasks, both with and without @s entries can have component jobs using @j entries.  
    - For tasks with an @s entry, jobs can have an &s entry to set the due date/datetime for the job. It is entered as a timeperiod relative to  the starting datetime (+ before or - after) for the task. Zero minutes is the default when &s is not entered.
    - For tasks with an @s entry, jobs can also have &a, alert, and &b, beginning soon, notices. The entry for &a is given as a time period relative to &s (+ before or - after) and the entry for &b is a positive integer number of days before the starting date/time to begin displaying "beginning soon" notices. The entry for @s in the task becomes the default for &s in each job.  E.g., with

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

### [Journal](#etm)

Type character: **%**

A record of something that the user wants to remember. The userid and password for a website would be an example. A journal entry for vacation day is another example. 

- The `@s` is optional and, if given, is interpreted as the datetime to which the record applies. 
- Records without @s entries might be used to record personal information such as account numbers, recipies or other such information not associated with a particular datetime. They are displayed in the *Journal* view
- Records with @s entries associate the record with the datetime given by @s. A vacation log entry, for example, might record the highlights of the day given by @s. They are displayed in the *Agenda* view as well as the *Journal* view.

Corresponds to VJOURNAL in the vcalendar specification.

### [inbox](#etm)

Type character: **!**

An inbox item can be regarded as a task that is always due on the current date. E.g., you have created an event to remind you of a lunch meeting but need to confirm the time. Just record it using **!** instead of **\*** and the entry  will appear highlighted in the agenda view on the current date until you confirm the starting time. 

Corresponds to VTODO in the vcalendar specification.

### [Internal types](#etm)

These are generated automatically by *etm*.

#### [beginning soon](#etm)

Type character: **>**

For unfinished tasks and other items with `@b` entries, when the starting date given by `@s` is within `@b` days of the current date, a warning that the item is beginning soon appears on the current date together with the item summary and the number of days remaining.

#### [past due](#etm)

Type character: **<**

When a task is past due, a warning that the task is past due appears on the current date together with the item summary and the number of days past due. 

#### [waiting](#etm)

Type character: **+**

When a task job has one or more unfinished prerequisites, it is displayed using **+** rather than **-**.

#### [finished](#etm)

Type character: **✓**

When a task or job is finished, it is displayed on the finished date using **✓** rather than **-**. 

## [Item options](#etm)

### [@ keys](#etm) 

@ followed by a character from the list below and a value appropriate to the key is used to apply attributes to an item. E.g.,

            @s mon 9a
would specify the the starting datetime for the item is 9am on the Monday following the current date.

*  @+: include: list of datetimes to include
*  @-: exclude: list of datetimes to exclude
*  @a: alert (list of + (before) or - (after) periods: list of commands)
*  @b: beginby: integer (number of days before)
*  @c: calendar: string
*  @d: description: string
*  @e: extent: period
*  @f: finished: datetime
*  @g: goto: string (url or filepath)
*  @h: history: (for repeating tasks, a list of the most recent completion datetimes)
*  @i: index: colon delimited string
*  @j: job summary: string, optionally followed by job &key entries
*  @l: location/context: string
*  @m: mask: string stored in obfuscated form
*  @n: attendee: 'name <emailaddress>' string 
*  @o: overdue: character from (r) restart, (s) skip or (k) keep
*  @p: priority: integer from 0 (none), 1 (low), 2 (normal), 3 (high), 4 (urgent)
*  @r: repetition frequency: character from (y)early, (m)onthly, (w)eekly,  
  (d)aily, (h)ourly or mi(n)utely, optionally followed by repetition &-key entries
*  @s: starting: date or datetime
*  @t: tag: string
*  @u: usedtime: period: datetime
*  @x: expansion key: string
*  @z: timezone: string

### [& keys](#etm)

& followed by a character from one of the lists below. These keys are only used with @j (job) and @r (repetition) entries.

#### for use with @j

*  &s: start/due: period relative to @s entry (default 0m)
*  &a: alert: list of + (before) or - (after) periods relative to &s: list of cmd names from the users configuration file
*  &b: beginby: integer number of days before &s
*  &d: description: string
*  &e: extent: period
*  &f: finish: datetime
*  &l: location/context: string
*  &m: mask: string stored in obfuscated form
*  &i: job unique id (string)
*  &p: prerequisites (comma separated list of ids of immediate prereqs)
*  &u: usedtime: period: datetime

#### for use with @r

*  &c: count: integer number of repetitions 
*  &E: easter: number of days before (-), on (0) or after (+) Easter
*  &h: hour: list of integers in 0 ... 23
*  &i: interval: positive integer to apply to frequency, e.g., with @r m &i 3, repetition would occur every 3 months
*  &m: monthday: list of integers 1 ... 31
*  &M: month number: list of integers in 1 ... 12
*  &n: minute: list of integers in 0 ... 59
*  &s: set position: integer
*  &u: until: datetime 
*  &w: weekday: list from SU, MO, ..., SA possibly prepended with a positive or negative integer
*  &W: week number: list of integers in (1, ..., 53)


### [Option notes](#etm)

* @a alerts and @b beginbys
    * With an email alert, the item summary is used as the subject and emails are sent to each attendee listed in an @n entry. The content of the body of the emails is a option that can be set in the user's configuration file. 
    * For repeating items, alerts and beginbys are only triggered for unfinished tasks and, when the task is repeating, only for the first unfinished instance. Similarly, pastdue notices for repeating tasks are only triggered for the first unfinished instance.
* Repetition
    * Using @s, @r and, optionally, @+. Datetimes from @+, if any, are added to the datetimes generated from the @r entry which fall on or after the @s datetime. Note that the datetime from @s will only be included if it matches one generated by the @r entry or by one included in @+.  

            * my event @s 2018-02-15 3p @r d &h 18 @+ 2018-03-02 4p
        would repeat daily at 6pm starting Feb 15 and at 4pm on Mar 2, *but not* at 3pm on Feb 15. 
    * Using @s and, optionally, @+ (but without @r). Datetimes from @+, if any, are added to @s. E.g., 

            * my event @s 2018-02-15 3p @+ 2018-03-02 4p
        would repeat at 4pm on Mar 2 *and* 3pm on Feb 15.
    * Using &c and &u in @r. It is an error in *dateutil* to specify both &c (count) and &u (until) since providing both would at best be redundant. A distinction between using @c and @u is worth noting and can be illustrated with an example. Suppose an item starts at 10am on a Monday and repeats daily using either count, &c 5, or until, &u fri 10a.  Both will create repetitions for 10am on each of the weekdays from Monday through Friday. The distinction arises if you later decide to delete one of the instances, say the one falling on Wednesday, using @-. With *count*, you would then have instances falling on Monday, Tuesday, Thursday, Friday *and Saturday* to satisfy the requirement for a count of five instances. With *until*, you would have only the four instances on Monday, Tuesday, Thursday and Friday to satisfy the requirement that the last instance falls on or before 10am Friday.
* @m masked entry. These entries are encoded in the database in an obfuscated or masket format but decoded when displayed in etm itself. A key, *secret*, specified in the user configuration file is used for the encoding/decoding.
* @x expansions. The `@x`, *expansion key*, entry is used to specify a key for options to be extracted from the etm configuration settings. E.g., suppose your configuration setting has the following entry for *expansions*:

            expansions:
                tennis: '@e 1h30m @a 30m, 15m: d @i personal:tennis'
                ...
    Then entering `@x tennis` in the following item

            * Conflict and Cooperation @s 1/25/2018 9:35am @x class 
    etm would offer to replace *@x class* with the corresponding entry from expansions, *@e 1h30m @a 30m, 15m: d @i personal:tennis*.


