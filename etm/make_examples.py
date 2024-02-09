#! /usr/bin/env python3
import random
import lorem
from dateutil import rrule as dr
from datetime import datetime, timedelta
import sys
import os
import time

from dateutil.parser import parse

# from etm.model import parse

num_items = 180

ONEDAY = timedelta(days=1)
ONEWK = 7 * ONEDAY

# rrule components
tmp = []
while len(tmp) < 8:
    _ = lorem.sentence().split(' ')[0]
    if _ not in tmp:
        tmp.append(_)

names = []
for i in range(0, 8, 2):
    names.append(f'{tmp[i]}, {tmp[i+1]}')


def phrase():
    # for the summary
    # drop the ending period
    s = lorem.sentence()[:-1]
    num = random.choice([3, 4, 5])
    words = s.split(' ')[:num]
    return ' '.join(words).rstrip()


def word():
    return lorem.sentence()[:-1].split(' ')[0]


def note_time():
    hour = random.choice(range(6, 18))
    minute = random.choice(range(0, 60))
    return f'{hour:02}:{minute:02}'


def days_or_weeks():
    return random.choice(['d', 'w'])


freq = [
    '@r w',
    '@r w &w MO, WE, FR',
    '@r w &i 2',
    '@r d',
    '@r d &i 2',
    '@r d &i 3',
]
stop = [f'&c {n}' for n in range(2, 5)] + [
    f'&u +{n}{days_or_weeks()}' for n in range(2, 5)
]


def cnt():
    return f"@+ {random.choice(['+', '-'])}{random.choice([1, 3, 5])}d, {random.choice(['+', '-'])}{random.choice([2, 4, 6])}d"


def beg():
    return f"@s -{random.choice([1,2,3,4])}{random.choice(['d', 'w'])}"


client_index = '$clients'
info_index = '$client info'
client_detail = f"""
Because of the index entry, all client records will be grouped under "{client_index}", then under the name of the relevant client in both index and journal view.  This infomation record will be first among the items for each client since beginning with a "{info_index}" will put it at the top of the sorting order for the index entries for each client. Having such a journal entry for each client ensures that the client name will be available for completion of the index entry when other client related items are being created. The choice of "{client_index}" and "{info_index}" is, of course, arbitrary but takes advantage of the sorting order that begins with "!", "#", "$" and "%".
"""


def week(dt: datetime) -> [datetime, datetime]:
    y, w, d = dt.isocalendar()
    wk_beg = dt - (d - 1) * ONEDAY if d > 1 else dt
    wk_end = dt + (7 - d) * ONEDAY if d < 7 else dt
    return wk_beg.date(), wk_end.date()


