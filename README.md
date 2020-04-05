<!-- ![event and task manager](https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etmlogo.png) -->
<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/etmlogo.png" alt="etm" title="event and task manager" />

* auto-gen TOC:
{:toc}

# [Overview](#overview)

## [Reminders](#overview)

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

* An event (**\***): have lunch with Ed [s]tarting next Tuesday at 12pm and [e]xtending for 90 minutes, i.e., lasting from 12pm until 1:30pm.

        * Lunch with Ed @s tue 12p @e 90m

* A record (**%**): a favorite Churchill quotation that you heard at 2pm today with the quote itself as the [d]escription.

        % Give me a pig - Churchill @s 2p @d Dogs look up at 
          you. Cats look down at you. Give me a pig - they 
          look you in the eye and treat you as an equal.

* A task (**-**): build a dog house, with component [j]obs.

        - Build dog house @j pick up materials @j cut pieces 
          @j assemble @j sand @j paint

* Inbox (**!**): meet Alex for coffee Friday. This can be 
  changed to an event when the time is confirmed by 
  replacing the **!** with an **\*** and adding the time to `@s`.

        ! Coffee with Alex @s fri @e 1h

    This inbox entry will appear on the current day in *agenda view* until you make the changes.

* An appointment (event) for a dental exam and cleaning at 2pm on Feb 5 and then again [@+] at 9am on Sep 3.

        * dental exam and cleaning @s 2p feb 5 2019 @e 45m 
          @+ 9am Sep 3 2019

### text entry versus forms

* Text entry removes the need to hunt for and click in the relevant entry box and allows you to keep your fingers on the keyboard.
* Text entry supports the full flexibility of the superb Python *dateutil* package. Consider, for example, creating a reminder for Presidential election day which repeats every 4 years on the first Tuesday after a Monday in November (a monthday falling between 2 and 8). In *etm*, this event would be

        * Presidential election day @s nov 1 2020 @r y &i 4 &M 11 
          &m 2, 3, 4, 5, 6, 7, 8 &w tu

    Try this with a form based calendar application.

### unobtrusive and timely entry assistance

When you want to create a new reminder or edit an exiting one, *etm* opens an area at the bottom of the screen that is divided into two parts by a horizontal line. The lower part is the entry area where what you type appears. The upper part is the prompt/feedback area where *etm* responds to your typing. This response might take the form of providing a suggestion about alternatives, information about the type of input required or feedback about how your current entry is being interpreted. It is important to realize that none of this interferes with your typing - you can blaze away as quickly as you like or even paste complete entries and never glance at the prompt if you like. This is the **unobtrusive** part of the prompt/feedback process.  

<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/new.png" alt="new" title="new entry" />

#### just in time entry prompts and feedback

Let's create the election day reminder to illustrate the **timely** part of the process. Begin by pressing `N` to create a new reminder and notice that *etm* automatically prompts you for the item type character and suggests the alternatives.

        item type
        Choose a character from * (event), - (task), % (record)
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
        required: @s (start)
        available: @+ (include), @- (exclude), @a (alerts),
        @b (beginby), @c (calendar), @d (description),
        @e (extent), @g (goto), @i (index), @l (location),
        @m (mask), @n (attendee), @o (overdue),
        @r (repetition frequency), @s (start), @t (tag),
        @u (used time), @x (expansion), @z (timezone)
        ────────────────────────────────────────────────────────────
        * Presidential election day @_

You see that `@s` is required, so add the `s` and *etm* will prompt you for the value for the start option and describe the type of input required.

        start
        starting date or datetime

        ────────────────────────────────────────────────────────────
        * Presidential election day @s_

As you enter the datetime, *etm* will display its interpretation of your entry.

        start
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

These are the first 5 repetitions on or after Nov 1 2020. Notice that the start value of Nov 1 2020 is not one of the repetitions since it doesn't satisfy the requirements. These appear correct, so press ^S to save the reminder.


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
* The prompts provide "just in time" information relevant to the entry you are typing and need only be consulted if you are uncertain about your entry. With a little experience, most reminders can be completed without a glance at the prompt.


#### Fuzzy parsing of datetimes

Whenever *etm* expects a datetime entry as, for example, when you are entering an `@s` starting datetime, it applies fuzzy parsing to your entry.  Suppose it is Dec 17 2019, your computer is in the Eastern timezone and you have just entered `@s` for your lunch event

        start
        starting date or datetime

        ────────────────────────────────────────────────────────────
        * lunch @s_

