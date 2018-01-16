# Data

## Item Types

Six item types are used: `*`, `-`, `$`, `%`, `?`  and `!`.

### `*`: event

- The `@s` entry is required and is interpreted as the starting date or datetime of the event. If the event has an `@e` entry it is interpreted as the extent or duration of the event and the end of the event is then given implicitly by starting datetime plus extent.

- The old `^`, *occasion*,  item type is eliminated. The functionality is replaced by using a *date* entry rather than a *datetime* in an event. See *Dates and Date Times* below.

- Stored as an *event* when exporting to *ical*.

### `-`: task

- The optional `@s` entry records the datetime at which the task is due or should be finished. Tasks with an `@s` entry are regarded as pastdue after this datetime. Tasks without an `@s` entry are to be completed when possible and are regarded as *next* items in the *Getting Things Done* method. An entry for `@e` can be given with or without an `@s` entry and is interpreted as the estimated time required to complete the task.

- The old `+`, *task group*, item type is eliminated. The functionality is replaced by the ability to add job entries, `@j`, to any task.

- The old `%`, *delegated*, item type is eliminated. 

- The old `@c`, *context*, for tasks has been merged into *location*, `@l`. The `@c` entry is now used to denote the *calendar* to which the item belongs.

- Stored as a *todo* when exporting to *ical*.

### `$`: action

- An entry for `@m` is required along with entries for `@s` and `@f`.

- The `@s` entry is interpreted as the aware datetime at which the action was *started*. 

- The `@f` entry is interpreted as the aware datetime at which the action was *completed*. 

- The `@m`, *memo*, entry in an action is interpreted as the time period actively spent working on the action. 

- An etm *timer* can be used to record an action entry:

    - Select the item (task, event, ...) to which the action is to be applied.

    - Press the start key to start the timer.

    - Press the pause/restart key as often as desired.

    - Press the finish key to finish and record the action entry.

      - The `@s` entry will record the moment at which the timer was first started.

      - The `@f` entry will record the moment at which the timer was finished.

      - The `@m` entry will record the accumulated time period during which the timer was active. Note that the finish time minus the start time minus active time implicitly gives the time period during which the timer was paused.

      - The summary, `@c`, `@i`, `@l` and `@t`  entries for the action will be those of the selected item. 

      - The action will be displayed for possible editing.

- One or more timers can be active at the same time but only one can be running - the rest will be paused.

- Actions cannot repeat, i.e., cannot have `@r` entries.

- Stored as a *journal* entry when exporting to *ical*.

### `%`: journal entry

- This is equivalent to the old *note* item type. 

- Journal items cannot repeat, i.e., cannot have `@r` entries.

- Stored as a *journal* entry when exporting to *ical*.

### `?`: someday maybe

- Unchanged. 

- Someday items cannot repeat, i.e., cannot have `@r` entries. Datetime related entries such as `@s`, `@a` and `@b` are ignored.

- Stored as a *journal* entry when exporting to *ical*.

### `!`: inbox

- Unchanged but for the change in the type character from `$` to `!`.

- All entries in inbox items are ignored save for the item type, summary and the created and last modified timestamps. 

- Stored as a *journal* entry when exporting to *ical*.

## Storage

- All etm data is stored in a single, *json* file using the python data store *TinyDB*. This is a plain text file that is human-readable, but not human-editable.  It can be backed up and/or queried using external tools as well as etm itself. 

- Two timestamps are automatically created for each item in the data store, one corresponding to the moment (microsecond) the item was created and the other to the moment the item was last modified. A new *history* view in etm  displays all items and allows sorting by either timestamp. The default is to show oldest first for created timestamps and newest first for last modified timestamps. The creation timestamp is used as the unique identifier for the item in the data store. 

- The heirarchial organization that was provided by file paths is provided by the *index* entry, `@i`, which takes a colon delimited string. E.g., the entry `@i plant:tree:oak` would store the item in the *index* view under:
      - plant
          - tree
              - oak

    The default for `@i` is *None*. Note that `@i` replaces the functionality of  the old `@k`, *keyword*.

- The organization that was provided by calendars is provided by the *calendar* entry, `@c`. A default value for calendar specified in preferences is assigned to an item when an explicit value is not provided. 

## Dates and Date Times

- The time zone entry, `@z`, is eliminated. 

- Dates (naive) and datetimes (both naive and aware) are suppored. 

