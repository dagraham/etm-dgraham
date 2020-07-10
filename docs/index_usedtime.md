# Tracking Time with Index and UsedTime

Here are some suggestions for using *index* (@i) and *usedtime* (@u) entries for tracking time spent. The general idea is to use (@u) *usedtime* entries in your reminders to record the period of time spent and the moment at which the period ended. These periods will automatically be attributed by *etm* to the (@i) *index* entry in the relevant reminders. 

## Index entries

The key issue with using index entries is to decide upon a pattern that fits your needs and then stick to that pattern. The general idea is to begin with the most general classifier and then add as many refinements as seem appropriate. 

    @i general/more particular/...
A good *general* classifier is the intended beneficiary of the activity. Here are some examples where the beneficiary is a client and the subsequent classifiers are *project* and *activity*:
* @i ABC, Inc/sales agreement/meeting
* @i ABC, Inc/sales agreement/document prep

and some others where the beneficiary is yourself
* @i personal/exercise/walking
* @i personal/reading/history
* @i personal/reading/fiction

My own experience is that three levels works well but you might want more or less. One thing to remember is that *etm* will display all the branches from a common root at the same length. E.g. with the personal branches given above the *index* view would display all branches at the common length of 3:

    1  2  3  
    personal
       exercise
          walking
             ...
       reading
          history
             ...
          fiction
             ...
But with these unequal personal branches
* @i personal/exercise
* @i personal/reading/history
* @i personal/reading/fiction

the *index* view display would instead display all branches at the shortest common length of 2:

    1  2  
    personal
       exercise
          ...
       reading/history
          ...
       reading/fiction
          ...
Creating branches from the same root with equal lengths is recommended. Once you have used a particular index entry in any *etm* reminder, it will be available for auto completion so preserving consistency will be easy.

## UsedTime entries

Now consider the process of adding usedtime entries to your reminders. Suppose, for example, you have a lunch meeting with a client, ABC, to discuss a project, *sales agreement* that you are preparing for them. You have two related reminders, an event and a task:

	* lunch meeting @s fri 1p @e 90m @i ABC, Inc/sales agreement/meeting
	- prepare contract @i ABC, Inc/sales agreement/document prep
After the meeting ends, you estimate that about 50% of the time was actually work related, so you want to attribute `@i ABC, Inc/sales agreement/meeting` for 45 minutes. To do this, select the *lunch meeting* event, press *Ctrl-T* (record usedtime) and, at the prompt, enter `45m: 2p` and press *enter*. Supposing that it is currently, Friday, July 3, 2020, this will add the entry `@u 45m: 2020-07-03 2:00pm` to the *lunch meeting* event.

Suppose you then decide to work on the *prepare contract* task. Begin by selecting the task and pressing *T* (toggle timer). The status bar will then display `0m*` the asterisk indicating that a timer is running and that thus far zero minutes have accumulated. You are interrupted after a while by a phone call, so you press *T* again to pause the timer and notice that the status bar now displays `17m!`, the exclamation point indicating that the timer is paused and that thus far 17 minutes have accumulated. After the phone call ends, you press *T* again to restart the timer and eventually decide to stop work on the contract for a while with 1h5m showing on the timer, so you press *Ctrl T* (record used time). This time, however, you are not prompted to enter a period and ending time but are instead asked to confirm that you want to record `1h5m` of usedtime in the reminder that you selected when you started the timer. If you confirm this addition, a usedtime entry will be appended to the selected item using the period `1h5m` and the datetime at which you pressed *Ctrl-T*. 

If you want to resume work on the contract later, you can repeat the process of selecting the task, pressing *T* to start a timer and, when you are done, pressing *Ctrl-T* to record the time spent. This will add another (@u) used time entry to the task. 

When a timer is active, either running or paused and thus displayed in the status bar, then pressing *Ctrl-T* will prompt for confirmation to record the accumated time to the originally selected item and using the current moment as the time. If, on the other hand, no timer is active, then pressing *Ctrl-T* with an item selected, will instead prompt for the timeperiod and ending datetime to use. 

You could, of course, open reminders for editing and manually add the usedtime entries yourself, but the shortcuts are more convenient.


## Used Time views

Reminders with usedtime entries are reported in the *completed* view along with finished tasks and jobs to give you a week by week summary of what you've accomplished. The main views for used time are, however, the *used time* and *used time summary* views. These display monthly aggregates of times for reminders that have **both** @i and @u entries. The organization and aggregation comes from the index entries and the times themselves come from the (@u) usedtime entries in your reminders.

The following are examples of these views using the sample data file  
[db.json](https://groups.io/g/etm/files/sample%20files/db.json).[^sample]

    July 2020
      client A
        project a1
          activity a1
            - Amet eius aliquam dolore          Jul 6: 46m 
            % Consectetur aliquam adipisci      Jul 14: 46m 
          activity a2
            - Adipisci sed velit sit quaer…     Jul 6: 1h4m 
            % Sed labore ut eius eius           Jul 13: 1h38m 
            - Magnam est ut sed tempora         Jul 22: 52m
     ...
and the corresponding *used time summary* view

    July 2020: 32h
       client A: 14h10m 
          project a1: 5h6m 
             activity a1: 1h32m 
             activity a2: 3h34m 
      ...
and here are the relevant reminders

    - Amet eius aliquam dolore @u 46m: 2020-07-06 4:46pm 
      @i client A/project a1/activity a1 
    % Consectetur aliquam adipisci @u 46m: 2020-07-14 
      @i client A/project a1/activity a1 
    - Adipisci sed velit sit quaerat @u 1h4m: 2020-07-06 9:04am 
      @i client A/project a1/activity a2 
    % Sed labore ut eius eius 
      @u 28m: 2020-07-13 3:28pm @u 1h10m: 2020-07-13 4:10pm 
      @i client A/project a1/activity a2 
    - Magnam est ut sed tempora @s 2020-07-22 3:00pm 
      @u 52m: 2020-07-22 
      @i client A/project a1/activity a2 
Note that the times reported in the *used time* view are themselves aggregates. E.g., the 1h38m reported for *Sed labore...* is the sum of the 28m and 1h10m recorded on 7/13. 

[^sample]: Please consider downloading this file, putting it in a new directory that you create for the purpose and then starting etm with the path to this directory. You can play around with a fairly extensive collection of reminders without modifying your own data. 

It is also worth noting that the aggregates displayed involve no rounding because of the `usedtime_minutes: 1` setting in the relevant configuration file. Had this setting been, e.g., `usedtime_minutes: 6` then all @u entries would have been rounded up to the nearest 6 minutes (1/10 of an hour) and the totals would have been reported in hours and tenths as

    July 2020
      client A
        project a1
          activity a1
            - Amet eius aliquam dolore          Jul 6: 0.8h 
            % Consectetur aliquam adipisci      Jul 14: 0.8h  
          activity a2
            - Adipisci sed velit sit quaer…     Jul 6: 1.1h 
            % Sed labore ut eius eius           Jul 13: 1.7h  
            - Magnam est ut sed tempora         Jul 22: 0.9h  
      ...
and 

    July 2020: 33.3h
       client A: 14.7h 
          project a1: 5.3h 
             activity a1: 1.6h 
             activity a2: 3.7h 
      ...
Note that the level of the refinements in the @i entries determine the level of the refinements in these used time views. 
