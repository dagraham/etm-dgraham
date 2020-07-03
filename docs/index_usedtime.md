# Tracking Time with Index and UsedTime

Here are some suggestions for using index (@i) and usedtime (@u) entries for tracking time spent. As tracking expenditure is essential to managing your money, so tracking time spent is essential to managing and, perhaps, billing your time. 

## Index entries

The key issue with using index entries to file your activities is to decide upon a pattern that fits your needs and then stick to that pattern. The general idea is to begin with the most general classifier and then add as many refinements as seem appropriate. 

    @i general/more particular/...
A good *general* classifier is the intended beneficiary of the activity. Here are some examples where the beneficiary is a client and the subsequent classifiers are *project* and *activity*:
* ABC, Inc/sales agreement/contract prep
* ABC, Inc/sales agreement/conference call

and some others where the beneficiary is yourself
* @i personal/exercise/walking
* @i personal/reading/history
* @i personal/reading/fiction

My own experience is that three levels works well but you might want more or less. One thing to remember is that *etm* will display all the branches from a common root at the same length. E.g. with the personal branches given above the *index* view would display all branches at the common length of 3:

    1  2  3  4
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

    1  2  3
    personal
       exercise
          ...
       reading/history
          ...
       reading/fiction
          ...
Once you have used a particular index entry in any *etm* reminder, it will be available for auto completion so preserving consistency will be easy.

## UsedTime entries

The *used time* and *used time summary* views in *etm* display monthly aggregates of times for reminders that have **both** @i and @u entries. The organization and aggregation comes from the index entries and the times themselves comes from the usedtime entries.

Here is an example of the *used time* view from the sample files section

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
