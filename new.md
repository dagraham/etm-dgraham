# What's planned for the next etm
**January 27, 2018**

# Goals

- Simplify code. Refactor, document code and add doc tests - make the code more easilty maintainable. See [Item Types](#item-types), [Dates and Date Times](#dates-and-date-times) and [Jobs](#jobs). 

- Speed up performance. Make use of a text-based document store called *TinyDB* that is designed for quick insertions, modifications and retrievals. Make use of stored unique identifiers, to limit view updates to the item actually changed. See [Storage](#storage).

- Simplify data entry. Provide "just in time" information when creating or editing data entries. See [Work Flow](#work-flow). 

- Provide a simpler, terminal-based GUI using *urwid* along with a CLI that allows creating items and reports from the command line. From what I understand, *urwid* apps can be run in a terminal emulator under Android.

# Data

## Item Types

Six item types are used: `*`, `-`, `%`, `$`, `?`  and `!`.

### `*`: event

- The `@s` entry is required and is interpreted as the starting date or datetime of the event. If the event has an `@e` entry it is interpreted as the extent or duration of the event and the end of the event is then given implicitly by starting datetime plus extent.
- The old `^`, *occasion*,  item type is eliminated. The functionality is replaced by using a *date* entry rather than a *datetime* in an event. See  [Dates and Date Times](#dates-and-date-times).

### `-`: task

- The optional `@s` entry records the datetime at which the task is due or should be finished. Tasks with an `@s` entry are regarded as pastdue after this datetime. Tasks without an `@s` entry are to be completed when possible and are regarded as *next* items in the *Getting Things Done* terminology. An entry for `@e` can be given with or without an `@s` entry and is interpreted as the estimated time required to complete the task.
- The old `+`, *task group*, item type is eliminated. The functionality is replaced by the ability to add job entries, `@j`, to any task. See [Jobs](#jobs) below.
- The old `%`, *delegated*, item type is eliminated. The functionality is replaced by using an `@u`, *user*, entry to indicate that the task has been delegated to a specified user. When displaying delegated tasks, the user followed by a colon is prepended to the task summary.
- The old `@c`, *context*, for tasks has been merged into *location*, `@l`. 
- The `@c` entry is now used to denote the *calendar* to which the item belongs. I use calendars named `dag` (me), `erp` (wife) and `shared`. My default is to display `dag` and `shared` and to assign `dag` to items without an `@c` entry. 
- Display characters for tasks and jobs including (delegated) ones with `@u` entries:

    - `x`: finished task or job
    - `-`: unfinished task or job without unfinished prerequisites
    - `+`: job with unfinished prerequisites

### `%`: journal entry

This is equivalent to the old *note* item type. 

### `$`: action

  - In addition to the old *action* item type, it is now possible to record timer information relating to existing events, tasks and journal entries without creating new actions that duplicate the original item information.
  - In *all* cases - events, tasks, journal entries as well as in actions themselves - timer information is recorded using the `@m`, *moment*, entry. The format is `@m datetime started, timeperiod active, datetime finished`. The timeperiod that the timer was inactive/paused is given implicitly by `finished` minus `started` minus `active`. 
  - Items can have multiple `@m` entries. 
  - Each `@m` entry is displayed in the *Done* view on the day of `datetime finished` using the display character `$`, the item summary, the time of `datetime finished` and the `timeperiod active`.
  - Items that contain `@m` entries, are also displayed in the normal ways for the type of the item. 
  - Displaying the details either for an `$` item in *Done* or for an item with `@m` entries in another view, will show the details for the item itself and thus all of its `@m` entries.
  - It is **strongly recommended** that items containing `@m` entries should have `@i`, *index*, entries as well since accounting reports which aggregate time expenditures are based on the index entries. 
  - An etm *timer* can be used to record an `@m` entry in a selected item or a newly created action:

      - Begin:
          - Either select an item (event, task, journal or existing action) to which the `@m` entry should be added. 
          - Or create a new item with the action type character `$` and at least a summary for the new action. 
      - Start the timer.
      - Pause/resume the timer as often as desired.
      - Finish the timer to record the time spent. The `@m` entry will contain:
          - the moment at which the timer was first started
          - the accumulated time period during which the timer was active
          - the moment at which the timer was stopped
      - Choose whether or not to edit the modified item.
      - Note: One or more timers can be active at the same time but only one can be running - the others will automatically be paused.

  - When moments are added to task jobs, `&m` is used in the `@j` entry for the job instead of `@m` in the task itself.

### `?`: someday

Unchanged.

### `!`: inbox

Unchanged but for the change in the type character from `$` to `!`.

### Defaults

The old *defaults* item type, `=`, is eliminated. Its functionality is replaced by the `@x`, *extract*, entry which is used to specify a key for options to be extracted from the etm configuration settings. E.g., suppose your configuration setting has the following entry for `extractions`:

        extractions = {
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

would be equivalent to entering

      * Conflict and Cooperation @s 1/25/2018 9:35am @e 1h15m @a 10m, 3m: d 
        @l Math-Physics Bldg @i Work:Teaching

The `@e`, `@a`, `@l` and `@i` entries from `class` have become the defaults for the event but the default for `@l` has been overridden by the explicit entry. 

## Storage

- All etm data is stored in a single, *json* file using the python data store *TinyDB*. This is a plain text file that is human-readable, but not human-editable - not easily anyway.  It can be backed up and/or queried using external tools as well as etm itself. 
- Two timestamps are automatically created for each item in the data store, one corresponding to the moment (microsecond) the item was created and the other to the moment the item was last modified. A new *history* view in etm  displays all items and allows sorting by either timestamp. The default is to show oldest first for created timestamps and newest first for last modified timestamps. The creation timestamp is used as the unique identifier for the item in the data store. 
- The heirarchial organization that was provided by file paths is provided by the *index* entry, `@i`, which takes a colon delimited string. E.g., the entry `@i plant:tree:oak` would store the item in the *index* view under:
      - plant
          - tree
              - oak

    The default for `@i` is *None*. Note that `@i` replaces the functionality of  the old `@k`, *keyword*.

    *Action accounting reports are based on the index entries of the items*.

- The organization that was provided by calendars is provided by the *calendar* entry, `@c`. A default value for calendar specified in preferences is assigned to an item when an explicit value is not provided. 

## Dates and Date Times

- The time zone entry, `@z`, is eliminated. 

- Dates (naive) and datetimes (both naive and aware) are suppored. 

- Fuzzy parsing of entries is suppored.

- The format for the `@s` entry is `date [time][, TimeZone|float]`. In the following entries for `@s` suppose that it is currently Wed, Jan 4, 2018 and that the local timezone is US/Eastern.

    - Naive date, e.g., `@s fri`.  Interpreted as `Fri, Jan 5, 2018`. *Without a time*, this schedules an all-day, floating (naive) item for the specified date in whatever happens to be the local timezone.

    - Aware date-time, e.g, `@s fri 2p`. Interpreted as `Fri, Jan 5, 2018 2pm EST`. *With a time specified*, this schedules an item starting at the specified date-time in the current timezone (US/Eastern).

    - Aware date-time, e.g., `@s fri 2p, US/Pacific`. *With the timezone specified*, this is interpreted as `Fri, Jan 5 2018 2pm PST`. 

    - Naive date-time, e.g., `@s fri 2p, float`. *With float specified*, this is interpreted as `Fri, Jan 5, 2018 2pm` in whatever happens to be the local time zone.

    The assumption here is that when a user enters a date, a date is what the user wants. When both a date and time are given, what the user wants is a datetime and, most probably, one based on the local timezone. Less probably, one based on a different timezone and that requires the additon of the comma and the timezone. Still less probably, one that floats and this requires the addition of the comma and `float`.

- When an item with an aware `@s` entry repeats, the hour of the repetition instance *ignores* daylight savings time. E.g., in the following all repetitions are at 2pm even though the first two are EST and the third is EDT.

            repetition rule:
                RRULE:FREQ=MONTHLY
                DTSTART:Fri Jan 26 2018 2:00PM EST
            The first 3 repetitions on or after DTSTART:
                Fri Jan 26 2018 2:00PM
                Mon Feb 26 2018 2:00PM
                Mon Mar 26 2018 2:00PM
            All times: America/New_York

- Storage: 

	- Special storage classes have been added to etm's instance of *TinyDB* for both date and datetime storage. *Pendulum* Date and datetime objects used by etm are automatically encoded (serialized) as strings when stored in *TinyDB* and then automatically decoded as date and datetime objects when retrieved by etm. 
	- Preserving the *naive* or *aware* state of the object is accomplished by appending either an *N* or an *A* to the serialized string. 
	- Aware datetimes are converted to UTC when encoded and are converted to the local time when decoded. 
	- Naive dates and datetimes require no conversion either way. 

- Display:

    - Naive dates are displayed without conversion and without a starting time. 
    - Naive datetimes are displayed without conversion.
    - Aware datetimes are converted to the current local timezone. E.g., in the US/Eastern timezone, `fri 2p` would display as starting at 2pm on Jan 5 if the computer is still in the Eastern timezone but would display as starting at 11am if the computer had been moved to the Pacific timezone. Similarly, `fri 2p, US/Pacific` would display as starting at 5pm if the computer were in the Eastern timezone.
    - Datetimes are rounded to the nearest minute for display.

## Jobs

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

		`job A` has no prerequisites but is a prerequisite for `job B` which, in turn, is a prerequisite for `job C`. 

	- Manually assigned.  Job prequisites can also be assigned manually using entries for `&i` (id) and `&p`, (comma separated list of ids of immediate prequisites). E.g., with

					- manually assigned
						@j job a &i a
						@j job b &i b
						@j job c &i 3 &p a, b

		Neither `job a` nor `job b` have any prerequisites but `job a` and `job b` are both prerequistes for `job c`. Note that the order in which the jobs are listed is ignored in this case. 

- Tasks with jobs are displayed by job using a combination of the task and job summaries with a type character indicating the status of the job. E.g., 

          x manually assigned [1/1/1]: job a
          - manually assigned [1/1/1]: job b
          + manually assigned [1/1/1]: job c

	would indicate that `job a` is *finished*, `job b` is *available* (has no unfinished prerequistites) and that `job c` is *waiting* (has one or more unfinished prerequisties). The status indicator in square brackets indicates the numbers of finished, active and waiting jobs, respectively.

# Views

View hotkeys: a)genda, b)usy, d)one, c)reated, m)odified, i)ndex, n)ext, q)uery. s)omeday and t)ags. In all views, l)evel prompts for the outline expansion level.

