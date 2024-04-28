# Weekly Goals

A "goal" reminder uses the type character "~" to specify the number of times per week that an instance of the goal is to be done. E.g., in the week beginning next Monday a goal of doing "whatever" at least 3 times would be specified as:

```
    ~ whatever @s mon @q 3 
```

As given this goal extends indefinitely but it could be limited to, say, five weeks by specifying `@q 3, 5` instead of `@q 3`. 

Unlike a task, the concepts of "finished", "unfinished" and "pastdue" are irrelevant. 

Supposing that it is currently Thursday, April 25 2024, this goal would be displayed in the Agenda View on Monday of the following week as

```
                    Apr 29 - May 5, 2024 #18
    Mon Apr 29
      ~ whatever: 3

                                                        agenda
```

indicating that the goal for that week is to complete three instances of "whatever". Next Monday, the display would change to 

```
                    Apr 29 - May 5, 2024 #18
    Mon Apr 29 (Today)
      ~ whatever: 0/3 > 7d

                                                        agenda
```

indicating that goal is active for the week, that zero of the three instances have been done and that seven days, including the current day, remain to complete them.

With "~ whatever" selected, pressing "F" would increment the record of the times done and change the display to 

```
                    Apr 29 - May 5, 2024 #18
    Mon Apr 29 (Today)
      ~ whatever: 1/3 > 7d

                                                        agenda
```

On Wednesday, selecting "~ whatever" and pressing "F" again would yield 

```
                    Apr 29 - May 5, 2024 #18
    Wed May 1 (Today)
      ~ whatever: 2/3 > 5d

                                                        agenda
```

Two more presses of "F" on Sunday would yield

```
                    Apr 29 - May 5, 2024 #18
    Sun May 5 (Today)
      ~ whatever: 4/3 > 1d

                                                        agenda
```

The status of the goal for the current week is always displayed on the current date and on Mondays of relevant future weeks in Agenda View.  The history is displayed on Sundays of previous weeks in Completed View. E.g., this Completed View 

```
                    Apr 29 - May 5, 2024 #18
    Sun May 5
      ~ whatever: 4/3

                                                     completed
```

would indicate that for the week ending on Sunday, May 5, "~ whatever" was completed four times when the goal was for three completions.

## Details

Done history: A dictionary with (year, week_number) tuples as keys lists of integer week day numbers (1 Mon, ... 7 Sun) as values:

```
    @h Dict[Tuple[int year, int week_num], List[int weekday_num]]
```
E.g, for the above examples involving week number 18, 2024 (Apr 29 - May 5), the history entry would be

```
    {(2024, 18): [1, 3, 7, 7]}
```

With a goal reminder selected on the current day, pressing "F" adds the current weekday number to `@h



