<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etmlogo.png" alt="etm" title="event and task manager" width="200px" />

This is the etm user manual. It is best viewed at [GitHub.io](https://dagraham.github.io/etm-dgraham/) where all the internal, contents links work correctly. etm itself is available from [PyPi](https://pypi.org/project/etm-dgraham/) and [GitHub](https://github.com/dagraham/etm-dgraham) and further information from the etm discussion group at [groups.io](https://groups.io/g/etm-dgraham). Brief how-to videos are available at [youtube](https://www.youtube.com/@etm-dgraham).


# Contents {#contents}
-   [Overview](#overview)
    -   [Reminders](#reminders)
        -   [examples](#examples)
        -   [text entry versus forms](#text-entry-versus-forms)
        -   [unobtrusive and timely entry assistance](#unobtrusive-and-timely-entry-assistance)
            -   [just in time entry prompts and feedback](#just-in-time-entry-prompts-and-feedback)
            -   [fuzzy parsing of datetimes](#fuzzy-parsing-of-datetimes)
            -   [relative datetimes](#relative-datetimes)
            -   [tab completion](#tab-completion)
    -   [Views](#views)
        -   [Weekly Views](#weekly-views)
        -   [Do Next View](#do-next-view)
        -   [Timer View](#timer-view)
        -   [Review View](#review-view)
        -   [Pinned View](#pinned-view)
        -   [Konnected View](#konnected-view)
        -   [Used Time Views](#used-time-views)
        -   [Query View](#query-view)
            -   [Simple queries](#simple-queries)
            -   [Simple query examples](#simple-query-examples)
            -   [Archive queries](#archive-queries)
            -   [Update queries](#update-queries)
            -   [Complex queries](#complex-queries)
            -   [Command History](#command-history)
            -   [Saved Queries](#saved-queries)
        -   [Common Features](#common-features)
    -   [Mobile Access to your reminders](#mobile)
    -   [Menus](#menus)
        -   [etm menu notes](#etm-menu-notes)
        -   [view menu notes](#view-menu-notes)
        -   [editor menu notes](#editor-menu-notes)
        -   [selected menu notes](#selected-menu-notes)
    -   [Installation](#installation)
        -   [For personal use](#for-personal-use)
        -   [For use in an isolated environment](#for-use-in-an-isolated-environment)
        -   [For use system wide](#for-use-system-wide)
    -   [Usage](#usage)
        -   [Terminal size and color](#terminal-size-and-color)
        -   [Home directory](#home-directory)
        -   [Timers](#timers)
        -   [lorem examples](#loremexamples)
        -   [Using etm+](#etmplus)
    -   [Deinstallation](#deinstallation)
        -   [From a virtual environment](#from-a-virtual-environment)
        -   [From a system wide installation](#from-a-system-wide-installation)
-   [Details](#details)
    -   [Item Types](#item-types)
        -   [event](#event)
        -   [task](#task)
        -   [journal](#journal)
        -   [inbox](#inbox)
        -   [status](#status)
            -   [beginning soon](#beginning-soon)
            -   [past due](#past-due)
            -   [waiting](#waiting)
            -   [finished](#finished)
    -   [Options](#options)
        -   [@ keys](#atkeys)
        -   [& keys](#ampkeys)
    -   [Notes](#notes)
        -   [notices](#notices)
        -   [repetition](#repetition)
            - [repetition examples](#repetition-examples)
            - [anniversary substitutions](#anniversary-substitutions)
        -   [archived reminders](#archived-reminders)
        -   [configuration](#configuration)
        -   [data storage](#data-storage)

# Overview {#overview}

*etm* began life in 2013 as *etm-qt* sporting a gui based on *Qt*. The intent was to provide an app supporting GTD (David Allen's Getting Things Done) and exploiting the power of python-dateutil. The name changed to *etmtk* in 2014 when *Tk* replaced *Qt*. Development of *etmtk* continued until 2019 when name changed to *etm-dgraham*, to honor the PyPi naming convention, and the interface changed to a terminal based one based on *prompt_toolkit*. Features have changed over the years but the text based interface and basic format of the reminders has changed very little. The goal has always been to be the Swiss Army Knife of tools for managing reminders.

## Reminders {#reminders}

*etm* offers a simple way to manage your events, tasks and other reminders.

Rather than filling out fields in a form to create or edit reminders, a simple text-based format is used. Each reminder in *etm* begins with a *type character* followed by a brief *summary* of the item and then, perhaps, by one or more *@key value* pairs to specify other attributes of the reminder. Mnemonics are used to make the keys easy to remember, e.g, @s for scheduled datetime, @l for location, @d for description and so forth.

The 4 types of reminders in etm with their associated type characters:

|  type   | char  |
| ------- | ----- |
| task    |    -  |
| event   |    *  |
| journal |    %  |
| inbox   |    !  |


See [Item Types](#item-types) for details about these item types and [Options](#options) for details about possible attributes.

[↺ contents](#contents)

### examples {#examples}

* A task (**-**): pick up milk.

        - pick up milk

* An event (**\***): have lunch with Ed [s]tarting next Tuesday at 12pm and [e]xtending for 90 minutes, i.e., lasting from 12pm until 1:30pm.

        * Lunch with Ed @s tue 12p @e 90m

* A journal entry (**%**): a favorite Churchill quotation that you heard at 2pm today with the quote itself as the [d]escription.

        % Give me a pig - Churchill @s 2p @d Dogs look up at
          you. Cats look down at you. Give me a pig - they
          look you in the eye and treat you as an equal.

    The *summary*, "Give me a pig - Churchill" in this example, follows the type character and is meant to be brief - analagous to the subject of an email. The optional *description* follows the "@d" and is meant to be more expansive - analagous to the body of an email.

* A task (**-**): build a dog house, with component [j]obs.

        - Build dog house @j pick up materials @j cut pieces
          @j assemble @j sand @j paint

* Inbox (**!**): meet Alex for coffee Friday.

        ! Coffee with Alex @s fri @e 1h

    This can be changed to an event when the details are confirmed by replacing the **!** with an **\*** and adding the time to `@s`.  This inbox entry will appear highlighed on the current day in *agenda view* until you make the changes.

* An appointment (event) for a dental exam and cleaning at 2pm on Feb 5 and then again [@+] at 9am on Sep 3.

        * dental exam and cleaning @s 2p feb 5 2019 @e 45m
          @+ 9am Sep 3 2019

[↺ contents](#contents)

### text entry versus forms {#text-entry-versus-forms}

* Text entry removes the need to hunt for and click in the relevant entry box and allows you to keep your fingers on the keyboard.
* Text entry supports the full flexibility of the superb Python *dateutil* package. Consider, for example, creating a reminder to vote for President election day which repeats every 4 years on the first Tuesday after a Monday in November (a Tuesday whose monthday falls between 2 and 8). In *etm*, this event would be

        * Presidential election day @s nov 1 2020 @r y &i 4 &M 11
          &m 2, 3, 4, 5, 6, 7, 8 &w tu

    Try this with a form based calendar application.

[↺ contents](#contents)

### unobtrusive and timely entry assistance {#unobtrusive-and-timely-entry-assistance}

When you want to create a new reminder or edit an exiting one, *etm* opens an area at the bottom of the screen that is divided into two parts by a horizontal line. The lower part is the entry area where what you type appears. The upper part is the prompt/feedback area where *etm* responds to your typing. This response might take the form of providing a suggestion about alternatives, information about the type of input required or feedback about how your current entry is being interpreted. It is important to realize that none of this interferes with your typing - you can blaze away as quickly as you like or even paste complete entries and never glance at the prompt if you like. This is the **unobtrusive** part of the prompt/feedback process.

<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/new.png" alt="new" title="new entry" width="600px" hspace="20px"/>



[↺ contents](#contents)

#### just in time entry prompts and feedback {#just-in-time-entry-prompts-and-feedback}

**FIXME** replace this section with a link to a new video

<!--
Let's create the election day reminder to illustrate the **timely** part of the process. Begin by pressing `N` to create a new reminder and notice that *etm* automatically prompts you for the item type character and suggests the alternatives.

        item type
        Choose a character from * (event), - (task), % (journal)
        or ! (inbox)

        ────────────────────────────────────────────────────────────
        _

Notice that you don't have to search for the part of the form in which you specify the type of reminder - *etm* effectively makes the one entry area the appropriate spot for this and all other input. Now enter an `*` to create an event and *etm* will prompt you for the event summary.

        summary
        brief item description. Append an '@' to add an option.

        ────────────────────────────────────────────────────────────
        *_

Enter the summary followed by an `@` and *etm* will automatically display the required and available `@-keys`.

        @-key
        required: @s (scheduled)
        available: @+ (include), @- (exclude), @a (alerts),
        @b (beginby), @c (calendar), @d (description),
        @e (extent), @g (goto), @i (index), @l (location),
        @m (mask), @n (attendee), @o (overdue),
        @r (repetition frequency), @s (scheduled), @t (tag),
        @u (used time), @x (expansion), @z (timezone)
        ────────────────────────────────────────────────────────────
        * Presidential election day @_

You see that `@s` is required, so add the `s` and *etm* will prompt you for the value for the scheduled option and describe the type of input required.

        scheduled
        scheduled date or datetime

        ────────────────────────────────────────────────────────────
        * Presidential election day @s_

As you enter the datetime, *etm* will display its interpretation of your entry.

        scheduled
        Sun Nov 1 2020

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20_

Now append an `@` to see the prompt for options and notice that `@s`, having been provided, is no longer listed.

        @-key
        available: @+ (include), @- (exclude), @a (alerts),
        @b (beginby), @c (calendar), @d (description),
        @e (extent), @g (goto), @i (index), @l (location),
        @m (mask), @n (attendee), @o (overdue),
        @r (repetition frequency), @t (tag), @u (used time),
        @x (expansion), @z (timezone)
        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @_

We want to repeat so enter an `r` and *etm* will describe the required input.

        repetition frequency
        repetition frequency: character from (y)early,
        (m)onthly, (w)eekly, (d)aily, (h)ourly or
        mi(n)utely.

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r_

Add a `y` for yearly. The repetition attribute, `@r`, has several possible attributes which apply specifically to it. Such attributes use `&` rather than `@` as a tag. Enter an `&` to see the prompts for repetition options.

        repetition &-key
        repetition &-keys: &i (interval), &m (monthdays),
        &E (easterdays), &h (hours), &M (months),
        &n (minutes), &w (weekdays), &W (week numbers),
        &c (count), &u (until), &s (set positions)

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &_

Enter an "i" to see what "interval" means.

        interval
        Interval requires a positive integer (default 1) that
        sets the frequency interval. E.g., with frequency w
        (weekly), interval 3 would repeat every three weeks.

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &i_

We want to repeat every 4 years so enter `4` followed by another `&` to see other options. [The display for *repetition &-keys* is unchanged from above and will be omitted hereafter.] Now enter an `M` to see what "months" means.

        months
        months: a comma separated list of integer month numbers
        from 1, 2, ..., 12

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &i 4 &M_

We want November, so enter 11 followed by an `&` for other options. Then enter an `m` to see what "monthdays" means

        monthdays
        monthdays: a comma separated list of integer month days
        from  (1, 2, ..., 31. Prepend a minus sign to count
        backwards from the end of the month. E.g., use  -1 for
        the last day of the month.

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &i 4 &M 11 &m_

We want a monthday between 2 and 8 so enter these monthdays followed by "&" for options. Then enter `w` to see what "weekdays" means

        weekdays
        weekdays: a comma separated list of English weekday
        abbreviations from SU, MO, TU, WE, TH, FR, SA. Prepend
        an integer to specify a particular weekday in the month.
        E.g., 3WE for the 3rd Wednesday or -1FR, for the last
        Friday in the month.

        ────────────────────────────────────────────────────────────
        * Presidential election day @s nov 1 20 @r y &i 4 &M 11
        &m 2, 3, 4, 5, 6, 7, 8 &w_

We want a Tuesday, so add `tu` to complete the entry. To check the entry, press ^R to show repetitions

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

These are the first 5 repetitions on or after Nov 1 2020. Notice that the scheduled value of Nov 1 2020 is not one of the repetitions since it doesn't satisfy the requirements. These appear correct, so press ^S to save the reminder.


General observations:

* The general structure of this reminder is

            * Presidential election day
                @s nov 1 20
                @r y
                    &i 4
                    &M 11
                    &m 2, 3, 4, 5, 6, 7, 8
                    &w tu

   The `@s` and `@r` entries provide attributes of the event itself and the `&i`, `&M`, `&m` and `&w` entries provide attributes of the `@r` entry. More than one `@r` entry can be provided and each can have its own set of `&-key` entries.
* *@-keys* can generally be entered in any order provided that `@s` is entered before any options that require it. *&-keys* can also be entered in any order.

* The prompts provide "just in time" information relevant to the entry you are typing and need only be consulted if you are uncertain about your entry. With a little
    experience, most reminders can be completed without a glance at the prompt.
-->
[↺ contents](#contents)

#### fuzzy parsing of datetimes {#fuzzy-parsing-of-datetimes}

Whenever *etm* expects a datetime entry as, for example, when you are entering an `@s` scheduled datetime, it applies fuzzy parsing to your entry.  Suppose it is Dec 17 2019, your computer is in the Eastern timezone and you have just entered `@s` for your lunch event

        scheduled
        scheduled date or datetime

        ────────────────────────────────────────────────────────────
        * lunch @s_

If you enter `1`, *etm* will interpret it as 1am on the current date in the local timezone.

        scheduled
        Tue Dec 17 2019 1:00am EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1_

Adding `p` changes the interpretation to 1pm.

        scheduled
        Tue Dec 17 2019 1:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p_

Now start adding 'fri' by appending an 'f'.

        scheduled
        '1p f' is incomplete or invalid

        ────────────────────────────────────────────────────────────
        * lunch @s 1p f_

and *etm* will complain that the entry is now either incomplete or invalid. Add the remaining 'ri'.

        scheduled
        Fri Dec 20 2019 1:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p fri_

and *etm* understands that you want the coming Friday, Dec 20. Now suppose that you will be in California on Friday and you want Pacific, not Eastern time. Then add an entry for `@z`.

        scheduled
        local datetime: Fri Dec 20 2019 4:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p fri_ @z US/Pacific

Note that `local datetime` is now prepended to the result which is still displayed in the local timezone, since that is the location of your computer, but the time has changed to `4:00pm EST` which, of course, is the same time as `1:00pm PST`. *etm* **always** displays times in the current local time zone. When you save this item, the time will be converted to universal time and the `@z US/Pacific` will be deleted - once the time has been converted, the original timezone is no longer relevant.

What if you had entered the 'fri' first?

        scheduled
        Fri Dec 20 2019

        ────────────────────────────────────────────────────────────
        * lunch @s fri

Here *etm* supposes again that you want the coming Friday, Dec 20 but without a time being specified, it is interpreted as a date rather than a datetime and thus without a timezone. Add the `1p` and timezone the result will be the same as before.

As a final illustration, suppose you want to be reminded of lunch at 1pm in whatever timezone you happen to be, i.e., you want the datetime to float to the local timezone. Add the `@z`.

        timezone
        a timezone entry such as 'US/Eastern' or 'Europe/Paris'
        or 'float' to specify a naive/floating datetime

        ────────────────────────────────────────────────────────────
        * lunch @s fri 1p @z

and note that supplying 'float' as the timezone does the trick.

        scheduled
        Fri Dec 20 2019 1:00pm

        ────────────────────────────────────────────────────────────
        * lunch @s fri 1p_ @z float

The datetime now appears without either the 'local datetime' prefix or the 'EST' suffix which reveals that it is a naive/floating datetime.


The assumption here is that when a user enters a date, a date is what the
user wants. When both a date and time are given, what the user wants
is a datetime and, most probably, one based on the local timezone. Less
probably, one based on a different timezone and that requires the addition
of the `@z` and timezone. Still less probably, one that floats and this
requires the addition of the `@z` and 'float'.

Note: When entering dates, `.`, `-` or `/` can be used to separate the components.
The interpretation of the date depends upon the 'dayfirst' and 'yearfirst' settings
in the etm configuration file - see [configuration](#configuration) for details
about these settings. For example, with both dayfirst and yearfirst false,

    6/1 => June 1 in the current year

but after changing dayfirst to true

    6/1 => January 6 in the current year

[↺ contents](#contents)

#### relative datetimes {#relative-datetimes}

Relative datetimes can be entered using period strings either instead of or in addition to datetimes using the format:

    [datetime] [period string]

Either the datetime or the period string is required but both are
allowed. The period string must begin with either a plus or a minus
sign.

If the datetime is omitted and
* the period string involves d (days), w (weeks) or M (months),
       then the assumed datetime is the current date,
* the period string involves only h (hours) or m (minutes),
       then the assumed datetime is the current time

Examples supposing it is currently 1:20pm on July 15:

    +1h30m     => 2:50pm on July 15
    +3d        => July 18
    -3d        => July 12
    8a         => 8am on July 15
    8a +1h30m  => 9:30am on July 15
    8a +3d     => 8am on July 18

[↺ contents](#contents)

#### tab completion {#tab-completion}

Some optional attributes that can be used in reminders can be tedious to enter either because they are lengthy or because they are used often and typographical errors would introduce inconsistencies. These attributes include the following:

* *@g*: goto url or filepath. In the latter case, the system default application is used to open the filepath, e.g., on my macbook the system default for files ending in `.py` is to open them in MacVim. In the former case, the url will be opened in the default browser. In either case, a typo would likely render the link useless.
* *@l*: location/context. In the *do next* view, `location` is used to organize undated tasks. Using `@l errands` in one task and `@l erands` in another would cause these tasks to be grouped separately.
* *@i*: index - forward slash delimited string. In both the *index* and the *used time* views, the index entry is used to group and aggregate entries. Using `@i jsmith/project a` in one entry and `@i jsmth/project a` in another would cause these these entries to be grouped and aggregated separately.
* *@n*: attendee. string using "[name:] address" format. If "address" begins with exactly 10 digits followed by an "@" it is treated as a mobile phone number. Otherwise it is treated as an email address. The optional "name:" can be used to facilitate autocompletion. Attendee entries are used in both email and text alerts.

Other tracked attributes include *@c* (calendar) and *@t* (tag).

For these attributes, etm keeps a record of each usage. I.e., for each reminder in your *etm* database, if the reminder includes a tracked attribute that has not already been included in the list of completions, then that attribute will be added. E.g., if you create an reminder containing

        @n joe: jsmith457@gmail.com

  and '@n joe: jsmith457@gmail.com' is not already in the list of completions, then it would be added.

When you next create a reminder and enter @n, *etm* will pop up a sorted list of every item in the completion list that begins with @n. You can use the up and down cursor keys to move through this list or you can continue typing to limit the possible completions, e.g., after entering '@n joe' only those completions that start with '@n joe' would still be displayed. When you have selected the completion you want, press the space bar to insert the completion in your entry.


[↺ contents](#contents)

## Views {#views}

_etm_ has several ways of viewing entries. These are listed below by the shortcut key used to activate the view. E.g., pressing `a` activates _Agenda_ view shown below. In each of the views, the etm menus appear at the top and the status bar at the bottom. The latter displays the current datetime and the name of the view.

<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etmview_agenda.png" alt="new" title="new entry" width="450px" hspace="20px"/>


The display for each reminder shows the itemtype and summary column on the left followed by a *flags* column which displays a combination of letters from 'g' (goto), 'k' (connection), 'p' (pinned) and 't' (timer) reflecting the presence of these attributes in the reminder. This column is sometimes followed on the extreme right by another column whose contents depends on the view. E.g. in index and journal views the 'id' of the reminder is displayed while in history view, the last modification timestamp of the reminder is displayed.

  * a: Agenda: dated unfinished tasks and other reminders by year-week and week day
  * b: Busy: a graphical illustration of busy and conflicted times by year-week
  * c: Completed: finished tasks and jobs and used time entries by year-week and week day
  * d: Do Next: undated tasks grouped by location/context and ordered by priority (highest first) and extent (least first)
  * e: Effort: instances of reminders with used time entries with daily totals displayed graphically
  * f: Forthcoming: unfinished dated tasks and other dated reminders by next occurrence
  * h: History: all items by the latter of the modified or created datetimes in descending order, i.e., most recent first. Datetimes are displayed using a 5 character format where, e.g., 1:15pm today would be displayed as 13:15, November 7 of the current year as 11/17 and January 15 of 2012 as 12.01.
  * i: Index: all items grouped hierarchically by index entry
  * j: Journal: journal entries grouped hierarchically by index entry
  * k: Konnection: items with @k konnection links either to or from the selected item.
  * l: Location: items grouped hierarchically by location entry
  * m: Timers: items with timers.
  * p: Pinned: items whose pin status is on.
  * q: Query: items matching a user specified query. Enter ? for query usage.
  * r: Review: undated tasks sorted by the time since the task was last modified with the most recently modified last.
  * t: Tags: all items with @t tag entries grouped by tag
  * u: Used Time: all items with @u used time entries grouped by month and hierarchically by index
  * U: Used Summary: used time aggregates grouped by month and hierarchically by index
  * y: Yearly Planning Calendar: compact monthly calendar.


[↺ contents](#contents)

### Weekly Views {#weekly-views}

The _agenda_, _busy_, _completed_ and _effort_ views display one week at a time and are *synchronized* so that all four views always display the same week. Press the ▶ (right) or ◀ (left) cursor keys go forward or backward a week at a time or press the space bar to jump to the week containing the current day. You can also press "end" and enter a date to jump to the week containing the date.

In _agenda_ view, only days with scheduled reminders are listed. If nothing is scheduled for the entire week, then "Nothing scheduled" is displayed.


In _busy_ view, only days that have events with busy times (@e and/or @w entries) are displayed. Press the number of the weekday, [1→Mon, ..., 7→Sun], to show the details of the busy periods from that day or press the ▼ (down) or ▲ (up) cursor keys to show the details of the next or previous day with busy periods.

_Completed_ view shows instances of completed tasks.

_effort_ view shows instances of reminders with used time entries with daily totals displayed graphically.

The normal agenda listing for a week day:

* all day events (events with dates as `@s` entries)
* datetime items (reminders with datetimes as `@s` entries) by time
* all day tasks (tasks with dates as `@s` entries)
* all day journal enties (journal entries with dates as `@s` entries)

And, on the current day only:

* inbox items
* *<* past due warnings in descending order of the number of days past due
* *>* beginby warnings in ascending order of the number of days remaining

Busy view requires a little explanation. Here is screen shot of agenda view for an illustrative week
<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/agenda.png" alt="new" title="agenda view" width="600px" hspace="20px"/>

along with one of busy view for the same week
<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/busy.png" alt="new" title="busy view" width="600px" hspace="20px"/>

The first thing to notice in busy view is that busy times are displayed each week day for the period between 7am and 9pm. This period is determined by the *beginbusy* setting in `cfg.yaml` which sets the number of hours after midnight that the display is to begin each day. The period ends 14 hours after *beginbusy*. In this case, it runs from 7 hours after midnight (*beginbusy*) to 7+14=21 hours after midnight or from 7am until 9pm. The resolution is 15 minute periods for each character *slot* so that, for example, the row for *Fr 2* shows a busy period with using 4 green (busy) characters for 10-10:15am, 10:15-10:30am, 10:30-10:45am and 10:45-11am. Now you might notice that this implies that the 4 character slots that begin at 8pm end just before the 9pm slot and that the 9pm slot actually corresponds to the interval 9-9:15pm. Since the actual display includes this last slot, it actually extends for 14 hours plus 15 minutes and thus actually ends at 9:15pm.

The second thing to notice is the red, conflict bar in the display for *Mo 28*. Since the details for this day are displayed in the "busy times" panel at the bottom as well as in the agenda view, you will notice that the conflict corresponds to the overlap between the 6-8am event and the 7-9:30am event. This conflict from 7-8am is illustrated by the 4 red (conflict) characters. Notice also that the period for the first event extends from 6-7am before the period displayed begins at 7am. The single green character to the left of 7am indicates that there were busy times before the displayed period begins. Similarly, the green character to the right of 9-9:15pm on *We 30* indicates that there were busy times after 9:15pm on that day. This corresponds to the 8-10:30pm event shown in agenda view for Wednesday that extends from 9:15-10:30pm after the displayed period.

As you might expect, if a conflict occurred either before or after the displayed period then the corresponding *before* or *after* character would be red instead of green.

[↺ contents](#contents)

### Do Next View {#do-next-view}

This view is a todo list on steroids. It displays undated and unfinished tasks grouped and sorted by their `@l` (location/context) entries and then, within each group by their priorities.  E.g., the entry `@l #next` would put a task in a group at the top of the list because of the `#`. As another example,`‘@l |someday`, would put the task in a group near the end of the list because of the `|`.

If you're curious, here is the list of visible ASCII characters in their sorted order:

        '!', '"', '#', '$', '%', '&', "'", '(', ')',
        '*', '+', ',', '-', '.', '/', '0', '1', '2',
        '3', '4', '5', '6', '7', '8', '9', ':', ';',
        '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D',
        'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
        'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_',
        '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
        'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
        'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '{', '|', '}', '~'

Context is useful for more than just the sorting order. Suppose you have a task that you want to deal with the next time you’re at the lake house. Just add `@l at/lake house` and all you have to remember is to check the subgroup 'lake house ' under the 'at' group in *do next view* when you’re next there. Many such contexts come to mind - `at/grocery store`, `at/office`, ...

One final useful context is 'waiting for'. E.g., completing a task might depend upon getting something from Joe. Add `@l waiting for/Joe` to the task and it will be listed in the subgroup 'Joe' under 'waiting for'.

### Timer View {#timer-view}

This view lists all reminders with associated timers sorted by the elapsed time since the timer's *state* was last changed. The display for each reminder shows the itemtype and summary, any applicable *flags* and the elapsed time and *state* of the associated timer.

The sort order assures that the reminder with the active timer will always be at the top of the list and followed by the reminders with the most recently modified timers. This makes it easy to switch back and forth between recent timers.

[↺ contents](#contents)

### Review View {#review-view}

Displays a list of the summaries and location/contexts (@l entries) of undated and unfinished tasks sorted by their (last) modified timestamp and grouped by the number of weeks since last modified.

This view is used for a periodic review of such "todos" with the goal of not letting them 'slip through the cracks'. Either editing a task or pressing "^U" with the task selected resets the modified timestamp to the current time and thus moves the task to the "this week" group at the bottom of the list.

A reasonable work flow would be to open this view once every week or so and examine tasks more than a week "old", editing them when necessary and otherwise updating the modified timestamp using "V" so that all tasks are kept within the 'last week' or 'this week' groups.

[↺ contents](#contents)

### Pinned View {#pinned-view}

Items that have been "pinned" (have their pin status toggled on) are displayed in *pinned view* grouped by itemtype and sorted by the created/modified datetime.

This view can be used to flag items that need attention in your daily workflow in the same way that you might flag email in your inbox that you want to handle first. Just as you might sort your inbox to move the flagged items to the top, you can switch to pinned view to see just the reminders that need attention. And just as you would remove the flag when you finish with an email, you can unpin the reminder that no longer needs attention and thus remove it from the pinned view.

The pinned status of items is retained so long as *etm* is active but cleared when *etm* is restarted.

[↺ contents](#contents)

### Konnected View {#konnected-view}

Items with @k konnection links either to or from other items are displayed with a 'k' in the *flags* column of normal views. Konnected view **only** displays items with such konnections. They are listed in order of their doc_ids and the view is similar to other item views, e.g., press 'space' to see the details of the selected item, 'E' to edit the selection and so forth. Unlike other item views, pressing 'k' toggles the display of the 'konnections' of the selected item. This opens a pane at the bottom of the display that shows the list of items with @k links to the selected item, then the selected item itself and finally the list of items with @k links from the selected item. This konnections display is also a normal view, e.g., selecting an item and pressing 'space' will display its details.

This view and the ability to add links between items in *etm* is meant to support the *Zettelkasten* system of note taking. The term is German for "slip box" where "slip" is a slip of paper containing a single note. These are the essential ideas:

* Each note represents a single, self-contained idea.
* Notes are linked to other, related notes.

This network of ideas and links has been compared to the brain with its network of neurons and connecting synapses. The links are the keys to both. With notes on paper slips, links required a unique label for each slip and a variety of labeling techniques have been used historically from suggestive keywords to the date and time the note was created.

Labels are built into *etm* since every note (journal entry), event, task or inbox entry gets a unique, integer *doc_id* when it is created. Links are provided by the `@k` konnections - e.g., adding `@k 238` to an item, konnects/links that item to the item with doc_id 238.

As discussed above, *konnected view* provides the means for examining the network of konnections. But how are these konnections created in the first place? When you type `@k` into the entry area, a list of possible completions will pop up. The lines in this list contain the following item values separated by spaces:

* the item index entry
* the item type character
* the item summary
* the item doc_id

Initially the list of possible completions includes **every** item in the *etm* active database, but as you begin typing an index entry, the list collapses to show only those items which contain what you have typed thus far. At any point you can stop typing and scroll up and down the list and, finding the item you want to use for the link, press **SPACE** to select it and then  **TAB** to replace the selected entry with just the doc_id from the selected entry.

What if you have an related idea while editing an item and the idea does not yet correspond to another item? Add `@K comment regarding idea` (note the capital K) and, when you save the item, etm will create an inbox item with your comment as its summary and then replace the `@K comment regarding idea` with `@k doc_id` using the doc_id of the new inbox item. When you have time, edit the inbox entry to better represent your idea and change the item type accordingly. You can add as many `@K` entries as you like - each will give rise to a new inbox item.

Other relationships are possible in *etm* - shared tags, common index entries, common item type, and so forth - and there are views to support examining these relationships - tags view, index view, journal view and so forth. *Konnected View* is uniquely intended to support examining the konnections among items.

*Konnected View* is specially designed to help you follow a thread of konnections. When you select an item and press 'k',
a konnection view opens that shows just the items with konnections to the selected item and the items with konnections from the selected item. Selecting an item from this view and pressing 'k' closes the konnections view but moves the selection in the konnected view to the item just selected so that pressing 'k' again will show the konnections for the item just selected.


[↺ contents](#contents)

### Used Time Views {#used-time-views}

The *used time* and *used time summary* views are bound to `u` and `U` respectively. They report `@u` (used time) entries in your reminders, rounded up according to the `usedtime_minutes` setting in your `cfg.yaml` file and grouped by year-month and then heirarchially by `@i` entries.

I have a file of reminders with `@i` and `@u` entries such as

        * Modi ut sit sed amet sit @s 2019-11-11 10:00am @e
           1h30m
        @u 58m: 2019-11-11 10:58am @u 34m: 2019-11-11 10:34am
        @i client A/project a1/correspondence
        @d Aliquam non sed aliquam eius tempora quisquam dolorem.
        Neque quiquia labore tempora magnam. Quiquia tempora
        porro est ut. Ut tempora sed non ut eius neque porro.
        Sed quaerat consectetur dolor sit.

With `usedtime_minutes: 6`, the *used time view* for November begins with

        November 2019
          client A
            project a1
              correspondence
                * Modi ut sit sed amet sit: 1.6h Nov 11
                % Amet modi neque eius adipisci: 2.7h Nov 27
              research
                * Quisquam quiquia velit non: 2.0h Nov 19
            project a2
              correspondence
                * Consectetur voluptatem dolorem: 1.0h Nov 6
                * Quaerat etincidunt sed non: 0.9h Nov 13
                * Consectetur eius est adipisci: 0.5h Nov 25
                % Magnam labore etincidunt: 1.8h Nov 28
              meeting
                % Adipisci dolor labore quiquia: 0.9h Nov 7
                % Adipisci eius velit porro: 1.4h Nov 14
              research
                * Non modi non velit eius: 1.0h Nov 20
          client B
            project b1
              correspondence
                * Dolor neque velit dolorem: 0.4h Nov 22
              meeting
                * Ipsum numquam porro consectetur: 0.8h Nov 15
              phone
                - Porro voluptatem aliquam: 1.0h Nov 12
                % Amet ut dolor velit aliquam: 1.9h Nov 13
              research
                * Quisquam labore ut sit aliquam: 0.7h Nov 5
                * Quiquia ut quisquam sit: 1.5h Nov 12
                % Adipisci amet modi sed eius: 2.6h Nov 15
                - Velit dolor quiquia etincidunt: 1.9h Nov 15

Note that the display is by month and, within the month, heirarchially by index entry and reminder. Note also, that the reported times are aggregates of all `@u` entries in the reminder. The first reminder, for example, has 2 such entries:

        @u 58m: 2019-11-11 10:58am @u 34m: 2019-11-11 10:34am

Because of

        usedtime_minutes: 6

in `cfg.yaml`, each `@u` timeperiod is first rounded up to the next 6 minutes and then added. Thus 58m becomes 1h, 34m becomes 36m and the sum, 1h36m, is reported in hours and tenths as 1.6h.

The reminder lines are similar to those in other views. With, e.g.,

            * Modi ut sit sed amet sit: 1.6h Nov 11

selected, pressing return would display the item's details, pressing `E` would open it for editing and so forth.


The *used time **summary** view* for the same month begins with:

        November 2019: 44.4h
           client A: 13.8h
              project a1: 6.3h
                 correspondence: 4.3h
                 research: 2.0h
              project a2: 7.5h
                 correspondence: 4.2h
                 meeting: 2.3h
                 research: 1.0h
           client B: 16.6h
              project b1: 10.8h
                 correspondence: 0.4h
                 meeting: 0.8h
                 phone: 2.9h
                 research: 6.7h
              project b2: 3.9h
                 meeting: 1.8h
                 research: 2.1h
              project b3: 1.9h
                 correspondence: 1.9h


This view omits the reminder lines and aggregates the used times hierarchically by index entry.

As with other dated views, the left and right cursor keys go backwards and forwards a month at a time and the space bar returns to the current month. Also, pressing `^C` copies the contents of the view to the system clipboard.

[↺ contents](#contents)

### Query View {#query-view}

In *query view* an entry line at the bottom of the screen is used to submit queries to your data store of reminders. For example, press `q` to open query view, enter

        includes summary waldo

and press return to see a list of reminders in which either the summary or the `@d` element includes a match for the case-insensitive regular expression "waldo". Each line of the display contains the item type, the summary and the document id of the matching reminder. You can use `in` as an abbreviation for `includes`. As another example

        exists u and ~exists i

would display reminders with an @u element but not an @i element.

Simple queries of this type produce a list of matching items with the itemtype, summary and id displayed and sorted by id, i.e., by the order created. It is also possible to create more complex queries in which the output is displayed heirarchially using a format determined by the query parameters. Enter `?` or `help` at the prompt to get this detailed usage information:

[↺ contents](#contents)

#### Simple queries {#simple-queries}

Return a list of items displaying the itemtype, summary
and id, and sorted by id, (order created) using commands
with the format:

    command field [args]

where "field" is either 'itemtype', 'summary' or one of
the '@-keys' such as 'l' or 's', and "command" is one of
those listed below (see Simple Query Examples below for
examples):

* begins field RGX: return items in which the value of
  field begins with a match for the case insensitve
  regular expression RGX.

* includes (or in) LST RGX: return items in which the value
  of one of the fields in LST includes a match for the case
  insensitive regular expression RGX. (LST contains all
  but the last, RGX, argument.)

* equals field VAL: return items in which the value of
  field == VAL

* more field VAL: return items in which the value of
  field >= VAL. The value of field and VAL must be
  comparable, i.e., both strings or both numbers

* less field VAL: return items in which the value of
  field <= VAL. The value of field and VAL must be
  comparable, i.e., both strings or both numbers

* exists field: return items in which field exists

* any field LST: return items in which the value of field
  is a list and at least one element of field is an
  element of LST

* all field LST: return items in which the value of field
  is a list and the elements of field contain all the
  elements of LST

* one field LST: return items in which the value of
  field is one of the elements of LST

* info ID: return the details of the item whose
  document id equals the integer ID

* dt field EXP: return items in which the value of field
  is a date if EXP = '? date' or a datetime if EXP = '?
  time'. Else if EXP begins with  '>', '=' or '<' followed
  by a string following the format 'yyyy-mm-dd-HH-MM' then
  return items where the datetime of the field value bears
  the specified relation to the string, with hours and
  minutes ignored when the value of field is a date. E.g.,

        dt s < 2020-1-17

  would return items with @s date/times whose year <=
  2020, month <= 1 and month day <= 17.

  Alternatively,

        dt s ? date and equals itemtype *

  would return events with @s date/times that are dates,
  i.e., all day events or occasions.

Enter the command at the 'query:' prompt and press 'enter'
to submit the query and display the results. Press 'q' to
reopen the entry area to submit another query. Use up and
down cursor keys to choose from the command history (see
Command History below), submit '?' or 'help' to show this
display, submit 'l' to see a list of stored queries (see
Saved queries below) or submit 'quit', 'exit' or nothing
at all, '', to close the entry area and return to the
previous display.

[↺ contents](#contents)

#### Simple query examples {#simple-query-examples}

Find items where the summary includes a match for
"waldo":

    query: includes summary waldo

Precede a command with `~` to negate it. E.g., find
reminders where the summary does not include a match for
"waldo":

    query: ~includes summary waldo

To enter a list of values for "arg", simply separate the
components with spaces. E.g.,

    query: includes summary d waldo

would return items in which either the summary or d
(@d description) contains a match for "waldo". Similarly

    query: all t blue green

would return items with both blue and green tags or

    query: any t blue green

would return items with either a blue or a green tag. As
a last example

    query: one itemtype - *

would return items in which the item type is either '-'
or '*', i.e., either a task or an event.

Conversely, to enter a regex with a space and avoid its
being interpreted as a list, replace the space with '\s'.
E.g.,

    query: includes i john\sdoe

would return items with '@i' (index) entries such as
"John Doe/...".

Note: in the world of regular expressions '\s' matches
any white space character, including a space.

Components can be joined the using "or" or "and". E.g.,
find reminders where the summary entry contains a match
for "waldo" but the @d (description) entry does not:

    query: includes summary waldo and ~includes d waldo

[↺ contents](#contents)

#### Archive queries {#archive-queries}

Queries, by default, search the items table in the etm
database. You can preceed any query with 'a ' (the letter
'a' followed by a space), to search the archive
table instead. E.g.,

    query: a includes summary waldo or includes d waldo

will search the archive table for reminders with matches
for 'waldo' in the summary or in the description.

Queries beginning with 'a ' are, in fact, the only way
to see archived items from within etm itself.

[↺ contents](#contents)

#### Update queries {#update-queries}

Queries can not only locate reminders but also update
them. The update commands act on items returned by a
query. E.g., this query

    query: includes i john\sdoe | replace i john\sdoe
        Jane\sDoe

can be regarded as taking the reminders whose index entry,
'i', includes a match for 'john doe' and feeding them to
the 'replace' command which then takes the index entry of
each reminder and replaces each match for 'john doe' with
'Jane Doe'.

All of the update commands work the same way: a query that
returns a list of reminders is followed by a pipe symbol
surrounded by spaces, ' | ', and an update command with
its arguments. Here is the complete list of these
update commands:

* archive: if the items table is active, move the
  reminders from the items table to the archive table,
  else vice versa

* remove: remove the reminders from the database

* replace field RGX VAL: in the value of 'field', replace
  matches for RGX with VAL. If the value of 'field' is a
  list, do this for each element of the list. Remember to
  replace spaces in in both RGX and VAL with '\s'

* delete field: if the reminder has an entry for 'field',
  delete the entry

* set field VAL: set the value of 'field' to VAL
  overriding the current value if it exists

* provide field VAL: set the value of 'field' to VAL if
  there is no existing entry for 'field'

* attach field VAL: if the value of 'field' is intended to
  be a list and if VAL is not in this list, then add VAL
  to the list, creating the entry if necessary

* detach field VAL: if the value of 'field' is a list and
  this list contains VAL, then remove VAL from the list

The recommended workflow for updating reminders is first
to perfect the query to be certain that it lists just the
items you want to update. Then press 'q' and the 'up'
cursor key to restore the previous query, add ' | ' and
the update command you want with its arguments.

WARNING: Since the results may not be reversible, consider
backing up your 'etm.json' database before using update
commands. This simple query, e.g., would PERMANENTLY DELETE
ALL YOUR REMINDERS:

    query exists itemtype | remove


[↺ contents](#contents)

#### Complex queries {#complex-queries}

Return a formatted, heirarchial display of items. Both the format and the items displayed are determined by the type of the query and the arguments provided. Since these queries can group and sort by date/times, these queries must begin by specifying which of the possible datetimes to use. There are four types of datetime specifications:

* u: sort and group by datetimes in '@u' (used time) entries. Also report aggregates of times spent in these entries. Only items with '@u' entries will be reported.
* s: sort and group by datetimes in '@f' entries in finished tasks and otherwise by '@s' entries. Only items with '@f' or '@s' entries will be reported.
* c: sort and group by the 'created' datetime. All items will be reported.
* m: sort and group by the 'modified' datetime if given else by the 'created' datetime. All items will be reported.

Complex queries follow the datetime specifier with a required group/sort specification consisting of a semicolon separated list with at least one of the following components:

* index specification such as i, i[1:2] or i[1:]

    E.g. for an item with index entry '@i A/B/C':
        i      = ['A','B','C']
        i[0]   = 'A'
        i[1]   = 'B'
        i[2]   = 'C'
        i[3]   => error, list index out of range
        i[0:]  = ['A','B','C']
        i[:1]  = ['A']
        i[1:]  = ['B','C']
        i[1:2] = ['B']
        i[:2]  = ['A','B']
        i[2:]  = ['C']
        i[3:4] = i[3:] = []

    Note: using slices such as i[1:2] rather than i[1] avoids 'list index out of range errors' for index entries missing the indicated position and is strongly recommended.

    When an index specification returns an empty list, '~' is used for the missing entry. Items without an '@i' entry are given a default entry of '~' and included by default. Include 'exists i' in '-q' (discussed below) to overrule this default.

* field specification:
    l: location
    c: calendar

    Note: items without the specified field are given a default entry of '~' and included by default. Include 'exists l' or 'exists c' in '-q' (discussed below) to overrule these defaults.

* date specification:
  * year:
    * YY: 2-digit year
    * YYYY: 4-digit year
  * month:
    * M: month: 1 - 12
    * MM: month: 01 - 12
    * MMM: locale abbreviated month name: Jan - Dec
    * MMMM: locale month name: January - December
  * week: (examples based on 2020 iso week number 3):
    * W: week number: 3
    * WW: month days interval for week: Jan 13 - 19
    * WWW: interval and year: Jan 13 - 19, 2020
    * WWWW: interval, year and week number: Jan 13 - 19, 2020 #3
    * WWWWW: interval, year and week number: January 13 - 19, 2020 #3
  * day:
    * D: month day: 1 - 31
    * DD: month day: 01 - 31
    * ddd: locale abbreviated week day: Mon - Sun
    * dddd: locale week day: Monday - Sunday

Note: when a date specification is given, the datetime used depends upon the report type.
* u: the value of the datetime component of the @u entry. Items without @u entries are omitted.
* s: the value of @f when it exists and, otherwise, the value of @s. Items lacking both @f and @s entries are omitted.
* c: the created datetime.
* m: the modified datetime if it exists, else the created datetime.

E.g.

    query: u i[:1]; MMM YYYY; i[1:]; ddd D

would create a usedtime query grouped (and sorted) by the first component of the index entry, the month and year, the remaining components of the index entry and finally the month day.

Sorting note: Specifications using weeks are all sorted and grouped by by (YYYY, W). Specifications involving months are all sorted by (YYYY, M). Specifications involving days are all sorted by (D).

The group/sort specification can be followed, optionally, by any of the following:

-b begin date/datetime: omit items with earlier datetimes

-e end date/datetime: omit items with later datetimes

-q query: exclude items not satisfying this simple query. Anything that could be used in a simple query described above could be used here. E.g., "-q exists f" would display only items with an "@f" entry, i.e., finished tasks. Similarly "-q equals itemtype - and ~exists f" would limit the display to unfinished tasks.

-a append: append the contents of this comma separated list of @key characters to the formatted output. E.g., "-a d, l" would append the item description and location to the display of each item.

Note: -b and -e accept shortcuts:
* daybeg: 12am on the current day
* dayend: 12am on the following day - 1 second
* weekbeg: 12am on Monday of the current week
* weekend: 12am on Monday of the following week - 1 second
* monthbeg: 12am on the 1st of the current month
* monthend: 12am on the 1st of the following month - 1 second
* prevmonthbeg: 12am on the 1st of the previous month
* prevmonthend: 12am on the 1st of the current month - 1 second

and can be combined with period strings using w (week), d (day), h (hour) and m (minute).
E.g.:
* `weekbeg - 1w`  (the beginning of the previous week)


[↺ contents](#contents)

#### Command History {#command-history}

Any query entered at the 'query:' prompt and submitted by pressing 'Enter' is added to the command history. These queries are kept as long as 'etm' is running and can be accessed using the up and down cursor keys in the query field. This means you can enter a query, check the result, press 'q' to reopen the query prompt, press the up cursor and you will have your previous query ready to modify and submit again. It is also possible to keep a permanent list of queries accessible by shortcuts. See 'Saved Queries' below.

[↺ contents](#contents)

#### Saved Queries {#saved-queries}

Commonly used queries can be specified in the "queries" section of `cfg.yaml` in your etm home directory along with shortcuts for their use. These saved queries support positional replacements. E.g. with

    queries:
        ...
        find: includes summary d {}

the expectation would be that 'find' will be followed by a single argument to replace the '{}'. E.g.,

    query: find waldo

Entering this at the query prompt would create and then, without further input, execute the query

    includes summary d waldo

thus identifying all items in which either the summary or the description (d) contains
'waldo'.

Arguments provided to saved queries are separated by spaces. This means that

    query: find John Smith

would raise an error because two arguments, 'John' and 'Smith', have been provided but there is only one '{}' placeholder. To fix this, replace each unwanted space with an '\s'. E.g.,

    query: find John\sSmith

As another example consider 's-d' (summary but not description):

    queries:
        ...
        s-d: includes summary {0} and ~includes d {0}

Here the '{0}' placeholders mean that only one argument is expected and it will be used to replace both of the placeholders. This entry

    query: s-d waldo

would then expand to

    includes summary waldo and ~includes d waldo

which identifies items with 'waldo' in the summary but not in the description.

As a final example, suppose you use one of the tags, 'unbilled', 'billed' or 'paid', to track billing and you want to find items that have an @i entry that contains a client name that you will specify and have @t entries that contain a tag that you will also specify. Consider this specification for 'status':

    queries:
        ...
        status: includes i {} and any t {}

with '{}' placeholders for the client and the tag. Then

    query: status IOU paid

would expand to

    includes i IOU and any t paid

which would identify items for the client 'IOU' which have been tagged 'paid'. Similarly

    query: status IOU unbilled

would identify items for the same client that have been tagged 'unbilled' instead of 'paid'.

Saved queries need not, of course, take arguments. With

    queries:
        ...
        unbilled: exists u and ~any t billed paid

the query

    query: unbilled

would identify all items with an @u (used time) entry and thus presumably billable but without either a 'billed' or 'paid' tag.

Note: To see a list of all your saved queries, just enter '`l`' (lower case '`L`') at the query prompt.

        query: l


[↺ contents](#contents)

### Common Features {#Common-Features}

While the views differ in many respects, they also share some common aspects:

* Press `N` in any view to create a new item.
* Select a reminder by clicking on it or by using the up and down cursor keys to move the cursor to the line displaying the reminder.
* With a reminder selected, press `return` to toggle displaying the details.
* Movement
    * Press page up or page down to shift the display a page at a time.
    * Press “l”  (lower case L) and enter a number to move the cursor to a particular line  number.
    * In the weekly views a),  b) and c), press “j” and enter a date to display the week containing that date.
    * In the dated views a), b), c), u), U) and y), press the right or left cursor keys to go  to the next or previous period, respectively, and the space bar to return to the current period.
* Search.
    * Press “/“ (or "?") and enter an expression to search the view forward (or backward) for a row whose content contains a case-insensitive match for the expression.
    * While entering the search expression, push the `up` or `down` cursor keys to change the direction of search.
    * After entering the search expression, press “n” to search (cyclically) for other matches in the direction specified.
    * Once a search is initiated, it remains active in all views with matches highlighted. To remove the highlighting, search for something unlikely to be matched, e.g., 3 consecutive commas.


[↺ contents](#contents)

## Mobile access to your reminders {#mobile}

The files `current.txt` and `next.txt` in your etm home directory are created by *etm* but not displayed within *etm* itself. Whether or not these files are created depends on two settings in your `cfg.yaml`:

* `keep_current`:  non-negative integers for `weeks` and `width`.  If `weeks` is positive, the agenda for that integer number of weeks starting with the current week will be scaled to fit `width` and written to `current.txt` and updated whenever necessary. A width of 46, for example, works well for an iPhone in portrait mode.

* `keep_next`: true or false. If `true`, the contents of *do next* view will be written to `next.txt` in your etm home directory and updated whenever necessary.

By creating links to these files in, e.g., a GoogleDrive folder, you can have access to your current schedule and tasks on your mobile device.

Here is a screen shot from an iPhone of an illustrative `current.txt`:

<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/current_on_iphone.png" alt="new" title="current view" width="300px" hspace="20px"/>


[↺ contents](#contents)

## Menus {#menus}

Pressing F1 toggles the *etm* menu display - opening it if it is closed and closing it if it is open. There are four menu tabs labeled *etm*, *view*, *editor* and *selected* with the options listed below:

    etm
        F1) activate/close menu
        F2) about etm
        F3) system info
        F4) check for updates
        F5) import file
        F6) datetime calculator
        F7) configuration settings
        F8) help
        ---
        ^q) quit
    view
        a) agenda
        b) busy
        c) completed
        d) do next
        e) effort
        f) forthcoming
        h) history
        i) index
        j) journal
        k) konnected
        l) location
        m) timers
        o) occurrences
        p) pinned
        q) query
        r) review
        s) scheduled alerts for today
        t) tags
        u) used time
        U) used summary
        v) refresh views to fit resized terminal
        y) yearly calendar
        ^c) copy active view to clipboard
    move
        space|home) go to today in a), b) and c)
        end) prompt for and goto date in a), b), c), u), U) and y)
        right) next in a), b), c), u), U) and y)
        left) previous in a), b), c), u), U) and y)
        ---
        /|?) initiate forward|backwards search
        n|N) search next|previous incrementally
        ,,) clear search
        ^l) prompt for and jump to line number
        ^p) jump to next pinned item
    edit
        +) add new item
        J) edit today's journal entry
        ---
        ^g) test goto link
        ^r) show repetitions
        ^s) save changes & close
        ^z) discard changes and close
    selected
        enter) toggle showing details
        E) edit
        C) edit copy
        D) delete
        F) finish
        P) toggle pin
        R) reschedule
        S) schedule new
        g) open goto link
        ^h) show completion history
        ^r) show repetitions
        ^u) update last modified
        ^x) toggle archived status
        --- konnected view
        k) toggle showing konnections
    timers
        m) show timer view
        --- for the selected reminder
        T) change timer to next state
        TR) record usedtime and end timer or add usedtime
        TD) delete timer
        --- ignores selection
        TT) toggle paused/running for active timer
        ^t) start quick timer