## Weekly

### Agenda

- Scheduled items, grouped and sorted by week and day

	 ASCII art is used in the following to suggest the appearance of the view in the *urwid* GUI.

        +------------------------- top bar --------------------------+
        |Agenda - Week 3: Jan 15 - 21, 2018                   F1:help|
        +------------------------------------------------------------+
        |Mon Jan 15                                                  |
        |  ^ Martin Luther King Day                                  |
        |  * Lunch with Joe                            12:30pm-1:30pm|
        |  - Revise 1st quarter schedule                      3pm    |
        |Thu Jan 18 - Today                                          |
        |  < Revise 1st quarter schedule                       3d    |
        |  > Duke vs Pitt                                      2d    |
        |  * Conference call                             11am-11:30am|
        |Sat Jan 20                                                  |
        |  * Duke vs Pitt                                  4pm-6pm   |
        |  * Dinner                                        7pm-9pm   |
        |                                                            |
        +------------------------ status bar ------------------------+
        | 8:49am Thu Jan 18                                10:30am+1 | 
        +------------------------------------------------------------+

- The top title bar shows the selected week.
- The bottom status bar shows current time, the next alarm and the number of remaining alarms for the current date.
- The main panel shows scheduled items grouped and sorted by date and time.
- Weeks are displayed sequentially. If there is nothing to display for the week, then the main panel of the display would show "Nothing scheduled". E.g, 

        Week 2: Jan 8 - 14, 2018                            F1:Help
          Nothing scheduled

    For the current week, the display would show "Nothing scheduled" under the current date. E.g.,

        Week 3: Jan 15 - 21, 2018                           F1:Help
        - Thu Jan 18 - Today
          Nothing scheduled

