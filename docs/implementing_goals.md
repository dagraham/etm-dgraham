# Weekly Goals

![alt text](image.png)

"walk the dog" is selected and the details panel shows its format. The leading "3/7+2 (4.8)" in the main window indicates that 3 instances of the goal of 7 have been completed in the current week, that 2 more completions today are needed to get back on schedule for the week and that 4.8 is the current average number of completions per week. (@h in the details panel shows the complete history of completions by year:week.) 

In the main window, active goals are sorted by their done/quota ratios and given a color indicating the degree of progress toward completing the goal for the current week based on comparing the done/quota fraction to the fraction of the week that has passed. Since the current weekday, Friday, is the 5th day of the week, the fraction of the week that has passed is somewhere between 4/7 (beginning of Friday) and 5/7 (end of Friday).   
- walk the dog:  colored red because 3/7 is less than 4/7 and thus completions are unambiguously behind schedule for the week - 2 completions today are needed to get back on schedule.
- wash dishes: colored yellow because 3/5 is between 4/7 and 5/7 - 1 completion today is needed to get back on schedule.
- interval training: blue because 3/4 > 5/7 and thus completions are ahead of schedule for this week - no completions are needed today to stay on schedule.

This is a normal view in etm and all the normal commands are available. Additionally, these commands are available when a goal is selected:
- F) increment the completion count for the current week (by incrementing the count for the current week in @h)
- ^a) toggle the active/inactive status (by reversing the sign of the quota component of @q). 
- ^e) end the goal (by setting the quota component of @q equal to zero)

Notes
- @q can optionally contain a number of weeks specification as well as a quota. E.g., "@q 3, 2" would specify a quota of 3 instances per week for 2 weeks. After the passage of the second week, the goal would be listed as "Ended".
- The entry for @s is automatically converted to the first day (Monday) of the week containing the specified datetime. If @s specifies a datetime after the current week, the goal would be listed as "Inactive" until the relevant week arrives.
- Goals view is activated either from the menu or by pressing "g". The binding for "open goto link" has been changed from "g" to "G". 