- The format for the `@s` entry is `date [time][, TimeZone|float]`. In the following entries for `@s` suppose that it is currently Wed, Jan 4, 2018 and that the local timezone is US/Eastern.

    - Naive date, e.g., `@s fri`.  Interpreted as `Fri, Jan 5, 2018`. Without a time, this schedules an all-day, floating (naive) item for the specified date in whatever happens to be the local timezone.

    - Aware date-time, e.g, `@s fri 2p`. Interpreted as `Fri, Jan 5, 2018 2pm EST`. With a time, this schedules an item starting at the specified date-time in the current timezone (US/Eastern).

    - Aware date-time, e.g., `@s fri 2p, US/Pacific`. Interpreted as `Fri, Jan 5 2018 2pm PST`.

    - Naive date-time, e.g., `@s fri 2p, float`. Interpreted as `Fri, Jan 5, 1018 2pm` in whatever happens to be the local time zone.

- Storage: 

    - Special storage classes have been added to etm's instance of *TinyDB* for both date and datetime storage. *Pendulum* Date and datetime objects used by etm are automatically encoded (serialized) as strings when stored in *TinyDB* and then automatically decoded as date and datetime objects when retrieved by etm. Preserving the *naive* or *aware* state of the object is accomplished by appending either an *N* or an *A* to the serialized string. Aware datetimes are converted to UTC when encoded and are converted to the local time when decoded. Naive dates and datetimes require no conversion either way.

- Display:

    - Naive dates are displayed without conversion and without the midnight starting time. All-day events (occasions) go first in the daily display before all the datetime items and all-day tasks and journal entries go last.

    - Naive datetimes are displayed without conversion, i.e., are interpreted as local datetimes without conversion.

    - Aware datetimes are converted to the current local timezone. E.g., in the US/Eastern timezone, `fri 2p` would display as beginning at 2pm on Jan 5 if the computer is still in the Eastern timezone but would display as starting at 11am if the computer had been moved to the Pacific timezone. Similarly, `fri 2p, US/Pacific` would display as starting at 5pm if the computer were in the Eastern timezone.

    - Datetimes are rounded to the nearest minute for display.

## Jobs

- Tasks, both with and without `@s` entries can have component job entries, `@j`.  A task with jobs thus replaces the old task group.

- For tasks with an `@s` entry, jobs can have an `&s` entry to set the due date/datetime for the job. It can be entered as a timeperiod relative to  the starting datetime (+ before or - after) for the task or as date/datetime. However entered, the value of `&s` is stored as a relative timeperiod with zero minutes as the default.

- For tasks with an `@s` entry, jobs can also have `&a`, alert, and `&b` beginning soon notices. The entry for `&a` is given as a time period relative to `&s` (+ before or - after) and the entry for `&b` is a positive integer number of days before the starting date/time to begin displaying "beginning soon" notices. Entries for `@a` and `@b` in the task become the defaults for `&a` and `&b`, respectively.

- Automatically assigned Job prerequisites

    The default is to suppose that jobs must be completed sequentially in the order in which they are listed. E.g., with

        - automatically assigned
            @j job A
            @j job B
            @j job C

    `job A` has no prerequisites but is a prerequisite for `job B` which, in turn, is a prerequisite for `job C`. 

- Manually assigned prerequisites

    Alternatively, job prequisites can be assigned manually using entries for `&i` (id) and `&p`, (comma separated list of ids of immediate prequisites). E.g., with

        - manually assigned
          @j job a &i a
          @j job b &i b
          @j job c &i 3 &p a, b

    Neither `job a` nor `job b` has any prerequisites but both `job a` and `job b` are prerequistes for `job c`. Note that the order in which the jobs are listed is ignored in this case. 

- Tasks with jobs are displayed by job using a combination of the task and job summaries with a type character indicating the status of the job. E.g., 

          x manually assigned: job a
          - manually assigned: job b
          + manually assigned: job c

    would indicate that `job a` if finished, `job b` is available (has no unfinished prerequistites) and that `job c` is waiting (has unfinished prerequisties). 

# Views

## Day View

- Scheduled items are grouped by week.

- The top title bar shows selected week, e.g.,

        Week 2: Jan 8 - 14, 2018                            F1:Help

- The bottom status bar shows current time, next alarm and the number of remaining alarms:

        8:49am Thu Jan 11                                 10:30am+2

- The main panel shows scheduled items grouped by date, e.g., 

        - Mon Jan 8
          ...
        - Tue Jan 9
          ...
        - Wed Jan 10 - Yesterday
          ...
        - Thu Jan 11 - Today
          ...
        - Fri Jan 12 - Tomorrow
          ...
        - Sat Jan 13
          ...
        - Sun Jan 14
          ...