- Starting from the top, the display for a day includes the following:

    - All day events (occasions), if any, using the display character `^` 
      instead of the event type character `*`
    - For the current date (today) only:

        - Inbox entries, if any
        - Pastdue tasks, if any, with the number of days that have passed since the task was due using the display character `<`. 
        - Beginning soon notices, if any, with the number of days remaining until the starting date of the item using the display character `>`.

        Note that the items included for the current date are those from the old *agenda* view.

    - Scheduled events, journal entries, actions and unfinished tasks sorted by `@s` which is displayed in the 2nd column. For events and tasks with *extent*, the ending time is also displayed. 
    - Unfinished all day tasks, if any
    - All day journal entries, if any

- *Agenda* is synchronized with *Done* and *Busy* so that switching from one of these views to another always displays the same week. 

### Busy

- Hours in the day that are partially or wholly "busy" are marked with `#`.
- Hours in which a conflict occurs are marked with `+++`. 

        +----------------------------------------------------------+
        |Busy - Week 4: Jan 22 - 28, 2018                   F1:help|
        +----------------------------------------------------------+
        |   Hr     Mo     Tu     We     Th     Fr     Sa     Su    |
        |  ----+-------------------------------------------------  |
        |  12a |   .      .      .      .      .      .      .     |
        |      |   .      .      .      .      .      .      .     |
        |      |   .      .      .      .      .      .      .     |
        |      |   .      .      .      .      .      .      .     |
        |      |   .      .      .      .      .      .      .     |
        |      |   .      .      .      .      .      .      .     |
        |   6a |   .      .      .      .      .      .      .     |
        |      |   .      .      .      .      .      .      .     |
        |      |   #      .      #      .      #      #      .     |
        |      |   #      .      #      .      #      #      .     |
        |      |   .      #      .      .      .      #      .     |
        |      |   .      #      .      #      .      #      #     |
        |  12p |   #      .      .      #      .      #      #     |
        |      |   #      .      .     +++     .      #      #     |
        |      |   .      .      .      #      .      .      #     |
        |      |   .      .      .      .      .      .      #     |
        |      |   #      .      .      .      .      .      .     |
        |      |   #      .      .      .      .      .      .     |
        |   6p |   .      .      #      .      .      .      .     |
        |      |   #      .      #      .      .      .      .     |
        |      |   #      .      #      .      .      .      .     |
        |      |   #      .      .      .      .      .      .     |
        |      |   .      .      .      .      .      .      .     |
        |      |   .      .      .      .      .      .      .     |
        +----------------------------------------------------------+
        | 8:49am Thu Jan 18                              10:30am+1 | 
        +----------------------------------------------------------+

