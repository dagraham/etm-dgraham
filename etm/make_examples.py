#! /usr/bin/env python3
import random
import lorem
from dateutil.rrule import *
from datetime import *
import pendulum
import sys, os

num_items = 800

def parse(s, **kwd):
    return pendulum.parse(s, strict=False, **kwd)

def phrase(minlen=24):
    # drop the ending period
    s = lorem.sentence()[:-1]
    tmp = ""
    words = s.split(' ')
    while words and len(tmp) < minlen:
        tmp += f"{words.pop(0)} "

    return tmp.strip()

def make_examples(egfile=None, num_items=num_items):
    num_konnections = 0
    num_items = int(num_items)
    # if make_many include 8 months - 6 previous, current and following months
    # else 4 months - 2 previous, current and following months
    months = num_items//200
    start = parse('9a 1') - pendulum.duration(months=months)
    until = parse('9a 1') + pendulum.duration(months=2) - pendulum.duration(days=1)
    # now = parse('9a Sun') - pendulum.duration(days=6)
    now = parse('8a')

    datetimes = list(rrule(DAILY, byweekday=range(7), byhour=range(6, 22), dtstart=start, until=until))
    past_datetimes = [x for x in datetimes if x <= now]

    types = ['-', '*', '%', '-']
    # clients = ['A', 'B', 'C', 'D', 'E']
    clients = ['A', 'B', 'C']
    projects = {
            'A': ['project a1', 'project a2'],
            'B': ['project b1', 'project b2', 'project b3'],
            'C': ['project c1', 'project c2'],
            'D': ['project d1'],
            'E': ['project e1', 'project e2', 'project e3'],
            }
    activities = {
            'A': ['activity a1', 'activity a2'],
            'B': ['activity b1', 'activity b2', 'activity b3'],
            'C': ['activity c1', 'activity c2'],
            'D': ['activity d1'],
            'E': ['activity e1', 'activity e2', 'activity e3'],
            }
    locations = ['errands', 'home', 'office', 'shop']
    tags = ['red', 'green', 'blue']
    dates = [0, 0, 0, 1, 0, 0, 0] # dates 1/7 of the time
    minutes = range(12, 96, 6) # for used times
    days = range(7)
    extent = [x for x in range(30, 210, 15)]

    client_contacts = {}
    client_id = {}
    examples = []

    examples.append(f"! the lorem examples @t lorem @d 1) This inbox item and each of the other {num_items} internally generated reminders is tagged 'lorem'. All of them can be removed in one step by opening query view (press 'q'), entering the query 'any t lorem | remove' and pressing 'return'. 2). The examples are generated to fit within a period including the month they were generated together with one subsequent and {months} previous months. You can remove and regenerate them whenever you like to keep them current.")


    for _ in range(num_items):
        t = random.choice(types)
        summary = phrase()
        start = random.choice(datetimes)
        end = random.choice(datetimes)
        date = random.choice(dates)
        s = start.strftime("%Y-%m-%d") if date else start.strftime("%Y-%m-%d %I:%M%p")
        end = end.strftime("%Y-%m-%d") if date else start.strftime("%Y-%m-%d %I:%M%p")
        d = lorem.paragraph()
        i1 = random.choice(clients)
        i2 = random.choice(projects[i1])
        # i3 = random.choice(activities[i1])
        begin = random.choice(range(1, 15))
        used = ""
        # konnect = random.choice(konnections) if konnections and random.randint(1, 10) <= 4 else ""
        for i in range(random.randint(1,2)):
            u = random.choice(minutes)
            if random.choice(dates):
                e = start.strftime("%Y-%m-%d")
            else:
                e = (start + pendulum.duration(minutes=u)).strftime("%Y-%m-%d %I:%M%p")
            if start < now:
                used += f"@u {u}m: {e} "

        if t == '*':
            if date:      # an event
                examples.append(f"{t} {summary} @s {s} @t {random.choice(tags)} @t lorem")
            else:
                x = random.choice(extent)
                examples.append(f"{t} {summary} @s {s} @e {x}m @i client {i1}/{i2} {used} @d {d} @t {random.choice(tags)} @t lorem")
        elif t == '-' and random.choice(['h', 't']) == 'h':
            if start < now:

                f = f" @f {s} -> {end} " if random.choice(['h', 't']) == 't' else ""
                examples.append(f"{t} {summary} @s {s} @i client {i1}/{i2} {f}{used} @d {d} @t lorem")
            else:
                examples.append(f"{t} {summary} @s {s} @i client {i1}/{i2} @d {d} @b {begin} @t lorem")

        else:
            examples.append(f"{t} {summary} @i client {i1}/{i2} @d {d} @l {random.choice(locations)} @t {random.choice(tags)} @t lorem")

    if egfile:
        with open(egfile, 'w') as fo:
            fo.writelines("\n".join(examples))
    else:
        return examples

if __name__ == '__main__':
    if len(sys.argv) > 2:
        egfile = sys.argv.pop(1)
        numitems = sys.argv.pop(1)
    elif len(sys.argv) > 1:
        egfile = sys.argv.pop(1)
        numitems = num_items
    else:
        egfile = None
    make_examples(egfile, numitems)