If you enter `1`, *etm* will interpret it as 1am on the current date in the local timezone.

        start
        Tue Dec 17 2019 1:00am EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1_

Adding `p` changes the interpretation to 1pm.

        start
        Tue Dec 17 2019 1:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p_

Now start adding 'fri' by appending an 'f'.

        start
        '1p f' is incomplete or invalid

        ────────────────────────────────────────────────────────────
        * lunch @s 1p f_

and *etm* will complain that the entry is now either incomplete or invalid. Add the remaining 'ri'.

        start
        Fri Dec 20 2019 1:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p fri_

and *etm* understands that you want the coming Friday, Dec 20. Now suppose that you will be in California on Friday and you want Pacific, not Eastern time. Then add an entry for `@z`.

        start
        local datetime: Fri Dec 20 2019 4:00pm EST

        ────────────────────────────────────────────────────────────
        * lunch @s 1p fri_ @z US/Pacific

Note that `local datetime` is now prepended to the result which is still displayed in the local timezone, since that is the location of your computer, but the time has changed to `4:00pm EST` which, of course, is the same time as `1:00pm PST`. *etm* **always** displays times in the current local time zone. When you save this item, the time will be converted to universal time and the `@z US/Pacific` will be deleted - once the time has been converted, the original timezone is no longer relevant.

What if you had entered the 'fri' first?

        start
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

        start
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


#### tab completion

Some optional attributes that can be used in reminders can be tedious to enter either because they are lengthy or because they are used often and typographical errors would introduce inconsistencies. These attributes include the following: 

* *@g*: goto url or filepath. In the latter case, the system default application is used to open the filepath, e.g., on my macbook the system default for files ending in `.py` is to open them in MacVim. In the former case, the url will be opened in the default browser. In either case, a typo would likely render the link useless.
* *@l*: location/context. In the *do next* view, `location` is used to organize undated tasks. Using `@l errands` in one task and `@l erands` in another would cause these tasks to be grouped separately.
* *@i*: index - colon delimited string. In both the *index* and the *used time* views, the index entry is used to group and aggregate entries. Using `@i jsmith:project a` in one entry and `@i jsmth:project a` in another would cause these these entries to be grouped and aggregated separately. 
* *@n*: attendee. string using "[name:] address" format. If "address" begins with exactly 10 digits followed by an "@" it is treated as a mobile phone number. Otherwise it is treated as an email address. The optional "name:" can be used to facilitate autocompletion. Attendee entries are used in both email and text alerts. 

Other tracked attributes include *@c* (calendar) and *@t* (tag).

For these attributes, etm keeps a record of each usage. I.e., for each reminder in your *etm* database, if the reminder includes a tracked attribute that has not already been included in the list of completions, then that attribute will be added. E.g., if you create an reminder containing

        @n joe: jsmith457@gmail.com

  and '@n joe: jsmith457@gmail.com' is not already in the list of completions, then it would be added.

When you next create a reminder and enter @n, *etm* will pop up a sorted list of every item in the completion list that begins with @n. You can use the up and down cursor keys to move through this list or you can continue typing to limit the possible completions, e.g., after entering '@n joe' only those completions that start with '@n joe' would still be displayed. When you have selected the completion you want, press the space bar to insert the completion in your entry.


## [Views](#overview)


_etm_ has several ways of viewing entries. These are listed below by the shortcut key used to activate the view. E.g., pressing `a` activates _Agenda_ view.

  * a: Agenda: dated unfinished tasks and other reminders by year-week and week day 
  * b: Busy: a graphical illustration of busy and conflicted times by year-week
  * c: Completed: finished tasks and jobs and used time entries by year-week and week day
  * d: Do Next: undated tasks grouped by location
  * f: Forthcoming: unfinished dated tasks and other dated reminders by next occurrence 
  * h: History: all items by the latter of the modified or created datetimes in descending order, i.e., most recent first
  * i: Index: events, tasks and inbox items grouped hierarchically by index entry
  * q: Query: items matching a user specified query. Enter ? for query usage.
  * r: Records: records grouped hierarchically by index entry
  * t: Tags: all items with @t tag entries grouped by tag
  * u: Used Time: all items with @u used time entries grouped by month and hierarchically by index 
  * U: Used Time Summary: used time aggregates grouped by month and hierarchically by index
  * x: Used Time Expanded: similar to Used Time but with @d entries displayed
  * y: Yearly Planning Calendar: compact monthly calendar by half year. 

### [Weekly Views](#overview)

