# Using Timers

In *etm* 4.6.2 it became possible to associate timers with as many *etm* reminders as you wish. When the elapsed time in a timer is recorded, the usedtime entry is added to the associated reminder.

## Timer states

Each timer can be in one of the following states:
* inactive
* active and
    * running
    * paused

A reminder can have at most one associated timers and at most one timer can be *active* (*running* or *paused*) at any given moment. All other timers will be *inactive*.

## Timers in all views

A *t* is displayed in the *flags* column in all *etm* views for each reminder that has an associated timer. This flag joins three other possible flags for reminders that are pinned or have @g (goto) or @k (konnection) links.

If there is an *active* timer, its state, either *r* (running) or *p* (paused), is displayed in the etm status bar together with the relevant time period, either the total elapsed time or how long it has been paused. Additionally, if there are other *inactive* timers, their total elapsed time is also displayed with the label *i*. E.g., this status bar display would indicate that the active timer is running with 14 minutes of elapsed time and that there are other inactive timers with a total of 10 minutes of elapsed time.

    r:14m + i:10m

This status bar reminder is a reminder that the timer data is stored in memory and will be lost if etm is stopped. **Don't forget to record these timers before closing etm.**

## Timer view

This view lists all reminders with associated timers sorted by the elapsed time since the timer’s state was last changed. The display for each reminder shows the itemtype and summary, any applicable flags and, in the right hand column, the elapsed time and state of the associated timer.

The sort order assures that the reminder with the *active* timer will always be at the top of the list and followed by reminders with *inactive* timers that were most recently modified. This makes it easy to switch back and forth between recent timers.

## Key bindings

### timer creation and state change

* Press T with a reminder selected.
     * If no timer is currently associated with the reminder, one will be created. If no another timer is active, the new timer will be running, otherwise the new timer will be inactive.
     * If an inactive timer is already associated with the reminder. Its state will be changed to running. If another timer is active, its state will be changed to inactive and, if it had been running, its elapsed time will be updated.
     * If an active timer is already associated with the reminder, its state will be toggled between paused and running.
* Press TD (i.e., press T and the D) to delete the timer associated with the selected reminder. You will be prompted for confirmation.
* press TT (i.e., press T twice) to toggle the state of the active timer, if one exists, between paused and running. This is a shortcut for first selecting the reminder associated with the active timer and then pressing T.

### recording usedtime entries

* press TR with a reminder selected.
     * If a timer is not currently associated with the reminder, prompt for a timeperiod and ending time to use in adding a usedtime entry to the reminder.
     * If a timer is currently associated with the reminder, its elapsed time and the last moment it was running will be provided as the defaults in the prompt for a usedtime timeperiod and ending time. When submitted, the elapsed time for the timer will be reset to zero minutes and, if the timer had been *running* its state will be changed to *paused*. Otherwise, its state will be left unchanged.

### new reminders in timers view

If a new reminder is created in timers view, then a new timer will automatically be associated with the reminder. The state of the new timer will be *running* is there are no other timers and, otherwise, the state will be *inactive*.

To illustrate how this might be useful, suppose you are busy with something for which a timer is active and you get a call from Joe. You want to take this call and time it. Press *N* in timers view to create a new reminder, then enter

       ! Joe

and press *Ctrl-S* to save and close the editor. This inbox reminder will now appear immediately below your active timer where you need only to select it and press *T* to start it running. When the call ends, your timer for "Joe" will be at the top of the list and your previous timer will be right below it in second place. Select the previous timer and press *T* to restart it. When you have time, you can save the usedtime entry for “Joe” by selecting it and pressing *TR*. You can then make whatever other changes you like to the reminder itself.
