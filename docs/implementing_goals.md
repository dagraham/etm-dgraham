# Weekly Goals

## Using Agenda View

A "goal" reminder uses the type character "~" to specify the number of times per week that an instance of the goal is to be done. E.g., in the week beginning next Monday a goal of doing "whatever" at least 3 times would be specified as:

```
    ~ whatever @s mon @q 3 
```

As given this goal extends indefinitely but it could be limited to, say, five weeks by specifying `@q 3, 5` instead of `@q 3`. 

Unlike a task, the concepts of "finished", "unfinished" and "pastdue" are irrelevant. 

Beginning next Monday, the goal would be displayed on the current day as

```
                    Apr 29 - May 5, 2024 #18
    Mon Apr 29 (Today)
      ~ 0/3 whatever

                                                        agenda
```

indicating that goal is active for the week and that zero of the three instances have been done.

With "~ whatever" selected, pressing "F" would increment the record of the times done and change the display to 

```
                    Apr 29 - May 5, 2024 #18
    Mon Apr 29 (Today)
      ~ 1/3 whatever

                                                        agenda
```

On Wednesday, selecting "~ whatever" and pressing "F" again would yield 

```
                    Apr 29 - May 5, 2024 #18
    Wed May 1 (Today)
      ~ 2/3 whatever

                                                        agenda
```

Two more presses of "F" on Sunday would yield

```
                    Apr 29 - May 5, 2024 #18
    Sun May 5 (Today)
      ~ 4/3 whatever

                                                        agenda
```

The status of the goal for the current week is always displayed on the current date and on Mondays of relevant future weeks in Agenda View.  The history is displayed in a Goals section of Completed View. E.g., this Completed View 

```
                    Apr 29 - May 5, 2024 #18
    Sun May 5
      ...

    
    Goals
      ~ whatever: 4
      ...

                                                     completed
```

would indicate that four completions have been recorded for "~ whatever" for week number 18 of 2024. Totals for all relevant goals for the week would be listed alphabetically in this section.

## Using Goals View

Analagous to journal view - not weekly

### Sections

- Active:
    clickable list of active goals
- Inactive: 
    clickable list of paused goals
- Inactive: 
    clickable list of goals with @q entries with weeks that have expired  

Details shows complete history.

## Details

### History

A dictionary with integer (year, week_number) tuples as keys and integer (done, quota) tuples as values:

```
    @h Dict[string yyyy:ww, int done]
```

E.g, for the above examples involving week number 18, 2024 (Apr 29 - May 5), the history entry would be

```
    {'2024:18': 4}
```

### Actions

* Completion

    With a goal selected (on the current day), pressing "C" increments the num_done (first component) of the @h entry for the current 'yyyy:ww'. If the goal does not yet have an entry for @h, one is created using the format

    ```
        {'yyyy:ww': 1} 
    ```

* Pausing

    With a goal selected, pressing "P" toggles pausing the goal by reversing the sign of the quota in the @q entry.

* New day

    The current status of a goal is always displayed on the current day

    ```
        ~ done/quota summary
    ```