The _weekly_ agenda, busy and completed views display one week at a time and are *synchronized* so that all three views always display the same week. Left or right cursor keys go backward or forward a week at a time and the pressing the space bar jumps to the week containing the current day. You can also press "j" and enter a date to jump to the week containing the date.

In both agenda and completed views, only days with scheduled reminders are listed. If nothing is scheduled for the entire week, then "Nothing scheduled" is displayed.

The normal agenda listing for a week day:

* all day events (events with dates as `@s` entries)
* datetime items (reminders with datetimes as `@s` entries) by time
* all day tasks (tasks with dates as `@s` entries)
* all day records (records with dates as `@s` entries)

And, on the current day only: 

* inbox items
* *<* pastdue warnings in descending order of the number of days past due
* *>* beginby warnings in ascending order of the number of days remaining


### [Used Time Views](#overview)

The *used time* and *used time summary* views are bound to `u` and `U` respectively. They report `@u` (used time) entries in your reminders grouped by year-month and then heirarchially by `@i` entries. I have a file of reminders with `@i` and `@u` entries such as

		* Modi ut sit sed amet sit @s 2019-11-11 10:00am @e
		   1h30m 
		@u 58m: 2019-11-11 10:58am @u 34m: 2019-11-11 10:34am 
		@i client A/project a1/correspondence 
		@d Aliquam non sed aliquam eius tempora quisquam dolorem.
		Neque quiquia labore tempora magnam. Quiquia tempora
		porro est ut. Ut tempora sed non ut eius neque porro.
		Sed quaerat consectetur dolor sit. 

and the *used time view* for November begins with

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

The *used time **expanded** view* is like the *used time* view but when a reminder has an `@d` entry, the contents of that field are also displayed wrapped and indented under the reminder. This view for November begins with

		November 2019
		  client A
			project a1
			  correspondence
				* Modi ut sit sed amet sit: 1.6h Nov 11
				  Aliquam non sed aliquam eius tempora
				  quisquam dolorem. Neque quiquia labore
				  tempora magnam. Quiquia tempora porro est
				  ut. Ut tempora sed non ut eius neque porro.
				  Sed quaerat consectetur dolor sit.
				% Amet modi neque eius adipisci: 2.7h Nov 27
				  Adipisci voluptatem labore amet neque neque
				  numquam. Voluptatem dolor dolorem sed sit.
				  Tempora labore ut ut labore tempora. Sit
				  ipsum dolorem aliquam aliquam voluptatem non
				  labore. Est quisquam etincidunt quiquia est
				  ipsum adipisci. Est quiquia velit sed sed
				  quisquam quisquam porro.
			  research
				* Quisquam quiquia velit non: 2.0h Nov 19
				  Labore ipsum non consectetur amet quiquia
				  sit porro. Quisquam amet ut sit etincidunt.
				  Quiquia modi consectetur ipsum velit eius.
				  Est dolorem etincidunt porro. Modi dolorem
				  porro magnam est. Adipisci non quiquia
				  voluptatem porro consectetur. Quaerat neque
				  modi sed tempora sit adipisci consectetur.
				  Dolor non dolore ut quaerat ipsum labore.
			project a2
			  correspondence
				* Consectetur voluptatem dolorem: 1.0h Nov 6
				  Dolore quaerat est dolore tempora. Modi amet
				  voluptatem etincidunt numquam neque velit.
				  Ipsum neque amet dolor magnam consectetur
				  dolorem voluptatem. Neque amet etincidunt
				  quiquia neque dolorem numquam quiquia. Neque
				  etincidunt labore numquam neque modi.


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


This view omits the reminder lines and aggregates the used times heirarchially by index entry.

As with other dated views, the left and right cursor keys go backwards and forwards a month at a time and the space bar returns to the current month. Also, pressing `^C` copies the contents of the view to the system clipboard.

### [Query View](#overview)

In *query view* an entry line at the bottom of the screen is used to submit queries to your data store of reminders. For example, press `q` to open query view, enter

		search summary waldo or search d waldo

and press return to see a list of reminders in which either the summary or the `@d` element contains the case-insensitive regular expression "waldo". Each line of the display contains the item type, the summary and the document id of the matching reminder. As another example

		exists u and ~exists i

would display reminders with @u elements but not an @i element. 

Simple queries of this type produce a list of matching items with the itemtype, summary and id displayed and sorted by id, i.e., by the order created. It is also possible to create more complex queries in which the output is displayed heirarchially using a format determined by the query parameters. Enter `?` or `help` at the prompt to get detailed usage information.

As with other etm views, in query view you can press `Ctrl-C` to copy the view to the system clipboard or select a reminder and press `Enter` to display its details, press `E` to edit it and so forth. 