def make_examples(egfile: str = None, num_items: int = num_items, last_id=0):
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    num_konnections = 0
    num_items = int(num_items)
    # include 12 weeks: 6 previous, the current and the following 5
    wkbeg, wkend = week(now)
    months = num_items // 200
    start = wkbeg - 6 * 7 * ONEDAY
    until = wkend + (5 * 7) * ONEDAY

    datetimes = list(
        dr.rrule(
            dr.DAILY,
            byweekday=range(7),
            byhour=range(6, 22),
            byminute=range(0, 60, 15),
            dtstart=start,
            until=until,
        )
    )
    past_datetimes = [x for x in datetimes if x <= now]

    alerts = [f'@a {random.choice([0, 15, 30])}m: d' for x in range(10)]

    types = ['-', '*', '%']
    clients = ['A', 'B', 'C', 'D']
    client_name = {
        'A': names[0],
        'B': names[1],
        'C': names[2],
        'D': names[3],
    }
    projects = {
        'A': ['project a1', 'project a2'],
        'B': ['project b1', 'project b2', 'project b3'],
        'C': ['project c1', 'project c2'],
        'D': ['project d1'],
        'E': ['project e1', 'project e2', 'project e3'],
    }
    # activities = {
    #     'A': ['activity a1', 'activity a2'],
    #     'B': ['activity b1', 'activity b2', 'activity b3'],
    #     'C': ['activity c1', 'activity c2'],
    #     'D': ['activity d1'],
    #     'E': ['activity e1', 'activity e2', 'activity e3'],
    # }
    locations = ['errands', 'home', 'office', 'shop']
    tags = ['red', 'green', 'blue']
    dates = [0, 0, 0, 1, 0, 0, 0]   # dates 1/7 of the time
    minutes = range(15, 110, 5)   # for used times (test rounding)
    # days = range(7)
    extent = [x for x in range(30, 210, 15)]

    # client_contacts = {}
    # client_id = {}
    examples = []

    for i in range(4):
        examples.append(
            f'- {phrase()} {beg()} {random.choice(freq)} {random.choice(stop)} {cnt()} @t lorem'
        )

    for client in clients:
        summary = f'{client_name[client]}'
        d = f'contact details for {client_name[client]} go here. {client_detail}'
        i = f'{client_index}/{client_name[client]}/{info_index}'
        examples.append(f'% {summary} @i {i} @d {d} @t lorem')

    examples.append(
        f"""\
! README @t lorem @d .
1) This inbox item and each of the other {num_items+len(examples)} internally generated reminders is tagged 'lorem'. All of them can be removed in one step by opening query view (press 'q'), entering the query 'any t lorem | remove' and pressing 'return'.
2). The examples are generated to fit within a period including the week they were generated together with 5 subsequent and 6 previous weeks. You can remove and regenerate them whenever you like to keep them current.\
"""
    )

    daily = []

    while len(examples) < num_items:
        # for _ in range(num_items):
        t = random.choice(types)
        summary = phrase()
        start = random.choice(datetimes)
        end = random.choice(datetimes)
        date = random.choice(dates)
        s = (
            start.strftime('%Y-%m-%d')
            if date
            else start.strftime('%Y-%m-%d %I:%M%p')
        )
        end = (
            end.strftime('%Y-%m-%d')
            if date
            else start.strftime('%Y-%m-%d %I:%M%p')
        )
        d = lorem.sentence()
        i0 = random.choice(clients)
        i1 = client_name[i0]
        i2 = random.choice(projects[i0])
        # i3 = random.choice(activities[i1])
        begin = random.choice(range(1, 15))
        used = ''
        # konnect = random.choice(konnections) if konnections and random.randint(1, 10) <= 4 else ""
        for i in range(random.randint(1, 2)):
            u = random.choice(minutes)
            if random.choice(dates):
                e = start.strftime('%Y-%m-%d')
            else:
                e = (start + timedelta(minutes=u)).strftime('%Y-%m-%d %I:%M%p')
            if start < now:
                used += f'@u {u}m: {e} '

        if t == '%' and start <= now:
            summary = start.strftime('%Y-%m-%d')
            if summary not in daily:
                daily.append(summary)
                description = start.strftime('%A, %B %-d %Y')
                examples.append(
                    f'{t} {summary} @i #daily @t lorem @d {description}\n\n* {note_time()}\n  - {phrase()}'
                )

        elif t == '*':
            if date:      # an event
                examples.append(
                    f'{t} {summary} @s {s} @t {random.choice(tags)} @t lorem'
                )
            else:
                x = random.choice(extent)
                c = random.choice([0, 0, 1])
                if c:
                    a = random.choice(alerts)
                else:
                    a = ''
                examples.append(
                    f'{t} {summary} @s {s} @e {x}m {a} @i {client_index}/{i1}/{i2} {used} @d {d} @t {random.choice(tags)} @t lorem'
                )
        elif t == '-':
            if start < now - 2 * ONEWK:
                f = f' @f {s} -> {end} '
                examples.append(
                    f'{t} {summary} @s {s} @i {client_index}/{i1}/{i2} {f}{used} @d {d} @t lorem'
                )
            elif start < now:
                f = (
                    f' @f {s} -> {end} '
                    if random.choice(['h', 't']) == 't'
                    else ''
                )
                examples.append(
                    f'{t} {summary} @s {s} @i {client_index}/{i1}/{i2} {f}{used} @d {d} @t lorem'
                )

            else:
                examples.append(
                    f'{t} {summary} @s {s} @i {client_index}/{i1}/{i2} @d {d} @b {begin} @t lorem'
                )

        else:
            examples.append(
                f'{t} {summary} @i {client_index}/{i1}/{i2} @d {d} @l {random.choice(locations)} @t {random.choice(tags)} @t lorem'
            )

    # # adding @k won't work since update hsh requires that the id exist
    indices = [x for x in range(last_id, last_id + len(examples))]
    parents = random.choices(indices, k=40)
    children = random.choices(indices, k=40)
    for p in parents:
        n = random.choice([x for x in range(3, 8)])
        samp = random.choices(children, k=n)
        entry = ' '.join([f'@k {x}' for x in samp if x != p])
        examples[p - last_id] += f' {entry}'

    if egfile:
        with open(egfile, 'w') as fo:
            fo.writelines('\n'.join(examples))
    return examples


if __name__ == '__main__':
    if len(sys.argv) > 2:
        egfile = sys.argv.pop(1)
        num_items = sys.argv.pop(1)
    elif len(sys.argv) > 1:
        egfile = sys.argv.pop(1)
    else:
        egfile = None

    res = make_examples(egfile, num_items)
    for _ in res:
        print(_)
