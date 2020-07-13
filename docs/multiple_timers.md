# Using Timers

The use of multiple timers was introduced in *etm* 4.6.2. Each timer is associated with an *etm* reminder - each reminder can have at most one assocated timer. When the elapsed time in a timer is recorded, the usedtime entry is added to the associated reminder.

## Timer states

Each timer can be in one of the following states:
* inactive
* active and
    * running
    * paused

At most one timer can be active (running or paused) at any given moment. All other timers will be inactive.

## Timers in all views

A flag, t, is displayed for reminders with associated timers in all views. This flag joins three other possible flags for reminders that are pinned or have @g (goto) or @k (konnection) links.

If there is an active timer, its state, either *r* (running) or *p* (paused), is displayed in the etm status bar together with the relevant time period, either its total elapsed time or how long it has been paused. Additionally, if there are other *inactive* timers, their total elapsed time is also displayed with the label *i*. E.g., this status bar display would indicate that the active timer is running with 14 minutes of elapsed time and that there are other inactive timers with a total of 10 minutes of elapsed time.

    r:14m + i:10m

This status bar reminder is a reminder that the timer data is stored in memory and will be lost if etm is stopped. 

## Timer view

This view lists all reminders with associated timers sorted by the elapsed time since the timer’s state was last changed. The display for each reminder shows the itemtype and summary, any applicable flags and, in the right hand column, the elapsed time and state of the associated timer.

The sort order assures that the reminder with the active timer will always be at the top of the list and followed by the reminders with the most recently modified timers. This makes it easy to switch back and forth between recent timers.

## Key bindings

### timer creation and state change

* Press T with a reminder selected.
     * If no timer is currently associated with the reminder, one will be created. If no another timer is active, the new timer will be running, otherwise the new timer will be inactive.
     * If an inactive timer is already associated with the reminder. Its state will be changed to running. If another timer is active, its state will be changed to inactive and, if it had been running, its elapsed time will be updated.
     * If an active timer is already associated with the reminder, its state will be toggled between paused and running.
* Press TD (i.e., press T and the D) to delete the timer associated with the selected reminder. You will be asked for confirmation.
* press TT (i.e., press T twice) to toggle the state of the active timer, if one exists, between paused and running. This is a shortcut for first selecting the reminder associated with the active timer and then pressing T.

### recording usedtime entries

* press TR with a reminder selected.
     * If a timer is not currently associated with the reminder, prompt for a timeperiod and ending time to use in adding a usedtime entry to the reminder.
     * If a timer is currently associated with the reminder, its elapsed time and the last moment it was running will be provided as the defaults in the prompt for a usedtime timeperiod and ending time.

### new reminders in timers view

If a new reminder is created in timers view, then a new timer will automatically be associated with the reminder. The state of the new timer will be inactive is another timer is active and, otherwise, the state will be running.

To illustrate how this might be useful, suppose you are busy with something for which a timer is active and you get a call from Joe. You want to take this call and to time it. Press *N* in timers view to create a new reminder, then enter

       ! Joe

and press *Ctrl-S* to save and close the editor. This inbox reminder will now appear immediately below your active timer where you need only to select it and press *T* to start it running. When the call ends, your previous timer will be next to the top of list with the timer for “Joe” at the top. Select the previous timer and press *T* to restart it. When you have time, you can save the usedtime entry for “Joe” by selecting it, pressing *Ctrl T* and making whatever other changes you like.