### [Common Features](#overview)

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
    * Press “/“ (forward slash) and enter an expression to search the view for a row whose content contains (case insensitive) the expression. 
	* While entering the search expression, push the `up` or `down` cursor keys to change the direction of search.
    * After entering the search expression, press “n” to search (cyclically) for other matches in the direction specified.
	* Once a search is initiated, it remains active in all views with matches highlighted. To remove the highlighting, search for something not likely to be matched such as 3 consecutive commas.


## [Menus](#overview)

### [etm](#overview)

Pressing F1 toggles the *etm* menu display - opening it if it is closed and closing it if it is open. The first of four menus is labeled *etm*: 

<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/menu-etm.png" alt="etm" title="menu-etm" width="50%" height="50%"/>

As with the other menus, each entry is preceeded by its shortcut, e.g., F2 for *about etm* or `^q` (`control` and `q` simultaneously) to quit.

Many of the entries are obvious but a few deserve comment.

* *import file* supports importing three different file types. A file ending with `.json` is expected to be one exported from *etm* 3.2.x. A file ending with  `.text` is expected to be a text file with lines corresponding to *etm* 4.x reminders. A file ending with `.ics` is expected to be a file in *iCalendar* format.
* *datetime calculator* processes an expression of the form `x [+-] y` where x is a datetime and y is either a timeperiod with `+` or a datetime or a timeperiod with `-`. As an example, suppose you have the arrival time in Paris of a flight and the departure time from Raleigh/Durham and you would like to determine the flight time. Entering

			7:45a 4/7 Europe/Paris - 5:30p 4/6 US/Eastern

    yields 

			8 hours 15 minutes
* *configuration settings* opens the file `cfg.yaml` using the default text editor for your operating system. Note that any changes you make to this file will not take effect until you close and reopen *etm*.
* *help* opens the *etm* documentation on google pages using the default web browser for your system. This is the most user friendly source for the documentation because it begins with a table of contents whose elements are active links to the relevant sections. It is updated with every commit so it is always the most recent version available.

### [view](#overview)

The *view* menu provides access to all the *etm* views with the shortcut keys for these views. E.g., press `a` to open *agenda view*. 

<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/menu-view.png" alt="view" title="menu-view" width="75%" height="75%"/>

The entries here are pretty obvious and the views themselves are descibed elsewhere.

### [editor](#overview)

<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/menu-editor.png" alt="editor" title="menu-editor" width="50%" height="50%"/>

It is worth noting here that when you are editing an item, `^s` (control and s) saves any changes you have made and closes the editor. `escape`, on the other hand, closes the editor without saving any changes but, if there are changes, asks for confirmation that this is what you want. 

### [selected](#overview)

Options in the *selected* menu are only relevant when a reminder has been selected in one of the views.

<img src="https://raw.githubusercontent.com/dagraham/etm-dgraham/master/menu-selected.png" alt="selected" title="menu-selected" width="75%" height="75%"/>

Several options here deserve comment.

* *delete* will prompt for comfirmation and, if the selected item is repeating, for whether to delete only the selected instance or the item itself, i.e., all instances. 
* *finish* applies only to unfinished task and will prompt for a datetime to use in creating an `@f` entry for the task.
* *reschedule* will prompt for a datetime. If the reminder is repeating, the provided datetime will replace the datetime of the selected instance. Otherwise it will be used either to replace the current value of `@s` or, if there is no `@s` entry, to create one.
* *schedule new* will prompt for a datetime and add that instance to any other instances of the reminder.
* *open goto* will use the system default application to open the file path or url specified in the selected reminders `@g` entry.
* *begin timer then toggle paused/running* will create and start an active timer associated with the selected reminder if an active timer does not currently exist and will otherwise toggle the paused or running state of the active timer.
* When a timer is active, the current status of the timer is displayed in the bottom, status line just to the left of the view name. For example, `3m*` would mean that the timer has 3 minutes of elapsed time and, because of the asterisk, that the timer is running. When the timer is paused, an exclamation point replaces the asterisk. 
* If there is an active timer, *record used time* will create an `@u` entry in the associated reminder using the current elapsed time as the time period and the current datetime as the ending time and then cancel the active timer. If there is no active timer, then *record used time* will prompt for a timeperiod and an ending time and then create an `@u` entry in the selected reminder using those elements. 


## [Installation/Deinstallation](#overview)

### [Installation](#overview)

