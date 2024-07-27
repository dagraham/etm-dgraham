import sys
import os
sys.path.append(os.path.dirname(__file__)) # for pytest
from item import Item, Instances
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, rruleset, rrulestr, DAILY
from dateutil.tz import gettz

json_entry = {
    "created": "{T}:20240712T1052",
    "itemtype": "*",
    "summary": "Thanksgiving",
    "s": "{T}:20101126T0500",
    "r": "RRULE:FREQ=MONTHLY;BYMONTH=11;BYDAY=+4THU",
    "modified": "{T}:20240712T1054"
}

string_entry = """\
DTSTART:20241028T133000
RRULE:FREQ=DAILY;COUNT=14
RRULE:FREQ=DAILY;INTERVAL=2;COUNT=7
RDATE:20241104T134500
RDATE:20241105T151500
EXDATE:20241104T133000
"""


def test_wkdays_to_rrule():
    rr = Instances()
    test_string = "mo, -1tu, +4fr, +1we , -3th, 2sa, +5su, 3xyz, -5mo, 0f"
    print(f"\ntesting: '{test_string}'")
    good_str, problem_str = rr.wkdays_to_rrule(test_string)
    print("good_str:", f"{good_str}")
    print(problem_str)
    assert(good_str == 'MO,-1TU,+4FR,+1WE,-3TH')
    assert(problem_str.split('\n')[0] == 'Problem entries: 2SA, +5SU, 3XYZ, -5MO, 0F')


def test_item_initialization():
    item = Item()
    partial_strings = [
        "",
        "- ",
        "- Thanksgiving ",
        "- Thanksgiving @",
        "- Thanksgiving @s 2010/11/",
        "- Thanksgiving @s 2010/11/26 ",
        "* Thanksgiving @s 2010/11/26 ",
        "* Thanksgiving @s 2010/11/26 @",
        "* Thanksgiving @s 2010/11/26 @r ",
        "* Thanksgiving @s 2010/11/26 @r y ",
        "* Thanksgiving @s 2010/11/26 @r y &",
        "* Thanksgiving @s 2010/11/26 @r y &M 11 ",
        "* Thanksgiving @s 2010/11/26 @r y &M 11 &w 4",
        "* Thanksgiving @s 2010/11/26 @r y &M 11 &w 4TH",
    ]

    print("\nparsing partial_strings")
    for s in partial_strings:
        print(f"\n\nprocessing: {s}")
        try:
            item.parse_input(s)
        except Exception as e:
            print(f"   {e = }")
    print("done with partial strings\n\n")
    print(f"{item.item = }")

    entry = "* carpe diem @s 2024/7/10 @r d"
    item = Item(entry)
    assert item.entry == entry
    assert item.tokens == [('*', 0, 1), ('carpe diem ', 2, 13), ('@s 2024/7/10 ', 13, 26), ('@r d', 26, 30)]

    item_from_json = Item(json_entry)
    entry = "* Thanksgiving @s 2010/11/26 @r y &M 11 &w 4TH"
    item_from_string = Item(entry)

    assert item_from_string.entry == entry
    assert item_from_string.tokens == [('*', 0, 1), ('Thanksgiving ', 2, 15), ('@s 2010/11/26 ', 15, 29), ('@r y ', 29, 34), ('&M 11', 34, 39), ('&w 4TH', 40, 46)]
    # print(f"{item_from_string.__dict__ = }")
    # print(f"{item_from_string.instances.__dict__ = }")

def test_repeat_from_rruleset():
    pacific = gettz('US/Pacific')
    mountain = gettz('America/Denver')
    central = gettz('US/Central')
    eastern = gettz('America/New_York')
    local = gettz()
    utc = gettz('UTC')
    naive = None

    tz = None
    # Define the start date

    rules_lst = []
    start_date = datetime(2024, 10, 28, 13, 30, tzinfo=tz)  # 0:30 on Mon Oct 28, 2024

    # Create a recurrence rule for daily events
    rule1 = rrule(freq=DAILY, dtstart=start_date, count=14)
    rules_lst.append(str(rule1))
    # Create another recurrence rule for specific days (e.g., every 2 days)
    rule2 = rrule(freq=DAILY, dtstart=start_date, interval=2, count=7)
    rules_lst.append(str(rule2))

    # Create an rruleset
    rules = rruleset()

    # Add the rules to the rruleset
    rules.rrule(rule1)
    rules.rrule(rule2)

    # Add a specific date to include
    plusdates = [datetime(2024, 11, 4, 13, 45, tzinfo=tz), datetime(2024, 11, 5, 15, 15, tzinfo=tz)]
    for dt in plusdates:
        rules.rdate(dt)
        rules_lst.append(dt.strftime("RDATE:%Y%m%dT%H%M%S"))
    # Add a specific date to exclude
    minusdates = [datetime(2024, 11, 4, 13, 30, tzinfo=tz),]
    for dt in minusdates:
        rules.exdate(dt)
        rules_lst.append(dt.strftime("EXDATE:%Y%m%dT%H%M%S"))

    # Generate the occurrences of the event
    # occurrences = list(rules)

    # start_date = datetime(2024, 10, 28, 13, 30).astimezone()
    rr = Instances(rules)
    # rr.set_startdt(start_date)
    # rr.add_rule(rhsh)
    occurrences = list(rr.ruleset)
    for occurrence in occurrences:
        print(occurrence.strftime("  %a %Y-%m-%d %H:%M %Z %z"))


def test_repeat_from_instance():
    pacific = gettz('US/Pacific')
    mountain = gettz('America/Denver')
    central = gettz('US/Central')
    eastern = gettz('America/New_York')
    local = gettz()
    utc = gettz('UTC')
    naive = None

    rr = Instances()
    tz = eastern
    # Define the start date

    start_date = datetime(2024, 10, 28, 13, 30, tzinfo=tz)  # 0:30 on Mon Oct 28, 2024
    rr.set_startdt(start_date)
    print(f"start_date: {rr.startdt}")

    rhsh = {'r': 'd', 'i': 3}
    rr.add_rule(rhsh)
    # occurrences = list(rr.ruleset)
    # for occurrence in occurrences:
    #     print(occurrence.strftime("  %a %Y-%m-%d %H:%M %Z %z"))


test_item_initialization()
test_wkdays_to_rrule()
test_repeat_from_rruleset()
test_repeat_from_instance()