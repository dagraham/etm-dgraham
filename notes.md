# Notes for etm
**Last modified: Fri Dec 21, 2018 04:21PM EST**

# TOC
<!-- vim-markdown-toc GFM -->

* [ToDo](#todo)
    * [Coding](#coding)
    * [Writing](#writing)
    * [States and Transitions](#states-and-transitions)

<!-- vim-markdown-toc -->

# ToDo

## Coding

* Foundation
    * Incorporate RDict and use for index view
    * View class for view_pt
    * Logging
    * Timing
* To use
    * Create new item
    * Edit exiting item
        * Which instance dialog
    * Finish
    * Alarms
* Whenever
    * Tools
        * Schedule new
        * Reschedule
    * Views
        * index
        * next 
        * tags
        * Query

## Writing

* README -> Getting Started

## States and Transitions

* items (agenda - other views similar but without busy toggle)
    * selection -> (a:busy, enter:details, e:edit, f1:help)
    * no selection -> f1:help

* busy -> a:items 

* help -> f1:items

* details -> (e:edit, enter:items, f1:help)

* edit selected
    * repeating
        * yes -> which
            * instances chosen -> editing
            * cancel -> items
        * no -> editing
* editing
    * check -> editing
    * save -> items
    * cancel -> items