<!--  [![etm: installing etm in a virtual environment](http://img.youtube.com/vi/fEPPG82AH7M/0.jpg)](http://www.youtube.com/watch?v=fEPPG82AH7M "installing etm in a virtual environment") -->

Setting up a virtual environment for etm is recommended. The steps for OS/X or linux are illustrated below. For details see [python-virtual-environments-a-primer](https://www.google.com/url?q=https%3A%2F%2Frealpython.com%2Fpython-virtual-environments-a-primer%2F&sa=D&sntz=1&usg=AFQjCNFh7QpJQ4rPCDjZ1eLrV1BRCCpSmw).

Open a terminal and begin by creating a new directory/folder for the virtual environment, say `etm-pypi` in your home directory:

        $ mkdir ~/etm-pypi
        $ cd ~/etm-pypi

Now continue by creating the virtual environment (python >= 3.7.4 is required for etm):

        $ python3 -m venv env

After a few seconds you will have an `./env` directory. Now activate the virtual environment:

        $ source env/bin/activate

The prompt will now change to something containing `(env)` to indicate that the virtual environment is active. Updating pip is now recommended:

        (env) $ pip install -U pip

Note that this invokes `./env/bin/pip`. Once this is finished, use pip to install etm:

        (env) $ pip install -U etm-dgraham

This will install etm and all its requirements in 

		./env/lib/python3.x/sitepackages 

and will also install an executable called `etm` in `./env/bin`. 

By the way, the suggested terminal size for etm is 60 (columns) by 32 or more (rows). The default color scheme is best with a dark terminal background. A scheme better suited to light backgrounds can be set using `style: light` in `cfg.yaml` in your home directory. Some of the *etm* display may not be visible unless `style` is set correctly for your display. 

Before you start etm, think about where you would like to keep your personal data and configuration files. The default is to use whatever directory you're in when you start _etm_ as your _etm_ home directory. If you start _etm_ in your virtual environment directory then the default will be to use that as your home directory as well. If this is not what you want, you can just give the path for whatever directory you would like to use when you start _etm_, e.g.,

        (env) $ etm ~/Documents/etm

Considerations:

* If more than one person will be using etm on the same computer, you might want to have different *home* directories for each user.
* If you want to use etm on more than one computer and use Dropbox, you might want to use `~/Dropbox/etm` to have access on each of your computers.
* If you want to separate personal and professional reminders, you could use different _home_ directories for each. You can run two instances of _etm_ simultaneously, one for each directory, and have access to both at the same time. 
* You can have multiple instances of *etm* running with the same *home* directory, provided that you treat all instances save one as **read only**, i.e., only make changes in one instance.

Whatever *home* directory you choose, running etm for the first time will add the following to that directory.

        etm home directory/
            backups/
            logs/
            cfg.yaml
            db.json

Here `cfg.yaml` is your user configuration file and `db.json` contains all your etm reminders. The folders `backups/` contains the 5 most recent daily backups of your `db.json` and `cfg.yaml` files. The folder `logs` contains the current `etm.log` file and the 5 most recent daily backups. Note that backup files are only created when the relevant file has been modified since the last backup.

The file `cfg.yaml` can be edited and the options are documented in the file.
See [configuration](#configuration) for details. 

### [Deinstallation](#overview)

If you should ever want to deinstall etm, first deactivate the virtual environment, if necessary, by changing to the virtual environment directory and entering

        (env) $ deactivate

You can now simply delete the virtual environment directory and, if you have additional *home* directories, delete each of them. One of the many advantages of the virtual environment is that these steps remove every trace.

# [Details](#overview)

## [Item Types](#overview)

### [event](#overview)

Type character: **\***

An event is something that happens at a particular date or datetime without any action from the user. Christmas, for example, is an event that happens whether or not the user does anything about it.


- The `@s` entry is required and can be specified either as a date or as a datetime. It is interpreted as the starting date or datetime of the event. 
- If `@s` is a date, the event is regarded as an *occasion* or *all-day* event. Such occasions are displayed first on the relevant date. 
- If `@s` is a datetime, an `@e` entry is allowed and is interpreted as the extent or duration of the event - the end of the event is then given implicitly by starting datetime plus the extent and this period is treated as busy time. 

Corresponds to VEVENT in the vcalendar specification.

### [task](#overview)

Type character: **-**

A task is something that requires action from the user and lasts, so to speak, until the task is completed and marked finished. Filing a tax return, for example, is a task. 

- The `@s` entry is optional and, if given, is interpreted as the date or datetime at which the task is due. 
    - Tasks with an `@s` datetime entry are regarded as pastdue after the datetime and are displayed in *Agenda View* on the relevant date according to the starting time. 
    - Tasks with `@s` date entry are regarded as pastdue after the due date and are displayed in *Agenda View* on the due date after all items with datetimes.
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

### [record](#overview)

Type character: **%**

A record of something that the user wants to remember. The userid and password for a website would be an example. A journal entry for vacation day is another example. 

- The `@s` is optional and, if given, is interpreted as the datetime to which the record applies. 
- Records without @s entries might be used to record personal information such as account numbers, recipies or other such information not associated with a particular datetime. They are displayed in the *Record* view
- Records with @s entries associate the record with the datetime given by @s. A vacation log entry, for example, might record the highlights of the day given by @s. They are displayed in the *Agenda* view as well as the *Record* view.

Corresponds to VJOURNAL in the vcalendar specification.

### [inbox](#overview)

Type character: **!**

An inbox item can be regarded as a task that is always due on the current date. E.g., you have created an event to remind you of a lunch meeting but need to confirm the time. Just record it using **!** instead of **\*** and the entry  will appear highlighted in the agenda view on the current date until you confirm the starting time. 

Corresponds to VTODO in the vcalendar specification.

### [status](#overview)

These type characters are generated automatically by *etm* to display the status of reminders.

#### [beginning soon](#overview)

Type character: **>**

For unfinished tasks and other items with `@b` entries, when the starting date given by `@s` is within `@b` days of the current date, a warning that the item is beginning soon appears on the current date together with the item summary and the number of days remaining until the current date.

#### [past due](#overview)

Type character: **<**

When a task is past due, a warning that the task is past due appears on the current date together with the item summary and the number of days that the task is past due. 

#### [waiting](#overview)

Type character: **+**

When a task job has one or more unfinished prerequisites, it is displayed using **+** rather than **-**.

#### [finished](#overview)

Type character: **✓**

When a task or job is finished, it is displayed in the _completed view_ on the  date that it was finished using **✓** rather than **-**. 

## [Options](#overview)

Notes:

* The term "list" means a comma and space separated list of elements, e.g., 

    @+ 2p Thu, 9p Mon, 11a Wed

* Options displayed with an asterick can be used more than once, e.g., 

    @a 1h, 30m: t, v @a 1d: e

    @n joe: jdoaks@whatever.com  @n john: jsmith@wherever.org

	@t red  @t green


### [@ keys](#overview)

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
*  @i: index. forward slash delimited string. E.g., client/project/activity
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
*  @z: timezone. string. A timezone specification, such as 'US/Eastern' or 'Europe/Paris' for aware datetimes or 'float', to indicate a naive or floating datetime. Datetime entries in the item are interpreted as belonging to the specified timezone when the entry is saved. The current timezone is the default when @z is not specified. Aware datetimes are converted to UTC (coordinated universal time) when stored and the @z entry, now irrelevant, is discarded.


### [& keys](#overview)

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


## [Notes](#overview)

### [alerts and beginbys](#overview)

* Alerts and beginbys can be added to any reminder with an `@s` start date/time entry. Alerts require a datetime in `@s`; beginbys also allow a date in `@s`.
* A beginby is specified by adding `@b n` to a reminder where `n` is a positive integer and is interpreted as a number of days. A reminder with such an entry will be displayed in *agenda view* on the current date provided that the current date is no more than `n` days before the start date/time of the reminder. Such a warning will appear n days before, n-1 days before and so forth until 1 day before the starting date/time of the reminder. The warning displays the type character `>`, the summary of the reminder and the number of days remaining. 
* An alert is specified by adding `@a <list of time periods>: <list of commands>` to a reminder. The time periods must be given in the usual etm format, e.g., `1h13m` for one hour and 13 minutes. The commands are single alphabetic characters, e.g., `a`, `b` and such. The commands used must either be `e` (email) or `t` (text) or be specified in the `alerts` section of the `cfg.yaml` file in your etm home directory. See [configuration](#configuration) for details about this file. Basically, it associates a command, such as `v` with a shell command to be invoked when an alert that includes `v` is triggered. E.g., the alert

			@a 20m: v

    would be triggered 20 minutes before the datetime specified in the reminder's `@s` entry and at that time the shell command associated with `v` would be invoked. Both positive (before) and negative (after) time periods can be used. Thus this entry

			@a 1d, -1h: v, w

	would invoke the shell commands associated with `v` and `w`, one day *before* and again 1 hour *after* the datetime specified in the reminder's `@s` entry.
* Reminders can have more than one `@a` alert entries. Different alerts could, for example, be used to trigger their commands at different times.
* With an email, `e`, or text alert, `t`, the item summary is used as the subject and an email or text message is sent to each attendee listed in @n entries. The content of the body of the emails/messages are options that can be set in the user's configuration file. 
* Alerts and beginbys are only triggered for unfinished tasks and, when the task is repeating, only for the first unfinished instance. Similarly, pastdue notices for repeating tasks are only triggered for the first unfinished instance.

### [repetition](#overview)

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


* @r examples

	* Christmas (an all day event) [r]epating (y)early on Dec 25.

			* Christmas @s 2015/12/25 @r y

	* Get a haircut (a task) on the 24th of the current month and then [r]epeatedly at (d)aily [i]ntervals of (14) days and, [o]n completion, (r)estart from the last completion date:

			- haircut @s 24 @r d &i 14 @o r

	* Take out trash (at task) on Mondays but if the task becomes [o]verdue, (s)kip the pastdue reminders.

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


### [configuration](#overview)

Configuration settings for *etm* are specified in the file `cfg.yaml` located in your etm *home directory*. See [installation](#installation) for the location of this directory. When *etm* is running, you can press `F8` to open this configuration file using your system default editor for *yaml* (text) files. Note that any changes you make will not become effective until you stop and restart *etm*. 

Here are the options with their default values from that file. The lines beginning with `#` are comments that describe the settings.

        # ampm: true or false. Use AM/PM format for datetimes if true 
        # else use 24 hour format. 
        ampm: true

        # locale: A two character locale abbreviation. E.g., "fr" for 
        # French.
        locale: en

        # style: dark or light. Designed for, respectively, dark or 
        # light terminal backgounds. Some output may not be visible
        # unless this is set correctly for your display.
        style: dark

        # colors: a 'namedcolor' entry for each of the following items:
        #     plain:        headings such as outline branches
        #     today:        the current date heading in agenda view
        #     inbox:        inbox reminders
        #     pastdue:      pasdue task warnings
        #     begin:        begin by warnings
        #     record:       record reminders
        #     event:        event reminders
        #     waiting:      waiting job reminders (unfinished prereqs)
        #     finished:     finished task/job reminders
        #     available:    available task/job reminders 
        # The default entries are suitable for the style "dark" given 
        # above. 
        # To restore the default colors for whichever "style" you have
        # set above, remove the color name for each of the items you 
        # want to restore and restart etm. 
        # To preview the namedcolors, download "namedcolors.py" from 
        #    "https://github.com/dagraham/etm-dgraham",
        # open a terminal with your chosen background color and run
        #    python3 <path to namedcolors.py>
        # at the command prompt.
        # Note that the color names are case sensitive. 
        colors:
          plain: Ivory
          today: Ivory bold
          inbox: Yellow
          pastdue: LightSalmon
          begin: Gold
          record: GoldenRod
          event: LimeGreen
          waiting: SlateGrey
          finished: DarkGrey
          available: LightSkyBlue

        # secret: A string to use as the secret_key for @m masked 
        # entries. In etm versions after 4.0.21, the default string 
        # is randomly generated when this file is first created and 
        # should be unique for each etm installation. WARNING: if 
        # you change this key, any @m entries that you made before 
        # the change will be unreadable after the change. 
        secret: <randomly generated alphanumeric string>

        # omit_extent: A list of calendars. Events with @c entries
        # belonging to this list will only have their starting times
        # displayed in agenda view and will neither appear nor cause
        # conflicts in busy view.
        omit_extent:
        - omit

        # keep_current: true or false. If true, the agenda for the  
        # current and following two weeks will be written to "current.txt" 
        # in your etm home directory and updated when necessary. You 
        # could, for example, create a link to this file in a pCloud or 
        # DropBox folder and have access to your current schedule on 
        # your mobile device.
        keep_current: false

        # archive_after: A non-negative integer. If zero, do not 
        # archive items. If positive, finished tasks and events with 
        # last datetimes falling more than this number of years 
        # before the current date will automatically be archived on a 
        # daily basis.  Archived items are moved from the "items" 
        # folder in the database to the "archive" folder and no 
        # longer appear in normal views. Note that unfinished tasks 
        # and records are not archived.
        archive_after: 0

        # num_finished: A non-negative integer. If positive, when 
        # saving retain only the most recent 'num_finished' 
        # completions of an infinitely repeating task, i.e., repeating 
        # without an "&c" count or an "&u" until attribute. If zero or 
        # not infinitely repeating, save all completions.
        num_finished: 0

        # usedtime_minutes: Round used times up to the nearest 
        # usedtime_minutes in used time views. Possible choices are 1, 
        # 6, 12, 30 and 60. With 1, no rounding is done and times are 
        # reported as hours and minutes. Otherwise, the prescribed 
        # rounding is done and times are reported as floating point 
        # hours. Note that each "@u" timeperiod is rounded before 
        # aggregation.
        usedtime_minutes: 1

        # alerts: A dictionary with single-character, "alert" keys and 
        # corresponding "system command" values. Note that characters 
        # "t" (text message) and "e" (email) are already used.  The 
        # "system command" string should be a comand with any 
        # applicable arguments that could be run in a terminal.
        # Properties of the item triggering the alert can be included 
        # in the command arguments using the syntax '{property}', e.g., 
        # {summary} in the command string would be replaced by the 
        # summary of the item. Similarly {start} by the starting time, 
        # {when} by the time remaining until the starting time, 
        # {location} by the @l entry and {description} by the @d entry. 
        # E.g., If the event "* sales meeting @s 2019-02-12 3p" 
        # triggered an alert 30 minutes before the starting time the 
        # string "{summary} {when}" would expand to "sales meeting in 
        # 30 minutes". E.g. on my macbook
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
        alerts:

        # expansions: A dictionary with 'expansion name' keys and 
        # corresponding 'replacement string' values. E.g. with
        #
        #    expansions:
        #        tennis: "@e 1h30m @a 30m: d @i personal:exercise" 
        #        ...
        #
        # then when "@x tennis" is entered the popup completions for 
        # "@x tennis" would offer replacement by the corresponding 
        # "@e 1h30m @a 30m: d @i personal:exercise".
        expansions:

        # sms: Settings to send "t" (sms text message) alerts to the 
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
        sms:
          body: '{location} {when}'
          from:
          pw:
          server:

        # smtp: Settings to send "e" (email message) alerts to the 
        # list of email addresses from the item's @n attendee
        # entries using the item's summary as the subject and body as 
        # the message. E.g., if you have a gmail account with email 
        # address "whatever457@gmail.com", then your entries should 
        # be
        #     from: whatever457@gmail.com
        #     id: whatever457
        #     pw: your gmail password
        #     server: smtp.gmail.com
        smtp:
          body: "{location} {when}\n{description}"
          from:
          id:
          pw:
          server:

Note that in the 'dictionary' entries above, the components must be indented. E.g., the illustrative alert entry would be:

	alerts:
	    v: /usr/bin/say -v "Alex" "{summary}, {when}"


### [data storage](#overview)

All *etm* reminders are stored in the text file `db.json` in your etm home direcotry using the wonderful *TinyDB* package. This *json* file is human readable but not easily editable. When you start *etm* for the first time, this file will have no entries:

	{
	"items": {},
	"archive": {}
	}

Note that to *json* this is a hash/dictionary with two keys: "items" and "archive". Both have empty hashes/dictionaries as values.

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

Take the entry `2019-12-23` for `@s`. To *etm* this is a pendulum date object. When *etm* stores this record, *TinyDB* recognizes that this attribute is a pendulum date object and encodes/serializes it as the string `"{D}:20191223"`. When *etm* retrieves this record from storage, *TinyDB* recognizes from the `{D}` that it is to be decoded and returned as a pendulum date object. All this is completely transparent - *etm* gives a date object to *TinyDB* which stores it as a string and when *etm* wants it back, *TinyDB* deserializes it and returns it as a date object.

As another example, When the reminder is created by *etm* the `created` timestamp is handed to *TinyDB* as an aware pendulum datetime object with US/Eastern as the timezone. *TinyDB* recognizes this and, because it is an aware datetime, first converts it to Universal time and then encodes/serializes it at `"{T}:20191221T1526A"`. The `{T}` indicates that it is a datetime object and the appended `A` indicates that it is aware and thus has been converted to Universal time. When *etm* retrieves this record, *TinyDB* recognizes from the `{T}` and the `A` that this is an aware datetime object, decodes it as an aware datetime object and, because it is aware, converts it from Universal time to whatever the current local timezone happens to be before returning it. Had this been a naive datetime, an `N` would have been appended to the serialization and no conversion would have been done either way.

These **date** and **datetime** serializations are extensions of *TinyDB* provided by *etm*. Three further extensions are also provided: **interval** for *pendulum duration* objects using the tag `{I}`, **weekday** for  *dateutil* weekday objects using the tag `{W}` and **mask** using the tag `{M}` for encoding/serializing *etm* strings in a masked or obfuscated manner.

