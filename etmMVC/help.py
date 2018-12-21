#!/usr/bin/env python3
from model import wrap
import textwrap

logo = [
    "                          ",
    " █████╗██████╗███╗   ███╗ ",
    " ██╔══╝╚═██╔═╝████╗ ████║ ",
    " ███╗    ██║  ██╔████╔██║ ",
    " ██╔╝    ██║  ██║╚██╔╝██║ ",
    " █████╗  ██║  ██║ ╚═╝ ██║ ",
    " ╚════╝  ╚═╝  ╚═╝     ╚═╝ ",
]


menu1 = [
    #------------------ ------------------ ------------------#
    "-- VIEWS -----------------------------------------------",
    "a: agenda/busy     h: history         i: index          ",
    "n: next            t: tags            q: query          ",
    "           F1: toggle displaying help                   ",
    ]

menu2 = [
    #------------------ ------------------ ------------------#
    "-- SELECTED ITEM ---------------------------------------",
    "C: copy            F: finish          I: export ical    ",
    "D: delete          R: reschedule      L: open link      ",
    "E: edit            S: schedule new    T: start timer    ",
    "      ENTER: toggle displaying item details             ",
    ]

menu3 = [
    #------------------ ------------------ ------------------#
    "-- TOOLS -----------------------------------------------",
    "A: show alerts     P: preferences     F2: date calc     ",
    "J: jump to date    Q: query           F3: yearly        ",
    "N: create new item V: view as text    F8: quit          ",
]

menu_text = "The key bindings for the various commands are listed above. E.g., press 'a' to open agenda view. In agenda view, pressing 'a' toggles between displaying the schedule and busy views. Pressing 'right' or 'left', respectively, changes to the subsequent or previous week and presssing 'space' changes to the current week." 


def show_help():
    width = 58
    output = []
    for item in [logo, menu1, menu2, menu3]:
        for line in item:
            output.append(line.center(width, ' ') + "\n")
        output.append('\n')
    return "".join(output) + textwrap.fill(menu_text, width)


if __name__ == '__main__':
    print(show_help())

