# tests/test_item.py
from etm.new_model import Item, Repeat
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, rruleset, DAILY, rrulestr, MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import gettz

json_entry = {
    "created": "{T}:20240712T1052",
    "itemtype": "*",
    "summary": "Thanksgiving",
    "s": "{T}:20101126T0500",
    "r": [
        {
            "r": "y",
            "M": [11],
            "w": ["{W}:4TH"]
        }
    ],
    "modified": "{T}:20240712T1054"
}

def test_wkdays_to_rrule():
    rr = Repeat()
    test_string = "MO, -1TU, 4FR, 1WE, -3TH, 2SA, 5SU, XYZ, -5MO"
    rep, good, bad = rr.wkdays_to_rrule(test_string)
    assert(good == ['MO', '-1TU', '4FR', '1WE', '-3TH', '2SA'])
    assert(bad == ['5SU', 'XYZ', '-5MO'])
    assert(rep == [MO, TU(-1), FR(+4), WE(+1), TH(-3), SA(+2)])
    

def test_item_initialization():
    item = Item(input_string="* carpe diem @s 2024/7/10 @r d")
    assert item.itemtype == "*"
    assert item.summary == "carpe diem"
    assert item.start.strftime("%Y/%m/%d") == "2024/07/10"

    item_from_json = Item(json_dict=json_entry)
    item_from_string = Item(input_string="* Thanksgiving @s 2010/11/26 @r y &M 11 &w 4TH")
    assert item_from_json.summary == item_from_string.summary
    
def test_repeat_from_rruleset():
    pacific = gettz('US/Pacific')
    mountain = gettz('America/Denver')
    central = gettz('US/Central')
    eastern = gettz('America/New_York')
    local = gettz()
    utc = gettz('UTC')
    naive = None

    tz = eastern
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
    rr = Repeat(rules)
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

    rr = Repeat()
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
        

    
test_wkdays_to_rrule()
test_repeat_from_rruleset()
test_repeat_from_instance()