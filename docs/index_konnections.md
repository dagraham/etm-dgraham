# Organizating with Index and Konnection[^kon]

Here is a possible use case for organizing relevant reminders based on their  index (@i), and konnection (@k), entries. The example is based on a user who has clients for whom projects are undertaken and one or more contacts for each client. 

[^kon]: The term 'konnection' is meant to suggest *connection* but using the letter *k* which is unemployed, instead of *c* which is already in use for *calendar*. Konnection entries are available for *etm >= 4.6.0*.


## Organizing with @i (index) entries

1. Use @i to organize your client, and contact information with journal entries such as these

        % ABC, Inc @i clients
        % Clair Smith - sales @i contacts/ABC, Inc
        % Bill Zoller - accounting @i contacts/ABC, Inc 
        % IOU, Ltd @i clients
        % Hal Burns - CEO @i contacts/IOU, Ltd

   At this point your *index* view in *etm* would look like this:

        clients
          % ABC, Inc
          % IOU, Ltd
        contacts
          ABC, Inc
            % Clair Smith - sales
            % Bill James - accounting
          IOU, Ltd
            % Hal Burns - CEO

  While creating these entries, you may want to add useful information such as

  * a goto link with the url for ABC, `@g www.abc.com`, in its client record.
  * the phone number for Clair Smith, `@n Clair Smith: 123 456-7890`, in  her contact record.
  * personal information for Bill James in his contact record 

        @d Married to Joan, 3 children John (1985), Frank (1988) 
           and Sally (1991) 
    All such information is just a click away and entries for attributes such as `@n` are added to the auto completion list so that typing 
    `@n c` in another reminder would pop up a list of completions including the one for Clair.

2. As you create client/contact related events, tasks or other journal entries, include an @i entries for the relevant project, here a *sales agreement*:

        * conference call @s 2p fri @i ABC, Inc/sales agreement
        - prepare contract @i ABC, Inc/sales agreement
   Note that autocompletion is also available for `@i` entries, so that
   typing `@i A` in the 'prepare contract' task would pop up a list of completions including those for `ABC, Inc`.


   Your *index* view would now expand to 

        clients
          % ABC, Inc
          % IOU, Ltd
        contacts
          ABC, Inc
            % Clair Smith - sales
            % Bill James - accounting
          IOU, Ltd
            % Hal Burns - CEO
        ABC, Inc
          sales agreement
            * conference call
            - prepare contract


   Well, you get the point - @i provides a filing system for your reminders with *index view* as the access point. 

## Adding @k (konnection) entries

As powerful as @i entries are for filing your reminders they are limited by the fact that, like a paper filing system, since each reminder can only have a single @i entry, you can only put a reminder in one folder . Well, you say, it is always possible to make a copy of a piece of paper and put the copy in another folder. @k (konnection) entries serve a similar purpose - they create links between reminders and you can put as many @k entries as you like in any particular reminder.

Let's begin with a simple example. ABC and Clair Smith are related - Clair is the sales contact for ABC - but this is only apparent in the *index view* and, even then, only by inspection: ABC is in the list of clients and Clair is in the list of contacts under ABC. Futhermore, the conference call event appears under ABC so there is a connection between the conference call and ABC as well. But suppose there is also a connection between the conference call and Clair who is, after all, the sales contact. How do we add that connection.  And how do we make all these connections more apparent?

Konnections are just what's needed. Let's go back and add @k konnections from ABC to Clair and from the conference call both to ABC and to Clair. Modify the ABC and conference call records as follows

    % ABC, Inc @i clients @k 123
    * conference call @s 2p fri @i ABC, Inc/sales agreement @k 27 @k 123 

  where 123 and 27 are the unique id's, respectively, for these records

    % Clair Smith - sales @i contacts/ABC, Inc
    % ABC, Inc @i clients

  Questions:
  * How did we obtain these unique ids?
      * The hard way would be to select each record in *etm*, press *enter* to show the details and then jot down the id displayed at the bottom of the details panel.
      * The easy way would be to select `% ABC...`, press *E* to edit the record, enter `@k ` at the end of the record and note that pop up completions are offered for every journal record which has an @i entry. Extend the entry to `@k co` and the list will shorten to ones that include 

            @k contacts/ABC, Inc % Clair Smith - sales: 123

        Acccepting this entry and saving it will drop everything from the @k through the colon to leave this as the saved journal entry

            % ABC, Inc @i clients @k 123

        A similar process when editing the conference call event and entering `@k cl` would pop up a list that includes

            @k clients % ABC, Inc: 27

  * What does adding these @k konnections to the records accomplish?
    * The `@k 123` in the first record directly links ABC to Clair. 
    * The `@k 27` and `@k 123` in the second record directly link the conference call both to the client ABC and to the contact Clair.

The display of these records now changes to reflect the presence of the connections so that *index* view now appears as 

        clients
          % ABC, Inc                      k
          % IOU, Ltd
        contacts
          ABC, Inc
            % Clair Smith - sales         k
            % Bill James - accounting
          IOU, Ltd
            % Hal Burns - CEO
        ABC, Inc
          sales agreement
            * conference call             k
            - prepare contract

The *k* appearing to the right of some of the original entries indicates that there are konnections either to or from these entries. Selecting an item with the *k* displayed and pressing 'k' opens the konnected view for that selection. Doing this with `% ABC...` selected would display this **konnected** view

        To the selection
          * conference call               k
        Selection
          % ABC, Inc                      k
        From the selection
          % Clair Smith - sales           k

Note that unlike *index* view, this is not a simple outline since there can be many branches both to and from the selection.

Now select `* conference call`, press `k` and the display changes to this *konnected* view

        Selection
          * conference call               k
        From the selection
          % Clair Smith - sales           k
          % ABC, Inc                      k

Similarly, selecting `% Clair Smith - sales` and pressing 'k' would give still a third *konnected* view


        To the selection
          * conference call               k
          % ABC, Inc                      k
        Selection
          % Clair Smith - sales           k

Tbe contents of these sections:

* To the selection
    * the list of all reminders whose @k entries contain the id of the selection
* Selection
    * the selected reminder
* From the selection
    * the list of reminders whose ids are among the @k entries of the selection 

In short, everything *konnected to the selection*, the *selection* itself, and everything *konnected from the selection*. 