[↺ contents](#contents)

### etm menu notes {#etm-menu-notes}


As with the other menus, each entry is preceeded by its shortcut, e.g., F2 for *about etm* or `^q` (`control` and `q` simultaneously) to quit.

Many of the entries are obvious but a few deserve comment.

* *import file* supports importing three different file types. A file ending with `.json` is expected to be one exported from *etm* 3.2.x. A file ending with  `.text` is expected to be a text file with lines corresponding to *etm* 4.x reminders. A file ending with `.ics` is expected to be a file in *iCalendar* format.

  If a file named `inbasket.text` exists in the root of the *etmdir* directory, it will be offered as the default for importing. When etm detects the presence of this file, a circled-i symbol, 𝕚, will be displayed in the right-hand end of the status bar.

  Any file located in the root of the *etmdir* will automatically be removed after it is imported to avoid duplications.
* *datetime calculator* processes an expression of the form `x [+-] y` where x is a datetime and y is either a timeperiod with `+` or a datetime or a timeperiod with `-`. As an example, suppose you have the arrival time in Paris of a flight and the departure time from Raleigh/Durham and you would like to determine the flight time. Entering

            7:45a 4/7 Europe/Paris - 5:30p 4/6 US/Eastern

    yields

            8 hours 15 minutes
* *configuration settings* opens the file `cfg.yaml` using the default text editor for your operating system. Note that any changes you make to this file will not take effect until you close and reopen *etm*.
* *help* opens the *etm* documentation on google pages using the default web browser for your system. This is the most user friendly source for the documentation because it begins with a table of contents whose elements are active links to the relevant sections. It is updated with every commit so it is always the most recent version available.

[↺ contents](#contents)

### view menu notes {#view-menu-notes}

The *view* menu provides access to all the *etm* views with the shortcut keys for these views. E.g., press `a` to open *agenda view*.

The *start quick timer* option creates a new, inbox reminder with the current datetime as the subject, associates a timer with reminder and starts the timer. If another timer is active, it will be paused if necessary and made inactive. Subsequent invocations repeat this process.

The entries here are pretty obvious and the views themselves are descibed elsewhere.

[↺ contents](#contents)

### editor menu notes {#editor-menu-notes}

It is worth noting here that when you are editing an item, `^s` (control and s) saves any changes you have made and closes the editor. `^z` (control and z), on the other hand, closes the editor without saving any changes but, if there are changes, asks for confirmation that this is what you want.

An options setting, 'vi_mode' determines which keybindings are used in the entry buffer when editing. If 'vi_mode' is true, then vi-style bindings are used and, otherwise, the default emacs-style bindings are used. The status bar describes the current mode, e.g., 'vi: insert' with a '+' appended if the contents have been modified.

[↺ contents](#contents)

### selected menu notes {#selected-menu-notes}

Options in the *selected* menu are only relevant when a reminder has been selected in one of the views.

Several options here deserve comment.

* *delete* will prompt for comfirmation and, if the selected item is repeating, for whether to delete only the selected instance or the item itself, i.e., all instances.
* *finish* applies only to unfinished tasks and will prompt for a datetime to use in creating an `@f` entry for the task with the current datetime as the default. Press
* *reschedule* will prompt for a datetime. If the reminder is repeating, the provided datetime will replace the datetime of the selected instance. Otherwise it will be used either to replace the current value of `@s` or, if there is no `@s` entry, to create one.
* *schedule new* will prompt for a datetime and add that instance to any other instances of the reminder.
* *open goto* will use the system default application to open the file path or url specified in the selected reminders `@g` entry. Items with goto links are displayed with a 'g' in the *flags* column of normal views.
* *toggle pin* toggles the pin status of an item between off and on. Items for which the pin status are displayed with a 'p', in the *flags* column of normal views and are also displayed in *pinned view*.
* *show repetitions* pops up a display showing illustrative repetitions if the item is repeating.
* *toggle archived status* moves the selected reminder from the items table if it is active to the archive table and vice versa if the archive table is active.
* *change timer to next state*.
    * These are the states for the timer associated with a reminder and the relevant status of any other timers:
        * *n* (no timer is associated with this reminder)
            * *n-*: no other timer is active
            * *n+*: another timer is active
        * *i* (a timer is associated with this reminder and it is inactive)
            * *i-*: no other timer is active
            * *i+*: another timer is active
        * *r-*: running (a timer is associated with this reminder and it is running - there cannot be another active timer)
        * *p-*: paused (a timer is associated with this reminder and it is paused - there cannot be another active timer)

    * These are the "next" state transitions associated with this action:
        * *n+* ⇒ *i+*
        * *n-* ⇒ *p-*
        * *i-* ⇒ *r-*
        * *i+* ⇒ *r-*
        * *r-* ⇒ *p-*
        * *p-* ⇒ *r-*

    * Here are the details:
        * If no timer is currently associated with the reminder, one will be created. If another timer is *active*, the new timer will be *inactive*, otherwise it will be *active* and *paused*.
        * If an *inactive* timer is already associated with the reminder. Its state will be changed to *running*. If another timer is *active*, that timer will be changed to *inactive* and, if *running*, its elapsed time will be incremented by the period it has been *running*.
        * If an *active* timer is already associated with the reminder, its state will be toggled between *paused* and *running*. With a transition from *running* to *paused*, the elapsed time for the timer in increased by the period since the timer's state changed to *running*.

      Additionally, if there is an *active* timer, its state, either *r* (running) or *p* (paused), is displayed in the *etm* status bar together with the relevant time period, either the total elapsed time or how long the timer has been paused. If there are *inactive* timers with non-zero elapsed times, the total of such elapsed times will also be reported in the status bar. E.g., this display in the status bar

            r:4m + i:13m

      would mean that the *active* timer is *running* with 4 minutes of unrecorded elapsed time and that there is an additional 13 minutes of unrecorded elapsed time in *inactive* timers.

* *record used time* with a reminder selected, will:
    * If a timer is not currently associated with the reminder, prompt for a timeperiod and ending time to use in adding a usedtime entry to the reminder.
    * If a timer is currently associated with the reminder, use its elapsed time and the last moment it was running as the defaults in the prompt for a usedtime timeperiod and ending time. If the entry is saved, the elapsed time for the timer will be reset to zero and, additionally, if the timer is currently *running*, its status will be changed to *paused*.


[↺ contents](#contents)

## Installation {#installation}


### For personal use {#for-personal-use}

The easiest way to install *etm* for personal use is to use *pip*:

    $ python3 -m pip install -U etm-dgraham

(This same command can be used to update *etm* when a new version is released.) This will install *etm* with all the needed python supporting modules. You can then start *etm* with

    $ etm <path to home>


See [Home directory](#home-directory) for details about `<path to home>`.


[↺ contents](#contents)

### For use in an isolated environment {#For-use-in-an-isolated-environment}

FIXME

Installing etm in an isolated or virtual environment (sandbox) is only slightly more complicated. Begin by using *pip* to install *pipx*:

    $ python3 -m pip install -U pipx

Now run:

    $ pipx ensurepath

to ensure that directories necessary for *pipx* operation are in your PATH environment variable and finally to install *etm* itself:

    $ pipx install etm-dgraham

(To upgrade *etm* when a new version becomes available, simply replace "install" in this command with "upgrade".) You can then start *etm* as before with

    $ etm <path to home>

Details about `<path to home>` are in [Home directory](#home-directory).

[↺ contents](#contents)

### For use system wide {#for-use-system-wide}

If your system allows you to run `sudo` and you want general access system wide, then you could instead install etm using

    $ sudo -H python3 -m pip install -U etm-dgraham

This would put both etm and etm+ in your path (in the bin directory for python3).

Notes:
* This same command would be used to update *etm* to the latest version.
* You may or may not need the '-H' argument for sudo. Here is the relevant section from the sudo man page:

        -H, --set-home
                    Request that the security policy set the
                    HOME environment variable to the home
                    directory specified by the target user's
                    password database entry.  Depending on
                    the policy, this may be the default
                    behavior.

* Invoking pip through python in this way forces the use of the pip that belongs to python3.

You can then open any terminal and start etm using

    $ etm <path to home>

See [home directory](#home-directory) for details about `<path to home>`.

[↺ contents](#contents)

## Usage {#usage}

### Terminal size and color scheme {#terminal-size-and-color-scheme}

The suggested terminal size for etm is 70 (columns) by 32 or more (rows). The default color scheme is best with a dark terminal background. A scheme better suited to light backgrounds can be set using `style: light` in `cfg.yaml` in your home directory. Some of the *etm* display may not be visible unless `style` is set correctly for your display.

The size of the terminal is used when *etm* starts to set various display options so changing the terminal size, especially reducing the width, is best avoided once *etm* is running.

[↺ contents](#contents)

### Home directory {#home-directory}

Before you start etm, think about where you would like to keep your personal data and configuration files. This will be your etm *home* directory. The default is to use whatever directory you're in when you start _etm_ as your _etm_ home directory. If you start _etm_ in your virtual environment directory then the default will be to use that as your home directory as well. If this is not what you want, you can just give the path for whatever directory you would like to use when you start _etm_.

    $ etm <path to home>

Finally, if there is an environmental variable, `ETMHOME`, set to this path then you can just enter

    $ etm

and etm will use `ETMHOME` as its home directory.

Home directory considerations:

* If more than one person will be using etm on the same computer, you might want to have different *home* directories for each user.
* If you want to use etm on more than one computer and use Dropbox, you might want to use `~/Dropbox/etm` to have access on each of your computers.
* If you want to separate personal and professional reminders, you could use different _home_ directories for each. You can run two instances of _etm_ simultaneously, one for each directory, and have access to both at the same time.
* You can have multiple instances of *etm* running with the same *home* directory, provided that you treat all instances save one as **read only**, i.e., only make changes in one instance.

Whatever *home* directory you choose, running etm for the first time will add the following to that directory.

        etm home directory/
            backups/
            logs/
            cfg.yaml
            etm.json

Here `cfg.yaml` is your user configuration file and `etm.json` contains all your etm reminders. The folders `backups/` contains the 7 most recent daily backups of your `etm.json` and `cfg.yaml` files. The folder `logs` contains the current `etm.log` file and the 7 most recent daily backups. Note that backup files are only created when the relevant file has been modified since the last backup.

The file `cfg.yaml` can be edited and the options are documented in the file.
See [configuration](#configuration) for details.

[↺ contents](#contents)

### Timers {#timers}

For tracking time spent, *etm* supports the use of one or more timers. Each timer is associated with a particular reminder and, if a timer is recorded, a used time entry will be added to the associated reminder using this format:

        @u <time spent>: <datetime recorded>

The timer itself records seconds, but the used time entry for `<time spent>` depends upon the `usedtime_minutes` setting in `cfg.yaml` as follows:

- 0: time is recorded in seconds after rounding to the nearest second
- 1: time is recorded in minutes after rounding off to the nearest minute, e.g., 1m29s => 1m; 1m30s => 2m
- 6: time is rounded up to the next one-tenth of an hour for reporting but recorded in minutes
- 12: time is rounded up to the next two-tenths of an hour for reporting but recorded in minutes
- 30: time is rounded up to the next half hour for reporting but recorded in minutes
- 60: time is rounded up to the next hour for reporting but recorded in minutes

The [Used Time Views](#used-time-views) show aggregations of these reported times by month and index entry. Any rounding up is done before aggregating.

Used time entries can be recorded directly by editing the relevant reminder and adding one or more `@u` entries. It is also possible to use *etm* to create timers *attached* to particular reminders and control them with hotkeys.

- T: with a reminder selected
    - If a timer is not already associated with this reminder, then create a new timer and associate it with this reminder
        - if another timer is active, make this timer inactive
        - otherwise make this timer active and paused
    - If a timer is already associated with this reminder
        - if the timer is inactive, make it active and running
        - otherwise toggle the state of the timer between paused and running
- TR: if a reminder is selected with an associated timer
    - open a dialog to record a used time entry with the current value of the timer and the current datetime
    - if, after possible editing, recording is confirmed then add the used time entry and delete the timer
- TD: if a reminder is selected with an associated timer
    - open a dialog to confirm deleting the timer without recording the used time
    - if deletion is confirmed then delete the timer
- TT: if there is an active timer
    - toggle the paused/running state for the active timer. Note that the reminder associated with the active timer *need not be selected*.
    - Note that if there are one or more timers, *exactly one of them will be the active timer*, i.e., either running or paused. The others, if any, will be inactive.

[Timer View](#timer-view), bound to `m`, provides a convenient way of manipulating multiple timers. It lists each existing timer with the active timer first and followed by the other timers in the order of most recently active. Pausing/running the active timer can be done from any view by pressing `TT`. To switch to another timer, change to timer view, press `TT` if necessary to pause the active timer, select the timer you want to start and press 'T' to change its state from 'inactive' to 'running'. It will move to the top of the list and the other timers will move down by one row.

When there is an active timer, either running or paused, its status will be displayed in a second line of the status bar. E.g., `6.3m r⌁10:23a' would mean that the active timer has been running since 10:23am today and has a total of 6.3m of elapsed time.  If there are other, inactive timers with positive elapsed times then the total of these times would be displayed in the first line of the status bar.

[↺ contents](#contents)

### *lorem* examples {#loremexamples}

If you are new to *etm*, you might find it very useful to install the *lorem* examples. If you press `F5`, enter 'lorem' at the prompt and press `return`, *etm* will generate a series of reminders all of which are tagged 'lorem'. These fall within a three month period including the month in which they were created as well as the previous and subsequent months. The examples are designed to illustrate nearly all of the etm views and features. You can play around with the examples as long as you wish and then remove them all at once by pressing `q` to open query view, entering the query 'any t lorem \| remove' and pressing `return`.

These examples are named for and depend upon the python package *lorem* that can generate random words, phrases, sentences and paragraphs in 'lorem ipsum' text. E.g., "Lorem ipsum dolor sit amet, consectetur adipiscing elit ...". This is "a placeholder text commonly used to demonstrate the visual form of a document or a typeface without relying on meaningful content."

[↺ contents](#contents)

### Using etm+ {#etmplus}

An added bonus of setting `ETMHOME` to the path of your *home* directory is the possibility of using the `etm+` shortcut for creating reminders. E.g., entering

    $ etm+ '* lunch with Peter @s fri 12p'
would append the line `* lunch with Peter @s fri 12p` to the file `inbasket.text`in `ETMHOME`, creating the file if necessary. `etm+` also accepts input piped to it so that

    $ echo '* lunch with Peter @s fri 12p' | etm+
would produce exactly the same result.

Finally, if `{T}` is included, it will be replaced with a time stamp corresponding to the moment the script was invoked. E.g.,

    $ echo '% got the test result at {T}' | etm+

would append something like `% got the test result at 2022-12-07 9:13:55 EST`.

Important
: The single quotes are necessary to keep the shell from expanding the "*" into the names of all the files in the current working directory and other such mischief.

*etm* checks once every minute for the presence of a file named `inbasket.text`in `ETMHOME` and, if found, will display an inbasket character, ⓘ , at the right end of its status bar reminding you that inbasket items are available for importing. Just press F5 in etm to import the reminders from this file and, on successful completion, automatically remove the file.

Note finally that `etm+` will accept quick notes which are not themselves valid etm reminders such as

    $ etm+ '123 456-7890 Peter'
This would result in the valid reminder

    ! 123 456-7890 Peter @t etm+
being appended to `inbasket.text` - note the added type character, `!` and the tag, `@t etm+`.

The addition of the typechar '!' means that after importing the reminder will appear as an 'inbox' item. These are highlighted in the list for the current day in agenda view, reminding you that they require futher attention. You can thus make quick notes without much thought and know that you will automatically be reminded to sort them out later. An added bonus is that when editing such entries in etm itself, all its completion, fuzzy parsing and verification features are available.

[↺ contents](#contents)

## Deinstallation {#deinstallation}

### From a personal installation {#from-a-personal-installation}

To remove *etm* run

    $ pip uninstall etm-dgraham

This will remove *etm* from the python site-packages directory and the *etm* and *etm+* executables from the python bin directory. Then remove any *etm home* directories that you have created.

[↺ contents](#contents)

### From a virtual environment {#from-a-virtual-environment}

Use *pipx* instead of *pip*:

    $ pipx uninstall etm-dgraham

You can now remove any *home* directories you may have created.

[↺ contents](#contents)

### From a system wide installation {#from-a-system-wide-installation}

To remove *etm* installed into, say, python3.7, run

    $ sudo -H pip uninstall etm-dgraham

This will remove *etm* from the python site-packages directory and the *etm* and *etm+* executables from the python bin directory. Then remove any *etm home* directories that you have created.

[↺ contents](#contents)

# Details {#details}

## Item Types {#item-types}

### event {#event}

Type character: **\***

An event is something that happens at a particular date or datetime without any action from the user. Christmas, for example, is an event that happens whether or not the user does anything about it.

- The `@s` entry is required and can be specified either as a date or as a datetime. It is interpreted as the scheduled date or datetime at which the event begins.
- If `@s` is a date, the event is regarded as an *occasion* or *all-day* event. Such occasions are displayed first on the relevant date.
- If `@s` is a datetime, an `@e` entry is allowed and is interpreted as the extent or duration of the event - the end of the event is then given implicitly by starting datetime plus the extent and this period is treated as busy time.

Corresponds to VEVENT in the vcalendar specification.

[↺ contents](#contents)

### task {#task}

Type character: **-**

A task is something that requires action from the user and lasts, so to speak, until the task is completed and marked finished. Filing a tax return, for example, is a task.

- The `@s` entry is optional and, if given, is interpreted as the date or datetime at which the task is scheduled to be completed.
    - Tasks with an `@s` datetime entry are regarded as past due after the datetime and are displayed in *Agenda View* on the relevant date according to the scheduled time.
    - Tasks with `@s` date entry are regarded as past due after the due date and are displayed in *Agenda View* on the due date after all items with datetimes.
    - Tasks that are past due are also displayed in *Agenda View* on the current date using the type character `<` with an indication of the number of days that the task is past due.
- Tasks without an `@s` entry are to be completed when possible and are sometimes called *todos*. They are regarded as *next* items in the *Getting Things Done* terminology and are displayed in *Do Next* view grouped by @l (location/context).
- Tasks with an `@r` (repeat) or an `@+` entry can have an `@o` (overdue) setting.
    - `@o k`: keep. Whenever completed, the next instance is due at the datetime specified in the recurrance rule even if that datetime has already passed. E.g. minutes from a monthly meeting to be made on the 1st of the month are due for each prior month in which they have not been made. With this option, many instances can be past due. By default, a completion applies to the oldest, past due one, though other instances can be selected. The default when no `@o` entry is given is `@o k`.
    - `@o r`: reset. Whenever completed, the next instance is due at the first datetime that falls after the current datetime. E.g., getting a haircut every 14 days is due 14 days after the last haircut. With this option, at most one instance can be past due.
    - `@o s`: skip. Like 'keep' with the addition that past due instances are ignored. E.g., taking out the trash every Monday morning for pickup is due every Monday morning but, if a Monday passes without taking out the trash, the instance is better regarded as irrelevant than past due. With this option, an instance can never be past due.

        Furthermore, if the options setting `limit_skip_display` were true, then only the first instance of such a task would be displayed in agenda view. E.g., with the `limit_skip_display` setting true, then for the task

            - meds @s +0d @r d &h 8,14,20 @o s

        agenda view at 10am today would only display the first, 2pm (14h) instance of this task. If, on the other hand, this setting were false, then agenda view would display not only the 2pm instance but also the 8pm (20h) instances and all three instances on every future date.

- Jobs
    - Tasks, both with and without @s entries can have component jobs using @j entries.
    - For tasks with an @s entry, jobs can have an &s entry to set the due date/datetime for the job. It is entered as a timeperiod relative to  the scheduled datetime (+ before or - after) for the task. Zero minutes is the default when &s is not entered.
    - For tasks with an @s entry, jobs can also have &a, alert, and &b, beginning soon, notices. The entry for &a is given as a time period relative to &s (+ before or - after) and the entry for &b is a positive integer number of days before the scheduled date/time to begin displaying "beginning soon" notices. The entry for @s in the task becomes the default for &s in each job.  E.g., with

            - beginning soon example @s 1/30/2018
                @j job A &s 5d &b 10
                @j job B &b 5

        Beginning soon notices would begin on Jan 15 for job A (due Jan 25) and on January 25 for job B (due Jan 30).
    - Prerequisites
        - Automatically assigned. Here it is supposed that jobs must be completed sequentially in the order in which they are listed. E.g., with

                - automatically assigned
                    @j job A
                    @j job B
                    @j job C
                    @j job D

            `job A` has no prerequisites but is a prerequisite for `job B` which, in turn, is a prerequisite for `job C` which, finally, is a prerequisite for `job D`.

            Auto assignment is done when the task is first saved by assigning 'a', 'b', 'c', ... as ids for the successive jobs with 'a' as a prerequisite for 'b', 'b' for 'c' and so forth. The task is then saved as

                - automatically assigned
                    @j job A &i a
                    @j job B &i b &p a
                    @j job C &i c &p b
                    @j job D &i d &p c

            and thereafter treated as if the ids and prerequisites had been manually assigned. Note that at most 26 jobs are possible with auto assignment.

            Once ids and prerequisites have been assigned, it is sometimes useful to be able to add a job here or there or change the order of existing jobs and have the ids and prerequisites generated again. To do this simply remove the `&i` and `&p` entries from the *first job* and save the task - *all* job ids and preqrequisites will automatically be reassigned.
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

[↺ contents](#contents)

### journal {#journal}

Type character: **%**

A record of something that the user wants to remember. The userid and password for a website would be an example. A journal entry for vacation day is another example.

- The `@s` is optional and, if given, is interpreted as the datetime to which the journal entry applies.
- Journal entries without @s entries might be used to record personal information such as account numbers, recipies or other such information not associated with a particular datetime. They are displayed in the *Journal* view
- Journal entries with @s entries associate the entry with the datetime given by @s. A vacation log entry, for example, might record the highlights of the day given by @s. They are displayed in *Agenda* view as well as *Journal* view.
- While Journal entries do not support repetition using `@r` entries, they do support the use of `@+` entries to add additional dates or datetimes to that provided by the `@s` entry.

Corresponds to VJOURNAL in the vcalendar specification.

[↺ contents](#contents)

### inbox {#inbox}

Type character: **!**

An inbox item can be regarded as a task that is always due on the current date. E.g., you have created an event to remind you of a lunch meeting but need to confirm the time. Just record it using **!** instead of **\*** and the entry  will appear highlighted in the agenda view on the current date until you confirm the scheduled time.

Inbox items are also useful when you have an idea but not enough time to think about it. Create an inbox entry with just enough information in the summary to remind you of the idea. Make a habit at the end of the day of checking inbox items. The idea is not necessarily to complete them but to change those that can’t be finished quickly to, say, undated tasks with appropriate `@l` entries and enough detail in the summaries and the `@d` descriptions so that you will have all the information you need to act on them when the time comes.

Corresponds to VTODO in the vcalendar specification.

[↺ contents](#contents)

### status {#status}

These type characters are generated automatically by *etm* to display the status of reminders.

[↺ contents](#contents)

#### beginning soon {#beginning-soon}

Type character: **>**

For unfinished tasks and other items with `@b` entries, when the scheduled date given by `@s` is within `@b` days of the current date, a warning that the item is beginning soon appears on the current date together with the item summary and the number of days remaining until the current date.

[↺ contents](#contents)

#### past due {#past-due}

Type character: **<**

When a task is past due, a warning that the task is past due appears on the current date together with the item summary and the number of days that the task is past due.

[↺ contents](#contents)

#### waiting {#waiting}

Type character: **+**

When a task job has one or more unfinished prerequisites, it is displayed using **+** rather than **-**.

[↺ contents](#contents)

#### finished {#finished}

Type character: **✓**

When a task or job is finished, it is displayed in the _completed view_ on the  date that it was finished using **✓** rather than **-**.

[↺ contents](#contents)

## Options {#options}

Notes:

* The term "list" means a comma and space separated list of elements, e.g.,

    @+ 2p Thu, 9p Mon, 11a Wed

* Options displayed with an asterick can be used more than once, e.g.,

    @a 1h, 30m: t, v @a 1d: e

    @n joe: jdoaks@whatever.com  @n john: jsmith@wherever.org

    @t red  @t green

<h3 id="atkeys">
@ keys
</h3>

`@` followed by a character from the list below and a value appropriate to the key is used to apply attributes to an item. E.g.,

            @s mon 9a

would specify the the scheduled datetime for the item is 9am on the Monday following the current date.

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
*  @i: index. forward slash delimited string. E.g., client/project/activity
*  @j*: job summary. string, optionally followed by job &key entries
*  @k*: doc_id. connect this reminder to the one corresponding to doc_id.
*  @l: location (aka context). forward slash delimited string. E.g., home/maintenance
*  @m: mask. string stored in obfuscated form
*  @n*: attendee. string using "[name:] address" format. If "address" begins with exactly 10 digits followed by an "@" it is treated as a mobile phone number. Otherwise it is treated as an email address. The optional "name:" can be used to facilitate autocompletion.
*  @o: overdue. character from (r) restart, (s) skip, (k) keep. Defaults to (k) keep.
*  @p: priority. integer from 0 (none), 1 (low), 2 (normal), 3 (high), 4 (urgent)
*  @r*: repetition frequency, a character from (y)early, (m)onthly, (w)eekly,
  (d)aily, (h)ourly or mi(n)utely, optionally followed by repetition &key entries
*  @s: scheduled date or datetime
*  @t*: tag. string
*  @u*: usedtime. string using "timeperiod spent: ending datetime" format
*  @w: wrap. A pair of before and after timeperiods to extend the busy period for an event, e.g., for travel time to and/or from the location of the event. Use `0m` as one of the timeperiods to avoid a wrap in that direction.
*  @x*: expansion. string
*  @z: timezone. string. A timezone specification, such as 'US/Eastern' or 'Europe/Paris' for aware datetimes or 'float', to indicate a naive or floating datetime. Datetime entries in the item are interpreted as belonging to the specified timezone when the entry is saved. The current timezone is the default when @z is not specified. Aware datetimes are converted to UTC (coordinated universal time) when stored and the @z entry, now irrelevant, is discarded.

<h3 id="ampkeys">
& keys
</h3>

& followed by a character from one of the lists below. These keys are only used with @j (job) and @r (repetition) entries.

For use with @j:

*  &s: scheduled: period relative to @s entry (default 0m) at which job is scheduled to be completed
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


[↺ contents](#contents)

## Notes {#notes}

### notices {#notices}

* A link character, 'g', is appended to the *flags* column of any reminder with an `@g` goto link. Press `^g` with such a reminder selected to have the operating system open the link using the default application if the link can be interpreted as a file path or a url. E.g. if the link is a URL, then it would be opened using the default browser. If link can be interpreted as a shell command followed by arguments, then the command would be executed with the arguments.
* An in-basket character, ⓘ , is appended to the right end of the status bar when a file named 'inbasket.text' is found in the etm root directory. This file should contain lines containing etm reminder entries - one on each line. It can be imported using the import file command bound to F5.
* An update available character, 𝕦, is appended to the right end of the status bar when checking for updates is enabled and a later version of etm is available. Details for enabling checking for updates are in [configuration](#configuration).
* Alerts and beginbys can be added to any reminder with an `@s` scheduled date/time entry. Alerts require a datetime in `@s`; beginbys also allow a date in `@s`.
* A beginby is specified by adding `@b n` to a reminder where `n` is a positive integer and is interpreted as a number of days. A reminder with such an entry will be displayed in *agenda view* on the current date provided that the current date is no more than `n` days before the scheduled date/time of the reminder. Such a warning will appear n days before, n-1 days before and so forth until 1 day before the scheduled date/time of the reminder. The warning displays the type character `>`, the summary of the reminder and the number of days remaining.
* An alert is specified by adding `@a <list of time periods>: <list of commands>` to a reminder. The time periods must be given in the usual etm format, e.g., `1h13m` for one hour and 13 minutes. The commands are single alphabetic characters, e.g., `a`, `b` and such. The commands used must either be `e` (email) or `t` (text) or be specified in the `alerts` section of the `cfg.yaml` file in your etm home directory. See [configuration](#configuration) for details about this file. Basically, it associates a command, such as `v` with a shell command to be invoked when an alert that includes `v` is triggered. E.g., the alert

            @a 20m: v

    would be triggered 20 minutes before the datetime specified in the reminder's `@s` entry and at that time the shell command associated with `v` would be invoked. Both positive (before) and negative (after) time periods can be used. Thus this entry

            @a 1d, -1h: v, w

    would invoke the shell commands associated with `v` and `w`, one day *before* and again 1 hour *after* the datetime specified in the reminder's `@s` entry.
* Reminders can have more than one `@a` alert entries. Different alerts could, for example, be used to trigger their commands at different times.
* With an email, `e`, or text alert, `t`, the item summary is used as the subject and an email or text message is sent to each attendee listed in @n entries. The content of the body of the emails/messages are options that can be set in the user's configuration file.
* Alerts and beginbys are only triggered for unfinished tasks and, when the task is repeating, only for the first unfinished instance. Similarly, past due notices for repeating tasks are only triggered for the first unfinished instance.
* Events with `@w <before>, <after>` *wrap* entries have 'busy periods' that extend from `<before>` (a time period) before the beginning of the event until `<after>` (another time period) after the end of the event. An entry such as `@w 30m, 0m` could be used, for example, to block out 30 minutes before a meeting to review your notes or, as another example, `@w 30m, 20m` to block out 30 minutes before and 20 minutes after an event to allow for travel time to and from the event's location. The additional busy time is displayed in *busy view* as well as in *agenda view* where the event

        * sales meeting @s 22/11/15 3p @e 1h30m @w 30m, 20m

    would appear as

        ~   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·   2:30pm
        * sales meeting ·  ·  ·  ·  ·  ·  ·  ·  ·  3-4:30pm
        ~   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·   4:50pm

[↺ contents](#contents)

### repetition {#repetition}

* Daylight savings time using @s and @r. The time specified in @s is respected in the repetitions. E.g., the first five repetitions for

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
            └──────────────────────────────────┘

    Note that all start at 9am even though the first 3 are EST and the last 2 are EDT.
* Using @s with @r and with @+. Datetimes from @+ are added to the datetimes generated from the @r entry. Note that the datetime from @s will only be included if it matches one generated by the @r entry or by one included in @+. E.g.,

        * my event @s 2018-02-15 3p @r d &h 18 @+ 2018-03-02 4p

    would repeat daily at 6pm starting Feb 15 and at 4pm on Mar 2, *but not* at 3pm on Feb 15 which is specified in `@s`.
* Using @s with @+ but without @r. Datetimes from @+ are added to @s. E.g.,

        * my event @s 2018-02-15 3p @+ 2018-03-02 4p

    would repeat at 4pm on Mar 2 *and* at 3pm on Feb 15 since `@r` is not specified.
* Using &c and &u in @r. It is an error in *dateutil* to specify both &c (count) and &u (until) since providing both would be at best redundant and at worst conflicting.

    A distinction between using @c and @u is worth noting and can be illustrated with an example. Suppose an item starts at 10am on a Monday and repeats daily using either count, &c 5, or until, &u fri 10a.  Both will create repetitions for 10am on each of the weekdays from Monday through Friday. The distinction arises if you later decide to delete one of the instances, say the one falling on Wednesday, using @-. With *count*, you would then have instances falling on Monday, Tuesday, Thursday, Friday *and Saturday* to satisfy the requirement for a count of five instances. With *until*, you would have only the four instances on Monday, Tuesday, Thursday and Friday to satisfy the requirement that the last instance falls on or before 10am Friday.


[↺ contents](#contents)

#### repetition examples {#repetition-examples}

* Christmas (an all day event) [r]epating (y)early on Dec 25.

        * Christmas @s 2015/12/25 @r y

* Get a haircut (a task) on the 24th of the current month and then [r]epeatedly at (d)aily [i]ntervals of (14) days and, [o]n completion, (r)estart from the last completion date:

        - haircut @s 24 @r d &i 14 @o r

* Reconcile accounts (a task) on the 2nd day of the current month and then [r]epeatedly at (m)onthly intervals on the second day of the month (&m 2) at midnight (&h 0 &n 0). *etm* will treat midnight as a date rather than a datetime. [o]n completion, (r)restart from the last completion datetime:

        - reconcile accounts @s 2 @r m &m 2 &h 0 &n 0 @o r

* Take out trash (at task) on Mondays but if the task becomes [o]verdue, (s)kip the past due reminders.

        - Take out trash @s mon @r w @o s

* A sales meeting (an event) [r]epeating m)onthly on [w]eekdays that are either the first or third Tuesdays in the month.

        * sales meeting @s tue 9a @e 45m @r m &w 1tu, 3tu

* Good Friday each year 2 days before [E]aster Sunday.

        * Good Friday @s 1/1/2015 @r y @E -2

* Friday tennis at 9:30am in November, December, January and February and at 8am in the other months:

        * Friday tennis @s 2019-01-01 6a @e 90m
          @r m &w fr &M 1, 2, 11, 12 &h 9 &n 30
          @r m &w fr &M 3, 4, 5, 6, 7, 8, 9, 10 &h 8 &n 0

* Payday on the last week day of each month. The &s -1 part of the entry extracts the last (-1) date which is both a weekday and falls within the last three days of the month):

        * payday @s 1/1 @r m &w MO, TU, WE, TH, FR &m -1,
          -2, -3 &s -1

[↺ contents](#contents)

#### anniversary substitutions {#anniversary-substitutions}

Repeating events or tasks can have an anniversary expression, {XXX}, in the summary that will be replaced by the appropriate ordinal for the anniversary: 1st, 2nd, 3rd, etc. E.g.,

    * {XXX} of 60 auto payments due @s 2020-06-01 @r m &c 60

would appear in agenda view

*   On July 1 2020
       * 1st of 60 auto payments due
*   On Aug 1 2020
       * 2nd of 60 auto payments due

...
*   On May 1 2025
       * 59th of 60 auto payments due
*   On Jun 1 2025
       * 60th of 60 auto payments due

Similarly

    * Will's {XXX} birthday @s 1985-08-23 @r y

would appear in agenda view on Aug 23, 2020 as

* Will's 35th birthday

As a final example, newlyweds might want to celebrate anniversaries initially at monthly intervals

    * Our {XXX} monthly anniversary @s 2020-06-18 @r m

and then eventually change to yearly celebrations by removing the 'monthly' and changing the 'm' to 'y'.

In addition to monthly and yearly frequencies, `d` (daily) and `w` (weekly) are also supported.

[↺ contents](#contents)

### archived reminders {#archived-reminders}

When a reminder is 'archived' in *etm*, it is is moved from the *items* table in the database to the *archive* table. Reminders in the *archive* table can only be viewed by opening *query view* and then beginning the query with 'a' to use the *archive* table. All other views display reminders from the *items* table.

There are two ways to archive a reminder:
* Automatically. If 'archive_after' in the configuration settings is set to a positive integer, then tasks with finished datetimes and events with last datetimes more than this number of years before the current date will be achived automatically at the beginning of each new day. Note that unfinshed tasks, journal entries, inbox reminders and reminders with an @k konnection entry are never automatically archived.
* Manually. Select a reminder and press `^x` (control and x) to archive it.

There is only one way to un-archive a reminder. Run a query beginning with 'a' in *query* view to use the archive table, select a reminder and press `^x`. This will un-archive the reminder, i.e., move it back to the *items* table.

[↺ contents](#contents)

### configuration {#configuration}

Configuration settings for *etm* are specified in the file `cfg.yaml` located in your etm *home directory*. See [installation](#installation) for the location of this directory. When *etm* is running, you can press `F8` to open this configuration file using your system default editor for *yaml* (text) files. Note that any changes you make will not become effective until you stop and restart *etm*.

Here are the options with their default values from that file. The lines beginning with `#` are comments that describe the settings.

        #### begin cfg.yaml ####
        etmversion: 5.0.12
        # The current version of etm and this file. DO NOT EDIT. This is
        # automatically updated when a new version of etm is installed.

        ampm: true
        # true or false. Use AM/PM format for datetimes if true else
        # use 24 hour format. See also the show_minutes setting.

        show_minutes: false
        # true or false. If true show ":00" in agenda and forthcoming views
        # when displaying times with zero minutes else suppress zero minutes
        # from being displayed. E.g., "9:00-10:30" if true else "9-10:30".
        # When ampm if false and show_minutes is true, hours will be displayed
        # with leading zeros applicable.

        dayfirst:  false
        yearfirst: true
        # each true or false. Whenever an ambiguous date is parsed, dayfirst
        # and yearfirst parameters control how the information is processed
        # using this precedence:
        # yearfirst: true
        #   dayfirst: true  => YDM
        #   dayfirst: false => YMD
        # yearfirst: false
        #   dayfirst: true  => DMY
        #   dayfirst: false => MDY
        # E.g., with both true, 3/4/5 would be interpreted as May 4, 2003.
        # When possible, dates will also be displayed respecting these settings.
        # I.e., the year will generally be displayed first when yearfirst is
        # true and last otherwise. Similarly, the day will generally be displayed
        # before the month when dayfirst is true and after the month otherwise.

        beginbusy: 7
        # non-negative integer. The number of hours after midnight to begin the
        # busy view display of busy times for each day. The display continues
        # for 14 hours after the begin_busy hour. E.g. with 'begin_busy: 7' the
        # display would show busy times from 7am (7h) until 9pm (21h).

        updates_interval: 0
        # non-negative integer. If positive,  automatically check for updates
        # every 'updates_interval' minutes. If zero, do not automatically
        # check for updates. When enabled, a blackboard u symbol, 𝕦, will be
        # displayed at the right end of status bar when an update is available
        # or a question mark when the check cannot be completed as, for
        # example, when there is no internet connection.

        locale: en_US
        # locale abbreviation. E.g., "en_AU" for English (Australia), "en_US"
        # for English (United States), "fr_FR" for French (France) and so
        # forth. Google "python locale abbreviatons" for a complete list."

        vi_mode: true
        # true or false. Use vi keybindings for editing if true else use emacs
        # style keybindings.

        secret: HIr13FiYj3
        # string to use as the secret_key for @m masked entries. E.g.
        # 'X6i2SGWu6m'. In etm versions after 4.0.21, the default string is
        # randomly generated when this file is created or when the secret
        # value is removed and etm is restarted. WARNING: if this key is
        # changed, any @m entries that were made before the change will be
        # unreadable after the change.

        omit_extent:
        # A list of calendar names. Events with @c entries belonging to this
        # list will only have their starting times displayed in agenda view
        # and will neither appear nor cause conflicts in busy view.

        keep_current: [3, 46]
        # A list of two, non-negative integers for "weeks" and "width". If
        # weeks is positive, the agenda for that integer number of weeks
        # starting with the current week will be written to "current.txt" in
        # your etm home directory and updated when necessary. The format will
        # be scaled to fit "width". A width of 46, e.g, fits an iPhone display
        # in portrait mode. You could, for example, create a link to
        # "current.txt" in a pCloud or GoogleDrive folder and always have access
        # to your current agenda on your mobile device.

        keep_next: true
        # true or false. If true, the 'do next' view will be written to
        # "next.txt" in your etm home directory. As with "current.txt", a link
        # to this file could be created in a pCloud or DropBox folder for
        # access from your mobile device.

        archive_after: 0
        # non-negative integer. If zero, do not archive items. If positive,
        # finished tasks and events with last datetimes falling more than this
        # number of years before the current date will automatically be
        # archived on a daily basis.  Archived items are moved from the
        # "items" table in the database to the "archive" table and will no
        # longer appear in normal views. Note that unfinished tasks and
        # journal entries are not archived.

        refresh_interval: 6
        # 6, 12, 30 or 60. The event loop responsible for refreshing
        # etm caches, updating alerts, timers and so forth, repeats once
        # every refresh_interval seconds.

        num_finished: 0
        # non-negative integer
        # If positive, when saving retain only the most recent "num_finished"
        # completions of an infinitely repeating task, i.e., repeating without
        # an "&c" count or an "&u" until attribute. If zero or not infinitely
        # repeating, save all completions.

        num_repetitions: 10
        # positive integer
        # Show at most this number of repetitions when showing repetitions
        # with (^r) or when showing completion history (^h). In the former
        # case these are instances for the selected item (repeating of any
        # item type) starting from date of the selected item and in the latter
        # case these are the completion instances (task item type). Note that
        # the num_finished setting can affect the number available for display
        # for the completion history.

        limit_skip_display: false
        # true or false. If true, only the first instance of a task with "@o
        # s" (overdue skip) will be displayed. For a task with an "@s" entry
        # that is a date this will be the first instance that falls on or
        # after the current date. Otherwise, when the "@s" entry is a
        # datetime, this will be the first instance that falls on or after the
        # current time.

        connecting_dots: true
        # true or false. If true, display dots connecting the item summary and
        # the right-hand details columns in tree views.

        usedtime_minutes: 6
        # 0, 1, 6, 12, 30 or 60. Round up used times. With 0, no rounding is done
        # and times are reported in hours, minutes and seconds. With 1, after
        # rounding up to the nearest minute, times are reported as hours and minutes.
        # Otherwise, rounding is up to the nearest integer multiple of
        # usedtime_minutes and times are reported as floating point hours. E.g.,
        # with usedtime_minutes = 6, 1 minute would be rounded up to 6 minutes and
        # reported as 0.1 hours. Similarly 13 minutes would be rounded up to 18
        # minutes and reported as 0.3 hours. The numbers 6, 12, 30 and 60 are
        # characterized by the fact that each is an integer multiple of 6 and 60 is
        # evenly divisible by each. This allows reported times to be expressed as
        # hours and tenths of an hour for each. Note that when rounding is specified,
        # each "@u" timeperiod is rounded before aggregation. Whatever the setting,
        # a used time record created using the timer is accurate to the nearest
        # second.

        usedtime_hours: 6
        # 0, 1, 2, ..., 24. The daily goal for used time. This is used in effort
        # view to control the display of the daily used time bars. The goal is to
        # to maximize the granularity of the bar when displaying this number of hours
        # in the space allowed by the terminal width.

        journal_name: daily
        # Journal items with this index entry and with an @s entry will have the
        # year and month appended to the index. E.g., with the setting
        #   journal_name: daily
        # this journal entry
        #   % visited Yellowstone @s 22/6/24 @i daily
        # would be displayed in journal view as if the index entry were
        #   @i daily/2022/ 6
        # thus organizing such entries by the year and month of their scheduled dates.
        # Within each month, entries will be also ordered by the month day.

        alerts:
        # A dictionary with single-character, "alert" keys and corresponding
        # "system command" values. Note that characters "t" (text message) and
        # "e" (email) are already used.  The "system command" string should be
        # a comand with any applicable arguments that could be run in a
        # terminal. Properties of the item triggering the alert can be
        # included in the command arguments using the syntax {prop}, e.g.,
        # {summary} in the command string would be replaced by the summary of
        # the item. Similarly {start} by the starting datetime, {time} by the
        # starting time (omits the date for the current date), {when} by the time
        # remaining until the starting datetime, {now} by the current time,
        # {location} by the @l entry and {description} by the @d entry. E.g., If
        # the event "* sales meeting @s 2019-02-12 3p" triggered an alert 30 minutes
        # before the starting time the string "{summary} {when}" would expand to
        # "sales meeting in 30 minutes". E.g. on my macbook
        #
        #    alerts:
        #        v:   /usr/bin/say -v "Alex" "{summary}, {when}"
        #        ...
        #
        # would make the alert 'v' use the builtin text to speech sytem
        # to speak the item's summary followed by a slight pause
        # (the comma) and then the time remaining until the starting
        # time, e.g., "sales meeting, in 20 minutes" would be triggered
        # by including "@a 20m: v" in the reminder.

        expansions:
        # A dictionary with 'expansion name' keys and corresponding
        # 'replacement string' values. E.g. with
        #
        #    expansions:
        #        tennis: "@e 1h30m @a 30m: d @i personal:exercise"
        #        ...
        #
        # then when "@x tennis" is entered the popup completions for
        # "@x tennis" would offer replacement by the corresponding
        # "@e 1h30m @a 30m: d @i personal:exercise".

        sms:
        body: '{location} {when}'
        from: 'None'
        server: 'None'
        pw: 'None'
        # Settings to send "t" (sms text message) alerts to the
        # list of phone numbers from the item's @n attendee
        # entries using the item's summary and the body as specified
        # in the template below as the message. E.g., suppose you
        # have a gmail account with email address "who457@gmail.com"
        # and want to text alerts to Verizon moble phone (123)
        # 456-7890. Then your sms entries should be
        #     from:   who457@gmail.com
        #     pw:     your gmail password
        #     server: smtp.gmail.com:587
        # and your item should include the following attendee entry
        #     @n 1234567890@vzwpix.com
        # In the illustrative phone number, @vzwpix.com is the mms
        # gateway for Verizon. Other common mms gateways are
        #     AT&T:     @mms.att.net
        #     Sprint:   @pm.sprint.com
        #     T-Mobile: @tmomail.net
        # Note. Google "mms gateway listing" for other alternatives.

        smtp:
        body: '{location} {when}\n{description}'
        from: 'None'
        server: 'None'
        id: 'None'
        pw: 'None'
        # Settings to send "e" (email message) alerts to the list of email
        # addresses from the item's @n attendee entries using the item's
        # summary as the subject and body as the message. E.g., if you have a
        # gmail account with email address "whatever457@gmail.com", then your
        # entries should be
        #     from: whatever457@gmail.com
        #     id: whatever457
        #     pw: your gmail password
        #     server: smtp.gmail.com

        locations:
        # A dictionary with location group names as keys and corresponding
        # lists of locations as values. When given, do next view will group
        # items first by the location group name and then by the location
        # within that group. Note that locations can appear under more than
        # one group name. E.g.,
        # locations:
        #    home: [home, garage, yard, phone, computer]
        #    work: [work, phone, computer, copier, fax]
        # Items with a location entry that does not belong to one of these
        # location groups will be listed under 'OTHER' and items without a
        # location entry under 'OTHER' and then tilde.

        queries:
        td: 'm l -q equals itemtype - and ~exists f'
        ui: 'u i[:1]; MMM YYYY; i[1:2] -a d'
        si: 's i[:1]; MMM YYYY; i[1:2] -a u, d'
        mi: 'exists u and ~exists i'
        arch: 'a exists itemtype'
        uw: 'u WWW; ddd D -b weekbeg - 1w -e weekend'
        find: 'includes summary d {}'
        f: 'includes summary d {}'
        index: 's MMM YYYY; ddd D -q in i {}'
        # A dictionary with short query "keys" and corresponding "query"
        # values. Each "query" must be one that could be entered as the
        # command in query view. Keys can be any short string other than
        # 'a', 'u', 'c' or 'l' which are already in use.
        # queries:
        #    td: m l -q equals itemtype - and ~exists f
        #    mi: exists u and ~exists i
        #    arch: a exists itemtype
        #    find: includes summary d {}
        # The latter would allow you to enter, e.g., `find waldo` and have
        # it expand to `includes summary d waldo` and thus locate all
        # reminders with `waldo` either in the summary or d (the description).

        style: dark
        # dark or light. Set the defaults for dark or light terminal
        # backgounds. Some output may not be visible unless this is set
        # correctly for your display.

        type_colors:
        # A dictionary with type keys and corresponding named-color or hex
        # values. The default colors are determined by the 'dark' or 'light'
        # style setting as follows:
        #
        #     key           dark default        light default
        #  -----------    -----------------   -----------------
        #  available       'LightSkyBlue',     'DarkBlue',
        #  begin           'Gold',             'DarkViolet',
        #  event           'LimeGreen',        'DarkGreen',
        #  finished        'DarkGrey',         'LightSlateGrey',
        #  inbox           'OrangeRed',        'MediumVioletRed',
        #  journal         'GoldenRod',        'Brown',
        #  pastdue         'LightSalmon',      'Red',
        #  plain           'Ivory',            'Black',
        #  today           'Ivory bold',       'Black bold',
        #  used            'Khaki',            'DodgerBlue',
        #  waiting         'SlateGrey',        'DarkSlateBlue',
        #  wrap            'ForestGreen',      'LightGrey',
        #  running         'OrangeRed',        'Gold',
        #  paused          'MediumVioletRed',   'DarkViolet',
        # Explanations for the key names:
        #     available:    available task/job reminders
        #     begin:        begin by warnings
        #     event:        event reminders
        #     finished:     finished task/job reminders
        #     inbox:        inbox reminders
        #     journal:      journal reminders
        #     pastdue:      pasdue task warnings
        #     plain:        headings such as outline branches
        #     today:        the current and following agenda date headings
        #     used:         used time rows in effort and used time views
        #     waiting:      waiting job reminders (jobs with unfinished prereqs)
        #     wrap:         before and after rows for events in agenda view with
        #                   @w entries
        #     running:      status bar color for 'r', running timer
        #     paused:       status bar color for 'p', paused timer
        #
        # E.g., with style 'dark', the default color for 'available' is
        # 'LightSkyBlue'. This entry
        #   colors:
        #       available: CornFlowerBlue
        # would change the 'available' color to 'CornflowerBlue' while leaving
        # the other 'dark' colors unchanged.
        #
        # To preview the namedcolors, download "namedcolors.py" from
        #    "https://github.com/dagraham/etm-dgraham",
        # open a terminal with your chosen background color and run
        #    python3 <path to namedcolors.py>
        # at the command prompt.

        window_colors:
        # A dictionary with style component keys and corresponding lists of
        #    [background, foreground, attribute]
        # components. background and foreground can either be named colors,
        # hex colors, or ''. Attribute is an optional font attribute such
        # as 'bold' which must, of course, be supported by the font used in
        # your terminal. The default settings are determined by the 'dark'
        # or 'light' style setting as follows:
        #
        #    key                       dark default                  light default
        # -------------------    -----------------------------  -----------------------------
        # ask:                    [grey2, Lime, bold]           [Cornsilk, Lime, bold]
        # button.focused:         [DarkGreen, White]            [DarkGreen, White]
        # details:                [, Ivory]                     [, Black]
        # dialog shadow:          [#444444, ]                   [#444444, ]
        # dialog:                 [DarkSlateGrey, White]        [DimGrey, White]
        # dialog-entry:           [White, Black]                [White, Black]
        # dialog-output:          [DarkSlateGrey, Lime]         [DimGrey, Lime]
        # dialog.body label:      [, White]                     [, White]
        # dialog.body:            [DarkSlateGrey, White]        [DimGrey, White]
        # entry:                  [grey2, LightGoldenRodYellow] [Cornsilk, LightGoldenRodYellow]
        # frame.label:            [DarkSlateGrey, White]        [DimGrey, White]
        # menu:                   [DarkSlateGrey, White]        [DimGrey, White]
        # menu-bar:               [grey1, White]                [grey1, White]
        # menu-bar.selected-item: [#ffffff, #000000]            [#ffffff, #000000]
        # menu.border:            [, #aaaaaa]                   [, #aaaaaa]
        # not-searching:          [, #222222]                   [, #777777]
        # query:                  [, Ivory]                     [, Black]
        # reply:                  [grey2, DeepSkyBlue]          [Cornsilk, DeepSkyBlue]
        # shadow:                 [#222222, ]                   [#222222, ]
        # status:                 [grey1, White]                [grey1, White]
        # status.key:             [, #ffaa00]                   [, #ffaa00]
        # status.position:        [, #aaaa00]                   [, #aaaa00]
        # text-area:              [grey2, Ivory]                [Cornsilk, Black]
        # window.border shadow:   [, #444444]                   [, #444444]
        # window.border:          [, #888888]                   [, #888888]
        #
        # Note that 'grey1' (#396060) and 'grey2' (#1d3030) are colors named
        # within etm itself. They are, respectively, one shade lighter and two
        # shades darker than DarkSlateGrey.
        #
        # Any of the style attributes above can be modified. E.g., with style
        # 'dark', the default for 'text-area' is [grey2, Ivory]. This entry
        #   window_colors:
        #       text-area: [Black, White]
        # would change the 'text-area' setting to 'Black' as the background color
        # and 'White' as the foreground color while leaving the other style settings
        # unchanged.
        #### end cfg.yaml ####


See [Saved Queries](#saved-queries) for more information about queries that allow for replaceable parameters.

Note that in the 'dictionary' entries above, the components must be indented (using 2 spaces not tabs). E.g., the illustrative alert entry would be:

    alerts:
        v: /usr/bin/say -v "Alex" "{summary}, {when}"


[↺ contents](#contents)

### data storage {#data-storage}

All *etm* reminders are stored in the text file `etm.json` in your etm home directory using the wonderful *TinyDB* package. [Prior to etm 5.0.0, the data storage file was named `db.json`. The format and name changed slightly with that version.] This *json* file is human readable but not easily editable. When you start *etm* for the first time, this file will have no entries:

    {
    "items": {},
    "archive": {}
    }

To *json* this is a hash/dictionary with two keys: "items" and "archive". Both have empty hashes/dictionaries as values.
Add a first reminder to take out the trash on Mondays

    - trash @s 2019-12-21 @r w &w mo

at 10:26am on Dec 21, 2019 EST and the file would change to

    {
    "items": {
    "1": {
    "itemtype": "-",
    "summary": "trash",
    "s": "{D}:20191223",
    "r": [
        {
        "r": "w",
        "w": [
        "{W}:MO"
        ]
        }
    ],
    "created": "{T}:20191221T1526A"
    }
    },
    "archive": {}
    }

`items` now has a first item with key (unique identifier) "1". The value corresponding to this key is a hash with keys and values corresponding to the attributes of the reminder. Though these attributes are stored as strings, some actually represent non-string objects. How is this possible?

Consider the entry `2019-12-23` for `@s`. To *etm* this is a pendulum date object. When *etm* stores this record, *TinyDB* recognizes that this attribute is a pendulum date object and encodes/serializes it as the string `"{D}:20191223"`. When *etm* retrieves this record from storage, *TinyDB* recognizes from the `{D}` that it is to be decoded and returned as a pendulum date object. All this is completely transparent - *etm* gives a date object to *TinyDB* which stores it as a string and when *etm* wants it back, *TinyDB* deserializes it and returns it as a date object.

As another example, When the reminder is created by *etm* the `created` timestamp is handed to *TinyDB* as an aware pendulum datetime object with US/Eastern as the timezone. *TinyDB* recognizes this and, because it is an aware datetime, first converts it to Universal time and then encodes/serializes it as `"{T}:20191221T1526A"`. The `{T}` indicates that it is a datetime object and the appended `A` indicates that it is aware and thus has been converted to Universal time. When *etm* retrieves this record, *TinyDB* recognizes from the `{T}` and the `A` that this is an aware datetime object, decodes it as an aware datetime object and, because it is aware, converts it from Universal time to whatever the current local timezone happens to be before returning it. Had this been a naive datetime, an `N` would have been appended to the serialization and no conversion would have been done either way.

These **date** and **datetime** serializations are extensions of *TinyDB* provided by *etm*. Three further extensions are also provided: **interval** for *pendulum duration* objects using the tag `{I}`, **weekday** for  *dateutil* weekday objects using the tag `{W}` and **mask** using the tag `{M}` for encoding/serializing *etm* strings in a masked or obfuscated manner.

[↺ contents](#contents)