- Weeks are displayed sequentially. If there is nothing to display for the 
  week, then the main panel of the display would show "Nothing scheduled". 
  E.g, 

        Week 3: Jan 15 - 21, 2018                           F1:Help
          Nothing scheduled

  For the current week, the display would show "Nothing scheduled" under the 
  current date. E.g.,

        Week 2: Jan 8 - 14, 2018                            F1:Help
        - Thu Jan 11 - Today
          Nothing scheduled


- Starting from the top, the display for a day includes the following:

    - All day events (occasions), if any, using the display character `^` 
      instead of the event type character `*`

    - For the current date (today) only:

        - Inbox entries, if any

        - Pastdue tasks, if any, with the number of days that have passed since 
          the task was due

        - Beginning soon notices, if any, with the number of days remaining 
          until the starting date of the item.  These notices use the display 
          character `>` whatever the type character of the item containing the 
          `@b` entry.

        Note that the items included for the current date are those from the old *agenda* view.

    - Scheduled events, journal entries, actions and unfinished tasks sorted by `@s` which is displayed in the 2nd column. For events and tasks with *extent*, the ending time is also displayed. 

    - Unfinished all day tasks, if any

    - All day journal entries, if any

    - Tasks, dated or undated, that were finished on this date, if any


## Next View

- Unfinished tasks and jobs without `@s` entries grouped and sorted by *location* and then *priority*.

- While finished tasks and jobs are removed from this view, they are added to *Day View* using the completion datetime.

## Someday View

- Someday items grouped and sorted by the last modified datetime 

## Tag View

- Tagged items grouped and sorted by tag

## Index View

- All items, grouped and sorted by their *index* entries

## History View

- All items, grouped and sorted by the datetime created (oldest first) or the datetime last modified (newest first)

## Finished View

- Finished tasks grouped and sorted by the completed datetime, most recent first.

## Action View

- Actions grouped, sorted and with moment time aggregated by month and index. 

# Work Flow

## Editing an existing item

- Pressing Return with item selected shows details using the jinja2 template

        +-------------------------- top bar -------------------------+
        |Current Version                                      F1:Help|
        +------------------------------------------------------------+
        |- task group @s 2016-06-28 00:00 @b 7 @a 2d: m @a 2d: v     |
        |@r m &i 1                                                   |
        |@j Job A &s 4w &b 2 &i 1 &a 2d: m &a 2d: v                  |
        |@j Job B &s 2w &b 3 &i 2 &p 1 &a 2d: m &a 2d: v             |
        |@j Job C &s 0m &b 7 &i 3 &p 2 &a 2d: m &a 2d: v             |
        |                                                            |
        |                                                            |
        +------------------------ status bar ------------------------+
        |Ret:close  e)dit  d)elete  c)opy  r)eschedule  s)chedule new| 
        +------------------------------------------------------------+

    - `@g` entries appear as clickable links in the details 

    - For repeated items, show as many as 3 reps below the details with a clickable `< more >` button if applicable. Each click shows as many as 3 more repetitions.

- When edit, delete or copy is pressed and the item is repeating then pop-up

                +-------------------------------------------+
                |    Which instances?                       |
                |                                           |
                |    [] Earlier   [X] Selected   [] Later   | 
                +-------------------------------------------+ 

- When edit or copy is pressed, the details of the relevant item is displayed using the jinja2 template and ready for editing. Note that since copy creates a new item, it will be displayed as having unsaved changes.

- When the edited version is different than the saved version

        -------------------------- top bar -------------------------
        Unsaved Changes                                      F1:Help

        ------------------------ status bar ------------------------
                ^S:save  ^Q:save and close   ^U:undo changes

    - Save processes the item, updates the data store, displays the item using the jinja2 template and reopens it for editing. 

- When the editied version is the same as the saved version

        -------------------------- top bar -------------------------
        Saved Version                                        F1:Help

        ------------------------ status bar ------------------------
                             ˆQ:close    e)dit 

- When Return is pressed, the details view closes and the original view is restored with the original and possibly modified item selected.

## Creating a new item

- When creating a new item, the process is the same but for the fact that the initial *Current Version* display will, of course be empty. 

        +-------------------------- top bar -------------------------+
        |New item                                             F1:Help|
        +------------------------------------------------------------+
        |type character for new item?                                |
        |> _                                                         |
        | ---------------------------------------------------------- |
        |item type characters:                                       |
        |  *: event       -: task          $: action                 |
        |  %: journal     ?: someday       !: inbox                  |
        |                                                            |
        |                                                            |
        |                                                            |
        +------------------------ status bar ------------------------+
        |                         Esc:cancel                         |
        +------------------------------------------------------------+

- Once the new item has been modified, then the status bar changes to

        ------------------------ status bar ------------------------
                ^S:save  ^Q:save and close   ^U:undo changes

