# etm: event and task manager
<!-- ![event and task manager](https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etmlogo.png) -->
<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etmlogo.png" alt="etm" title="event and task manager" />

# Overview

## [Reminders](#etm)

*etm* offers a simple way to manage your events, tasks and other reminders. 

Rather than filling out fields in a form to create or edit reminders, a simple text-based format is used. Each reminder in *etm* begins with a *type character* followed by a brief *summary* of the item and then, perhaps, by one or more *@key value* pairs to specify other attributes of the reminder. Mnemonics are used to make the keys easy to remember, e.g, @s for starting datetime, @l for location, @d for description and so forth.

The 4 types of reminders in etm with their associated type characters:

* task: **-** 
* event: **\***
* record: **%**
* inbox: **!** 

See [Item Types](#item-types) for details about these item types and [Options](#options) for details about possible attributes.


### examples

* A task (**-**): pick up milk. 

		- pick up milk
* An event (**\***): have lunch with Burk [s]tarting next Tuesday at 12pm and [e]xtending for 90 minutes, i.e., lasting from 12pm until 1:30pm.

        * Lunch with Burk @s tue 12p @e 90m
* A record (**%**): a favorite Churchill quotation that you heard at 2pm today with the quote itself as the [d]escription.

        % Give me a pig - Churchill @s 2p @d Dogs look up at 
          you. Cats look down at you. Give me a pig - they 
          look you in the eye and treat you as an equal.
* A task (**-**): build a dog house, with component [j]obs.

        - Build dog house @j pick up materials @j cut pieces 
          @j assemble @j sand @j paint
* Inbox (**!**): meet Alex for coffee Friday. This can be 
  changed to an event when the time is confirmed by 
  replacing the **!** with an **\***.

        ! Coffee with Alex @s fri ? @e 1h
* An appointment (event) for a dental exam and cleaning at 2pm on Feb 5 and then again [@+] at 9am on Sep 3.

        * dental exam and cleaning @s 2p feb 5 2019 @e 45m 
          @+ 9am Sep 3 2019

### text entry versus forms

* Text entry removes the need to hunt for and click in the relevant entry box and allows you to keep your fingers on the keyboard.
* Text entry supports the full flexibility of the superb Python *dateutil* package. Consider, for example, creating a reminder for Presidential election day which repeats every 4 years on the first Tuesday after a Monday in November (a monthday falling between 2 and 8). In *etm*, this event would be

        * Presidential election day @s nov 3 2020 @r y &i 4 &M 11 
          &m 2, 3, 4, 5, 6, 7, 8 &w tu
  Try this with a form based calendar application.

### timely and unobtrusive entry assistance

#### just in time entry prompts and feedback


Let's create the election day reminder to illustrate the *etm* prompt/feedback process. In the illustrations below, the prompt appears above the horizontal line and your entry appears below the horizontal line with the position of the cursor indicated by the underscore character.

Begin by pressing `N` to create a new reminder and notice that *etm* automatically prompts you for the item type character

        item type
        Choose a character from * (event), - (task), % (record)
        or ! (inbox)

        ────────────────────────────────────────────────────────────
        _
Enter an "\*" to create an event and *etm* prompts you for the event summary

        summary
        brief item description. Append an '@' to add an option.

        ────────────────────────────────────────────────────────────
        *_

Enter the summary followed by an `@` and *etm* automatically prompts you with the required and available `@-keys`

        @-key
        required: @s (start)
        available: @+ (include), @- (exclude), @a (alerts),
        @b (beginby), @c (calendar), @d (description),
        @e (extent), @g (goto), @i (index), @l (location),
        @m (mask), @n (attendee), @o (overdue),
        @r (repetition frequency), @s (start), @t (tag),
        @u (used time), @x (expansion), @z (timezone)
        ────────────────────────────────────────────────────────────
        * Presidential election day @_

You see that "@s" is required, so enter the "s" and *etm* prompts you for the value for the start option

        start
        starting date or datetime

        ────────────────────────────────────────────────────────────
        * Presidential election day @s_

Enter a date and *etm* will display its interpretation of your entry as you type

        start
        Sun Nov 1 2020

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20_

Now append an @ to see the prompt for options

        @-key
        available: @+ (include), @- (exclude), @a (alerts),
        @b (beginby), @c (calendar), @d (description),
        @e (extent), @g (goto), @i (index), @l (location),
        @m (mask), @n (attendee), @o (overdue),
        @r (repetition frequency), @t (tag), @u (used time),
        @x (expansion), @z (timezone)
        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @_

We want to repeat so enter an "r"

        repetition frequency
        repetition frequency: character from (y)early,
        (m)onthly, (w)eekly, (d)aily, (h)ourly or
        mi(n)utely.

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r_

Add a "y" for yearly and an "&" to see the prompts for repetition options.

        repetition &-key
        repetition &-keys: &i (interval), &m (monthdays),
        &E (easterdays), &h (hours), &M (months),
        &n (minutes), &w (weekdays), &W (week numbers),
        &c (count), &u (until), &s (set positions)

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &_


Enter "i" to see what "interval" means 

        interval
        Interval requires a positive integer (default 1) that
        sets the frequency interval. E.g., with frequency w
        (weekly), interval 3 would repeat every three weeks.

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &i_

We want to repeat every 4 years so enter "4" followed by another "&" to see other options. [The display for *repetition &-keys* is unchanged from above and thus omitted here.] Then enter "M" to see what "months" means

        months
        months: a comma separated list of integer month numbers
        from 1, 2, ..., 12

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &i 4 &M_

We want November, so enter 11 followed by an "&" for other options. Then enter "m" to see what "monthdays" means

        monthdays
        monthdays: a comma separated list of integer month days
        from  (1, 2, ..., 31. Prepend a minus sign to count
        backwards from the end of the month. E.g., use  -1 for
        the last day of the month.

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &i 4 &M 11 &m_ 

We want a monthday between 2 and 8 so enter these monthdays followed by "&" for options. Then enter "w" to see what "weekdays" means

        weekdays
        weekdays: a comma separated list of English weekday
        abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend
        an integer to specify a particular weekday in the month.
        E.g., 3WE for the 3rd Wednesday or -1FR, for the last
        Friday in the month.

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &i 4 &M 11 
        &m 2, 3, 4, 5, 6, 7, 8 &w_

We want a Tuesday, so add "tu" to complete the entry. To check the entry, press ^R to show repetitions

            ┌─────| First 5 repetitions |──────┐
            │                                  │
            │ from Sun Nov 1 2020:             │
            │   Tue Nov 3 2020                 │
            │   Tue Nov 5 2024                 │
            │   Tue Nov 7 2028                 │
            │   Tue Nov 2 2032                 │
            │   Tue Nov 4 2036                 │
            │                                  │
            │           <    OK    >           │
            │                                  │
            └──────────────────────────────────┘

These are the first 5 repetitions on or after Nov 1 2020. They appear to be correct, so press ^S to save the reminder.


General observations:

* The general structure of this reminder is

        * Presidential election day 
            @s nov 1 20 
            @r y 
                &i 4 
                &M 11 
                &m 2, 3, 4, 5, 6, 7, 8 
                &w tu
   The `@s` and `@r` entries provide attributes of the event itself and the `&i`, `&M`, `&m` and `&w` entries provide attributes of the `@r` entry. More than one `@r` entry can be provided and each can have its own set of `&-key` entries with each `&-key` applying to the last `@r` entry which precedes it. 
* *@-keys* can generally be entered in any order provided that `@s` is entered before any options that require it. *&-keys* can also be entered in any order.
* The prompts provide "just in time" information relevant to the entry you are typing and need only be consulted if you are uncertain about your entry. With a little experience, most reminders can be completed without a glance at the prompt.


#### Fuzzy parsing of datetimes

Whenever *etm* expects a datetime entry as, for example, when you are entering an `@s` starting datetime, it applies fuzzy parsing to your entry.  Suppose it is Dec 17 2019, your computer is in the Eastern timezone and you have just entered `@s` for your lunch event

        start
        starting date or datetime

        ────────────────────────────────────────────────────────────
        * lunch @s_

If you enter `1`, *etm* will interpret it as 1am on the current date in the local timezone:

        start
        Tue Dec 17 2019 1:00am EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1_

Adding `p` changes the interpretation to 1pm

        start
        Tue Dec 17 2019 1:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p_

Now start adding 'fri' by appending an 'f'

        start
        '1p f' is incomplete or invalid

        ────────────────────────────────────────────────────────────
        * lunch @s 1p f_

and *etm* will complain that the entry is now either incomplete or invalid. Add the remaining 'ri'

        start
        Fri Dec 20 2019 1:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p fri_

and *etm* understands that you want the coming Friday, Dec 20. Now suppose that you will be in California on Friday and you want Pacific, not Eastern time. Then add an entry for `@z`

        start
        local datetime: Fri Dec 20 2019 4:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p fri_ @z US/Pacific

Note that `local datetime` is now prepended to the result which is still displayed in the local timezone, since that is the location of your computer, but the time has changed to `4:00pm EST` which, of course, is the same time as `1:00pm PST`. [*etm* always displays times in the local time zone.]

What if you had entered the 'fri' first?

        start
        Fri Dec 20 2019

        ────────────────────────────────────────────────────────────
        * lunch @s fri

Here *etm* supposes again that you want the coming Friday, Dec 20 but without a time being specified, it is interpreted as a date rather than a datetime and thus without a timezone. Add the `1p` and timezone the result will be the same as before.

As a final illustration, suppose you want to be reminded of lunch at 1pm in whatever timezone you happen to be, i.e., you want the datetime to float to the local timezone. Add the `@z`

        timezone
        a timezone entry such as 'US/Eastern' or 'Europe/Paris'
        or 'float' to specify a naive/floating datetime

        ────────────────────────────────────────────────────────────
        * lunch @s fri 1p @z
and note that supplying 'float' as the timezone will do the trick

        start
        Fri Dec 20 2019 1:00pm

        ────────────────────────────────────────────────────────────
        * lunch @s fri 1p_ @z float
The datetime now appears without either the 'local datetime' prefix or the 'EST' suffix which reveals that it is a naive/floating datetime.


The assumption here is that when a user enters a date, a date is what the
user wants. When both a date and time are given, what the user wants
is a datetime and, most probably, one based on the local timezone. Less
probably, one based on a different timezone and that requires the additon
of the `@z` and timezone. Still less probably, one that floats and this
requires the addition of the `@z` and 'float'.


#### tab completion

Some optional attributes that can be used in reminders can be tedious to enter either because they are lengthy or because they are used often and typographical errors would be problematic. These attributes include the following: 

* *@g*: goto url or filepath. In the latter case, the system default application is used to open the filepath, e.g., on my macbook the system default for files ending in `.py` is to open them in MacVim. In the former case, the url will be opened in the default browser. In either case, a typo would likely render the link useless.

* *@l*: location/context. In the *do next* view, `location` is used to organize undated tasks. Using `@l errands` in one task and `@l erands` in another would cause these tasks to be grouped separately.

* *@i*: index - colon delimited string. In both the *index* and the *used time* views, the index entry is used to group and aggregate entries. Using `@i jsmith:project a` in one entry and `@i jsmth:project a` in another would cause these these entries to be grouped and aggregated erroneously. 

* *@n*: attendee. string using "[name:] address" format. If "address" begins with exactly 10 digits followed by an "@" it is treated as a mobile phone number. Otherwise it is treated as an email address. The optional "name:" can be used to facilitate autocompletion. Attendee entries are used in both email and text alerts. 

* *@z*: timezone. `@z Europe/Paris` is a valid timezone but `@z EU/Paris` isn't.

Other tracked attributes include *@c* (calendar) and *@t* (tag).

For these attributes, etm keeps a record of each usage. I.e., for each record in your *etm* database, if the record includes a tracked attribute that has not already been included in the list of completions, then that attribute will be added. E.g., if you create an item containing

        @n joe: jsmith457@gmail.com
  and '@n joe: jsmith457@gmail.com' is not already in the list of completions, then it will be added.

When you next create a reminder and enter `@n `, *etm* will pop up a sorted list of every item in the completion list that begins with `@n`. You can use the up and down cursor keys to move through this list or you can continue typing to limit the possible completions, e.g., after entering `@n joe` only those completions that start with `@n joe` would still be displayed. When you have selected the completion you want, press the space bar to insert the completion in your entry.


## [Views](#etm)


_etm_ has several ways of viewing entries. This are listed below by the shortcut key used to activate the view. E.g., pressing “a” activates _Agenda_ view.

  * a: Agenda
  * b: Busy
  * c: Completed
  * d: Do Next
  * f: Forthcoming
  * h: History
  * i: Index
  * r: Records
  * t: Tags
  * u: Used Time or U: Used Time Summary

### a] Agenda View
                        Dec 2 - 8, 2019 #49 
        Mon Dec 2
            * Corolla 
            * Tennis                                   8am 
        Tue Dec 3 (Today)
            < Subaru Outback license renewal            -2 
            > Fri tennis                                13 
            > Tue tennis                                13 
        Wed Dec 4
            * Tennis                                   8am 
            * Candlelight dinner                   5:30-9:30pm 
        Thu Dec 5
            * cleaners                                1:30pm 
        Sat Dec 7
            * Breakfast buffet                    10:15am-1:15pm 
        Sun Dec 8
            - Hair cut                                 3pm 
            * Cassells for dinner and tree            6-10pm 


### b] Busy View

                          Dec 2 - 8, 2019 #49 
              Mo 2   Tu 3   We 4   Th 5   Fr 6   Sa 7   Su 8  
              _____  _____  _____  _____  _____  _____  _____
        12am    .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
        6am     .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      #      .  
                .      .      .      .      .      #      .  
        12pm    .      .      .      .      .      #      .  
                .      .      .      .      .      #      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
                .      .      #      .      .      .      .  
        6pm     .      .      #      .      .      .      #  
                .      .      #      .      .      .      #  
                .      .      #      .      .      .      #  
                .      .      #      .      .      .      #  
                .      .      .      .      .      .      .  
                .      .      .      .      .      .      .  
              _____  _____  _____  _____  _____  _____  _____
        total   0      0     240     0      0     180    240 


### c] Completed View

                        Dec 2 - 8, 2019 #49 
        Tue Dec 3 (Today)
            ✓ Tue tennis 1/1/1: request dates          1pm 
            ✓ Fri tennis 1/1/1: request dates          1pm 

While the views differ in many respects, they also share some common aspects:

* Press “N” in any view to create a new item.
* Select a reminder by clicking on it or by using the up and down cursor keys to move the cursor to the line displaying the reminder. 
* With a reminder selected:
    * Press “return” to toggle displaying the details. 
    * Pressing “E” to edit.  Then press “Ctrl-S” to save your changes and end  editing or “Ctrl-C” to end editing without saving your changes.
    * Press “C” to open a copy as a new reminder for editing.
    * Press “D” to delete.
    * Press “R” to reschedule the starting datetime.
    * Press “S” to schedule a new datetime instance.
    * For an item with an @g “goto” link, press “Ctrl-G” to open the link.
    * For an item that repeats, press “Ctrl-R” to show repetitions.
    * Timers
        * Press “T” to begin a timer for the reminder.
        * With a timer active, press “T” to toggle paused/running.
        * Press “^T” to end the timer and record an  `@u usedtime` entry in the reminder.
* Movement
    * Press page up or page down to shift the display a page at a time. 
    * Press “l”  (lower case L) and enter a number to move the cursor to a particular line  number. 
    * In the weekly views a),  b) and c), press “g” and enter a date to display the week containing the date.
    * In the dated views a), b), c), u), U) and y), press the right or left cursor keys to go  to the next or previous period, respectively, and the space bar to return to the current period.
