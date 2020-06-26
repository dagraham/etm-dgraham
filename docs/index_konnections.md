# Organizating with Index and Konnection
## Preliminary and incomplete

Here is a possible use case for organizing relevant reminders based on their  index (@i), and konnection[^kon] (@k), entries.  

[^kon]: Please forgive the spelling. It is meant to suggest *connection* but the letter *k* is available for use in *etm*, while *c* is not. Konnection entries are available for *etm >= 4.6.0*.

Imagine a business situation in which your clients are sometimes companies who will be billed for services rendered. The clients who are companies may have employees who are your actual contacts. Clients who are individuals would have no employees and are themselves the contacts. Also, with each client you may have repeated transactions that will be called projects.

For the purposes of this example, I will use names such as *Client A*, *Client B*, *Employee A1* and so forth to clarify the type of entry while in actual practice you would be using their actual names, *ABC, Inc*, *John Smith*, and so forth.

## Organization steps
1. Create `%` reminders (records) for each client and relevant employee. 

        % Client A @i clients
        % Employee A1 @i employees/Client A
        % Employee A2 @i employees/Client A
        % Client B @i clients
        % Employee B1 @i employees/Client A
        % Employee B2 @i employees/Client A
        % Employee B3 @i employees/Client A
        ...
    Think of the `@i` entries as putting the record into the specified folder. E.g. the second entry puts the 'Employee A1' record in the folder `employees/Client A`.

    While creating these entries you may want to add useful information to the records. E.g., `@n` entries with the relevant phone numbers. Once entered, they will not only be easily retrieved but they will also be available for auto completion when creating other entries.[^atn] Another example would be an `@g` entry with the URL for the client's website. A final example would be an `@d` entry with any client/employee specific information. Of course, such additions can always be made later.

[^atn]: If you use entries such as  `@n John Smith: 123 456-7890`, the when recording an `@n` in another reminder, typing `@n j` will limit the completions to those starting with `j` and will display the full matching names and numbers.

2. Add *konnections* from the clients to their employees, if any. You can now use auto completion to add konnections from the clients to the employees. For example, select `% Client A` in, say, *index view* and press `E` to open it for editing. Move to the end of the entry and type `@k` followed by a space. The available completions will include `employees/Client A % Employee A1: id` where `id` is the unique identifier of the record. The id will be an integer, say `967`. Selecting this from the completions will give the entry

        % Client A @i Client A @k employees/Client A % Employee A1: 967
    When this reminder is saved, only the integer id will be retained to establish the konnection from Client A to the employee whose id is 967:

        % Client A @i Client A @k 967

## Workflow steps

Now suppose you have a transaction with *Client A* that will be called *Project A1*. As with the other illustrative names, in actual use something more suggestive such as *Probate will* could be used. 

1. A task for this project could be created as:

        - task 1 @i Client A/Project A1 
    Now enter `@k` followed by a space and, from the completions choose `@k clients/Client A % Client A: 966` where 966 is the id of Client A. This gives

        - task 1 @i Client A/Project A1 @k Client A % Client A: 966
    which, when saved, becomes

        - task 1 @i Client A/Project A1 @k 966
    thus establishing a konnection between task 1 and Client A. Now suppose that Employee A2 is the relevant contact person for this task. Edit the task, append another @k and select `Client A/employees/Employee A2 % Employee A2: 968` where 968 is the id of Employee A2. After saving this gives:

        - task 1 @i Client A/Project A1 @k 966 @k 968
    so that task 1 is konnected both to Client A (id 966) and to Employee A1 (id 968).

