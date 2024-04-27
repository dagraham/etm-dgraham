# Goals

The objective is to implement a new item type "goal" with the type character "#". E.g., in the week beginning next Monday set a goal of doing "whatever" at least 3 times:

```
    # whatever @s mon @e 1w @q 3 
```

Unlike a task, such a goal applies just to the period from @s to @s + @e and the concepts of "finished", "unfinished" and "pastdue" are irrelevant.

This goal could also be repeated, e.g., weekly:

```
    # whatever @s mon @e 1w @q 3 @r w
```
with the relevant period extending from the datetime of the instance of the repetition to that datetime plus one week with the goal for each such period independent from other periods.

Next Monday, this goal could be displayed in Agenda View 

```
    Mon Apr 29 (Today)
      # whatever: 0/3 done with 7 days remaining
```
With "# whatever" selected, pressing "f" would increment the record of the times done and change the display to 

```
    Mon Apr 29 (Today)
      # whatever: 1/3 done with 7 days remaining
```
The current status of the goal would thus always be available on the current date. This would also be displayed in Completed View on the relevant date. 

Note that the status might alternatively be displayed in an abbreviated format as: 
```
    Mon Apr 29 (Today)
      # whatever: 1/3 > 7d
```

Skipping ahead to, say, Wednesday, selecting "# whatever ..." and pressing "f" again would yield 

```
    Wed May 1 (Today)
      # whatever: 2/3 > 5d
```
Completed view would also be updated to 

```
    Mon Apr 29 
      # whatever: 1/3 > 7d
    Wed May 1 (Today)
      # whatever: 2/3 > 5d
```
With two more presses of "f" on Sunday, Completed View for the week would appear as

```
    Mon Apr 29 
      # whatever: 1/3 > 7d
    Wed May 1
      # whatever: 2/3 > 5d
    Sun May 5
      # whatever: 3/3 > 0d
      # whatever: 4/3 > 0d
```
Note that Completed View would thus show the history of times done for each week. 