* Search.
    * Press “/“ (forward slash) and enter an expression to search the view for an item whose summary contains (case insensitive) the expression. 
    * After entering the search expression, press “n” to search  forward  (cyclically)  for other matches.


## [Installation/Deinstallation](#etm)

### [Installation](#etm)

<!--  [![etm: installing etm in a virtual environment](http://img.youtube.com/vi/fEPPG82AH7M/0.jpg)](http://www.youtube.com/watch?v=fEPPG82AH7M "installing etm in a virtual environment") -->

Setting up a virtual environment for etm is recommended. The steps for OS/X or linux are illustrated below. For details see [python-virtual-environments-a-primer](https://www.google.com/url?q=https%3A%2F%2Frealpython.com%2Fpython-virtual-environments-a-primer%2F&sa=D&sntz=1&usg=AFQjCNFh7QpJQ4rPCDjZ1eLrV1BRCCpSmw).

Open a terminal and begin by creating a new directory/folder, say `etm-pypi` in your home directory, for the virtual environment:

        $ mkdir ~/etm-pypi
        $ cd ~/etm-pypi
Now continue by creating the virtual environment (python >= 3.6 is required):

        $ python3 -m venv env
After a few seconds you will have an `./env` directory. Now activate the virtual environment:

        $ source env/bin/activate
The prompt will now change to something containing `(env)` to indicate that the virtual environment is active. Updating pip is now recommended:

        (env) $ pip install -U pip
Note that this invokes `./env/bin/pip`. Once this is finished, use pip to install etm:

        (env) $ pip install -U etm-dgraham
This will install etm and all its requirements in `./env/lib/python3.x/sitepackages` and will also install an executable called `etm` in `./env/bin`.

By the way, the suggested terminal size for etm is 60 (columns) by 32 or more (rows). The default color scheme is best with a dark terminal background. A scheme better suited to light backgrounds can be set in `cfg.yaml`.

Before you start etm, think about where you would like to keep your personal data and configuration files. The default is to use whatever directory you're in when you start _etm_ as your _etm_ home directory. If you start _etm_ in your virtual environment directory then the default will be to use that as your home directory as well. If this is not what you want, you can just give the path for whatever directory you would like to use when you start _etm_, e.g.,

        (env) $ etm ~/Documents/etm

Considerations:

* If more than one person will be using etm on the same computer, you might want to have different *home* directories for each user.
* If you want to use etm on  more than one computer and use Dropbox, you might want to use `~/Dropbox/etm` to have access on each of your computers.
* If you want to separate personal and professional reminders, you could use separate _home_ directories for each. You can run two instances of _etm_ simultaneously, one for each directory, and view both at the same time. 

Whatever *home* directory you choose, running etm for the first time will add the following to that folder.

        etm home directory/
            backups/
            logs/
            cfg.yaml
            db.json
Here `cfg.yaml` is your user configuration file and `db.json` contains all your etm reminders. The folders `backups/` contains the 5 most recent daily backups of your `db.json` and `cfg.yaml` files. The folder `logs` contains the current `etm.log` file and the 5 most recent daily backups. Note that backup files are only created when the relevant file has been modified since the last backup.

The file `cfg.yaml` can be edited and the options are documented in the file.

### [Deinstallation](#etm)

If you should ever want to deinstall etm, first deactivate the virtual environment, if necessary, by changing to the virtual environment directory and entering

        (env) $ deactivate

You can now simply delete the virtual environment directory and, if you have additional *home* directories, by deleting each of them. One of the many advantages of the virtual environment is that all installations are local to that environment and removing the directory, removes every trace.

# [Details](#etm)

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
- Tasks without an `@s` entry are to be completed when possible and are sometimes called *todos*. They are regarded as *next* items in the *Getting Things Done* terminology and are displayed in *Do Next* view grouped by @l (location/context).
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

### [record](#etm)

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

### [status](#etm)

These type characters are generated automatically by *etm* to display the status of reminders.

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

## [Options](#etm)

Notes:

* The term "list" means a comma and space separated list of elements, e.g., 

    @+ 2p Thu, 9p Mon, 11a Wed

* Options displayed with an asterick can be used more than once, e.g., 

    @a 1h, 30m: t, v   @a 1d: e

    @n joe: jdoaks@whatever.com   @n john: jsmith@wherever.org

	@t red   @t green

### [@ keys](#etm) 

`@` followed by a character from the list below and a value appropriate to the key is used to apply attributes to an item. E.g.,

            @s mon 9a
would specify the the starting datetime for the item is 9am on the Monday following the current date.

*  @+: include. list of datetimes to include
*  @-: exclude. list of datetimes to exclude
*  @a*: alert. list of + (before) or - (after) periods: list of commands
*  @b: beginby. integer (number of days before)
*  @c: calendar. string 
*  @d: description. string
*  @e: extent. timeperiod
*  @f: finished. datetime
*  @g: goto. string (url or filepath)
*  @h: history. (for repeating tasks, a list of the most recent completion datetimes)
*  @i: index. colon delimited string
*  @j*: job summary. string, optionally followed by job &key entries
*  @l: location/context. string
*  @m: mask. string stored in obfuscated form
*  @n*: attendee. string using "[name:] address" format. If "address" begins with exactly 10 digits followed by an "@" it is treated as a mobile phone number. Otherwise it is treated as an email address. The optional "name:" can be used to facilitate autocompletion.
*  @o: overdue. character from (r) restart, (s) skip or (k) keep
*  @p: priority. integer from 0 (none), 1 (low), 2 (normal), 3 (high), 4 (urgent)
*  @r*: repetition frequency, a character from (y)early, (m)onthly, (w)eekly,  
  (d)aily, (h)ourly or mi(n)utely, optionally followed by repetition &key entries
*  @s: start. date or datetime
*  @t*: tag. string
*  @u*: usedtime. string using "timeperiod spent: ending datetime" format
*  @x*: expansion. string
*  @z: timezone. string


### [& keys](#etm)

& followed by a character from one of the lists below. These keys are only used with @j (job) and @r (repetition) entries.

For use with @j:

*  &s: start/due: period relative to @s entry (default 0m)
*  &a: alert: list of + (before) or - (after) periods relative to &s: list of cmd names from the users configuration file
*  &b: beginby. integer number of days before &s
*  &d: description. string
*  &e: extent. period
*  &f: finished. datetime
*  &l: location/context. string
*  &m: masked. string stored in obfuscated form
*  &i: job unique id. string 
*  &p: prerequisites. list of ids of immediate prereqs
*  &u*: usedtime. string using "timeperiod spent: ending datetime" format

For use with @r:

*  &c: count. integer number of repetitions 
*  &E: easter. number of days before (-), on (0) or after (+) Easter
*  &h: hour. list of integers in 0 ... 23
*  &i: interval. positive integer to apply to frequency, e.g., with @r m &i 3, repetition would occur every 3 months
*  &m: monthday. list of integers 1 ... 31
*  &M: month number. list of integers in 1 ... 12
*  &n: minute. list of integers in 0 ... 59
*  &s: set position: integer
*  &u: until. datetime 
*  &w: weekday. list from SU, MO, ..., SA possibly prepended with a positive or negative integer
*  &W: week number. list of integers in 1, ..., 53


## [Notes](#etm)

### @a alerts and @b beginbys:

* With an email/text alert, the item summary is used as the subject and emails/text messages are sent to each attendee listed in an @n entry. The content of the body of the emails/messages are options that can be set in the user's configuration file. 
* Alerts and beginbys are only triggered for unfinished tasks and, when the task is repeating, only for the first unfinished instance. Similarly, pastdue notices for repeating tasks are only triggered for the first unfinished instance.

### repetition notes

* Daylight savings time using @s and @r. The time specified in @s is, by default, respected in the repetitions. E.g., the first five repetitions for 

        * monthly @s jan 1 2020 9a @r m 
  would be 

            ┌─────| First 5 repetitions |──────┐  
            │                                  │
            │ from Wed Jan 1 2020:             │ 
            │   Wed Jan 1 2020 9:00am EST      │
            │   Sat Feb 1 2020 9:00am EST      │
            │   Sun Mar 1 2020 9:00am EST      │
            │   Wed Apr 1 2020 9:00am EDT      │
            │   Fri May 1 2020 9:00am EDT      │
            │                                  │
            │           <    OK    >           │
            │                                  │
            └──────────────────────────────────┘
  Note that all start at 9am even though the first 3 are EST and the last 2 are EDT. 
* Using @s with @r and, optionally, with @+. Datetimes from @+ which fall on or after the @s datetime, if any, are added to the datetimes generated from the @r entry. Note that the datetime from @s will only be included if it matches one generated by the @r entry or by one included in @+. E.g., 

        * my event @s 2018-02-15 3p @r d &h 18 @+ 2018-03-02 4p
    would repeat daily at 6pm starting Feb 15 and at 4pm on Mar 2, *but not* at 3pm on Feb 15 which is specified in `@s`. 
* Using @s without @r and, optionally, @+. Datetimes from @+, if any, are added to @s. E.g., 

        * my event @s 2018-02-15 3p @+ 2018-03-02 4p
    would repeat at 4pm on Mar 2 *and* at 3pm on Feb 15 since `@r` is not specified.
* Using &c and &u in @r. It is an error in *dateutil* to specify both &c (count) and &u (until) since providing both would be at best redundant and at worst conflicting. A distinction between using @c and @u is worth noting and can be illustrated with an example. Suppose an item starts at 10am on a Monday and repeats daily using either count, &c 5, or until, &u fri 10a.  Both will create repetitions for 10am on each of the weekdays from Monday through Friday. The distinction arises if you later decide to delete one of the instances, say the one falling on Wednesday, using @-. With *count*, you would then have instances falling on Monday, Tuesday, Thursday, Friday *and Saturday* to satisfy the requirement for a count of five instances. With *until*, you would have only the four instances on Monday, Tuesday, Thursday and Friday to satisfy the requirement that the last instance falls on or before 10am Friday.


### repetition examples

* Christmas (an all day event) [r]epating (y)early on Dec 25.

        * Christmas @s 2015/12/25 @r y
* Get a haircut (a task) on the 24th of the current month and then [r]epeatedly at (d)aily [i]ntervals of (14) days and, [o]n completion, (r)estart from the last completion date:

        - haircut @s 24 @r d &i 14 @o r
* Take out trash (at task) on Mondays but if the task becomes [o]verdue, (s)kip the pastdue reminders.

        - Take out trash @s mon @r w @o s
* A sales meeting (an event) [r]epeating m)onthly on [w]eekdays that are either the first or third Tuesdays in the month.

        * sales meeting @s tue 9a @e 45m @r m &w 1tu, 3tu

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

### @m masked/obfuscated entry

These entries are encoded in the database in an obfuscated or masked format but decoded when displayed in etm itself. A key, *secret*, specified in the user configuration file is used for the encoding/decoding. E.g., a reminder that appears as

        % masked entry @s 2019-11-30 4pm @m obfuscated entry

could appear in the database as

        "1685": {
        "itemtype": "%",
        "summary": "masked entry",
        "s": "{T}:20191130T2100A",
        "m": "{M}:w5TDlsOTwpXDnMOWwoHDm8OXw4nCgcOZwo_DmcOmw6Y=",
        "created": "{T}:20191130T1642A",
        "modified": "{T}:20191130T1643A"
        }

### @x expansions

The `@x`, *expansion key*, entry is used to specify a key for options to be extracted from the etm configuration settings. E.g., suppose your configuration setting has the following entry for *expansions*:

            expansions:
                tennis: '@e 1h30m @a 30m, 15m: v @i personal:tennis'
                ...
Then when entering the following reminder

        * Conflict and Cooperation @s 1/25/2018 9:35am @x tennis 
tab completion would offer `'@e 1h30m @a 30m, 15m: v @i personal:tennis'` as a replacement for `'@x tennis'`.