- *Busy* is synchronized with *Agenda* and *Done* so that switching from one of these views to another always displays the same week.

### Done

- Actions and finished tasks grouped and sorted by week and day using the finished datetime
- Actions are displayed with type character `$`, the item summary,  the time finished and the active time period. Finished tasks are displayed with type character `x`, the summary and time finished. E.g., here is a record of time spent working on a task and then marking the task finished:

        +------------------------- top bar --------------------------+
        |Done - Week 3: Jan 15 - 21, 2018                     F1:help|
        +------------------------------------------------------------+
        |Mon Jan 15                                                  |
        |  $ report summary                             4:29pm - 47m |
        |  x report summary                                4:30pm    | 

- *Done* is synchronized with *Agenda* and *Busy* so that switching from one of these views to another always displays the same week.

## Next

- Unfinished tasks and jobs that are undated (without `@s` entries) grouped and sorted by *location* and then *priority*

- Finished tasks and jobs are removed from this view, but are added to *Done* using the completion datetime.

## Someday

Someday items grouped and sorted by the last modified datetime

## Index

- All items, grouped and sorted by their *index* entries
- Items without `@i` entries are listed last under *None*.

## History

### Created

All items, sorted by the datetime created and grouped by year and month.

### Modified

All items, sorted by the datetime last modified and grouped by year and month.

## Tags

Tagged items grouped and sorted by tag.

## Query

Analagous to the old custom view. Used to issue queries against the data store and display the results. 

## Monthly 

        +----------------------------------------------------------+
        | August 2017                                              |
        +----------------------------------------------------------+
        |                                                          |
        |   Wk     Mo     Tu     We     Th     Fr     Su     Su    |
        |  ----+-------------------------------------------------  |
        |      |                                                   |
        |   31 |   31      1      2      3      4      5      6    |
        |      |                                                   |
        |   32 |    7      8      9     10     11     12     13    |
        |      |                                                   |
        |   33 |   14     15     16     17     18     19     20    |
        |      |                                                   |
        |   34 |   21     22     23     24     25     26     27    |
        |      |                                                   |
        |   35 |   28    [29]    30     31      1      2      3    |
        |      |                                                   |
        |   36 |    4      5      6      7      8      9     10    |
        |      |                                                   |
        +------+---------------------------------------------------+
        | Tue Aug 29 2917                                          |
        |   Nothing scheduled                                      |
        |                                                          |
        |                                                          |
        |                                                          |
        |                                                          |
        |                                                          |
        +----------------------------------------------------------+
        | 8:49am Thu Jan 18                              10:30am+1 | 
        +----------------------------------------------------------+


# Work Flow

## Editing an existing item

ASCII art is used in the following to suggest the appearance of the view in the *urwid* GUI.

- Pressing Return with an item selected shows details:

        +------------------------- top bar --------------------------+
        |details                                              F1:help|
        +------------------------------------------------------------+
        |- task group @s 2016-06-28 00:00 @b 7 @a 2d: m @a 2d: v     |
        |@r m &i 1                                                   |
        |@j Job A &s 4w &b 2 &i 1 &a 2d: m &a 2d: v                  |
        |@j Job B &s 2w &b 3 &i 2 &p 1 &a 2d: m &a 2d: v             |
        |@j Job C &s 0m &b 7 &i 3 &p 2 &a 2d: m &a 2d: v             |


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

## Creating a new item

- When creating a new item, the process is the same but for the fact that the initial entry will be empty. 

        +------------------------- top bar --------------------------+
        |editing: new item                                    F1:help|
        +------------------------------------------------------------+
        |type character for the new item?                            |
        |> _                                                         |
        | ---------------------------------------------------------- |
        |item type characters:                                       |
        |  *: event       -: task          $: action                 |
        |  %: journal     ?: someday       !: inbox                  |

- Editing takes place in the line beginning with the `>` prompt. The current cursor position is shown by the underscore `_`.

- Closing before any changes have been made will cancel the operation and no new item will be created. 

- The main panel reflects any changes as they occur:

        +------------------------- top bar --------------------------+
        |editing: unsaved changes                             F1:help|
        +------------------------------------------------------------+
        |summary for the event?                                      |
        |> * my ev_                                                  |
        | ---------------------------------------------------------- |
        |Enter the summary for the event followed, optionally, by    |
        |@key and value pairs.                                       |

- As editing progresses, the display changes to show information relevant to the current entry. Here are some illustrative screens.

  - Summary entered and an initial `@` but without the key:

        +------------------------------------------------------------+
        |@key?                                                       |
        |> * my event @_                                             |
        | ---------------------------------------------------------- |
        |Available @keys:                                            |
        |  Required: @s                                              |
        |  Allowed: @c, @d, @e, @g, @i, @l, @m, @t, @v               |
        |  Requires @s: @a, @b, @r                                   |
        |  Requires @r: @+, @-                                       |

  - With `@s fri` entered but without a time

        +------------------------------------------------------------+
        |@s: starting date or datetime?                              |
        |> * my event @s fri_                                        |
        | ---------------------------------------------------------- |
        |currently: Fri Jan 19 2018                                  |
        |Without a time, this schedules an all-day, floating item    |
        |for the specified date in whatever happens to be the local  |
        |timezone.                                                   |

  - With `@s fri 2p` entered

        +------------------------------------------------------------+
        |@s: starting date or datetime?                              |
        |> * my event @s fri 2p_                                     |
        | ---------------------------------------------------------- |
        |currently: Fri Jan 19 2018 2:00PM EST                       |
        |The datetime will be interpreted as an aware datetime in    |
        |the current timezone. Append, e.g., ", US/Pacific" to       |
        |specify a particular timezone or ", float" to specify a     |
        |floating item in whatever happens to be the local timezone. |

  - Starting an entry for `@r`:

        +------------------------------------------------------------+
        |@r: repetition frequency?                                   |
        |> * my event @s fri 2p @r_                                  |
        | ---------------------------------------------------------- |
        |A character from: (y)early, (m)onthly, (w)eekly, (d)aily    |
        |   (h)ourly, mi(n)utely                                     |


  - With `@r m` entered:

        +------------------------------------------------------------+
        |@r: repetition rule?                                        |
        |> * my event @s fri 2p @r m_                                |
        | ---------------------------------------------------------- |
        |currently:                                                  |
        |    RRULE:FREQ=MONTHLY                                      |
        |    DTSTART:Fri Jan 19 2018 2:00PM EST                      |
        |The first 3 repetitions on or after DTSTART:                | 
        |    Fri Jan 19 2018 2:00PM                                  |
        |    Mon Feb 19 2018 2:00PM                                  |
        |    Mon Mar 19 2018 2:00PM                                  |
        |All times: America/New_York                                 |
        |                                                            |
        |Possible options: &c (count), &E (Easter), &h (hour),       |
        |   &i (interval), &m (monthday), &M (month), &n (minute),   |
        |   &s (set position), &u (until), &w (weekday)              |

  - With `@r m &w` entered:

        +------------------------------------------------------------+
        |&w: weekdays?                                               |
        |> * my event @s fri 2p @r m &w_                             |
        | ---------------------------------------------------------- |
        |A comma separated list of English weekday abbreviations     |
        |from SU, MO, TU, WE, TH, FR, SA, SU. Prepend an integer     |
        |to specify a particular weekday in the month. E.g., 3WE for |
        |the 3rd Wednesay or -1FR for the last Friday in the month.  | 

  - With `@r m &w -2FR` entered:

        +------------------------------------------------------------+
        |@r: repetition rule?                                        |
        |> * my event @s fri 2p @r m &w -2fr                         |
        | ---------------------------------------------------------- |
        |currently:                                                  |
        |    RRULE:FREQ=MONTHLY;BYWEEKDAY=-2FR                       |
        |    DTSTART:Fri Jan 19 2018 2:00PM EST                      |
        |The first 3 repetitions on or after DTSTART:                | 
        |    Fri Jan 19 2018 2:00PM                                  |
        |    Fri Feb 16 2018 2:00PM                                  |
        |    Fri Mar 23 2018 2:00PM                                  |
        |All times: America/New_York                                 |
