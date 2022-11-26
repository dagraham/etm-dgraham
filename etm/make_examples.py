#!/usr/bin/python3
import random
import lorem
from dateutil.rrule import *
from datetime import *
import pendulum
import sys, os

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

def make_examples(egfile=None):
    num_items = 300
    num_konnections = 0
    # include 3 months - the previous, current and next months
    start = parse('9a 1') - pendulum.duration(months=1)
    until = parse('9a 1') + pendulum.duration(months=2) - pendulum.duration(days=1)
    now = parse('9a') - pendulum.duration(days=7)

    datetimes = list(rrule(DAILY, byweekday=range(7), byhour=range(6, 22), dtstart=start, until=until))

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
    dates = [0, 0, 1, 0, 0] # dates 1/5 of the time
    minutes = range(12, 96, 6) # for used times
    days = range(7)
    extent = range(60, 180, 30)

    client_contacts = {}
    client_id = {}
    examples = []

    examples.append("! the lorem examples @t lorem @d 1) This inbox item and each of the other internally generated reminders is tagged 'lorem'. All of them can be removed in one step by opening query view (press 'q'), entering the query 'any t lorem | remove' and pressing 'return'. 2). The examples are generated to fit within a three month period including the month they were generated together with the previous and subsequent months. You can remove and regenerate them whenever you like to keep them current.")

    # for client in clients:
    #     # client records
    #     num_contacts = random.randint(1, 4)
    #     client_contacts[client] = contact_ids
    #     # add links from client to contacts
    #     for i in range(len(contact_ids)):
    #         doc_id += 1
    #         # add contact records
    #         examples.append(f"% contact {client}{i+1} @i contact/client {client} @d {lorem.sentence()[:-1]} @t lorem")
    #     doc_id += 1
    #     client_id[client] = doc_id
    #     if num_konnections:
    #         # add clients with links from client to contacts
    #         tmp = ' '.join([f'@k {x}' for x in contact_ids])
    #     else:
    #         tmp = ''
    #     examples.append(f"% client {client} @i clients @d {lorem.sentence()[:-1]} {tmp} @t lorem")

    # konnections = []
    # if num_konnections:
    #     for _ in range(num_konnections):
    #         client = random.choice(clients)
    #         num_contacts = random.randint(1, len(client_contacts[client]))
    #         # examples.append(client_contacts, num_contacts)
    #         contacts = random.sample(client_contacts[client], k=num_contacts)
    #         contacts.sort()
    #         tmp = ' '.join([f'@k {x}' for x in contacts])

    #         konnections.append(f"@k {client_id[client]} {tmp}")

    for _ in range(num_items):
        t = random.choice(types)
        summary = phrase()
        start = random.choice(datetimes)
        date = random.choice(dates)
        s = start.strftime("%Y-%m-%d") if date else start.strftime("%Y-%m-%d %I:%M%p")
        d = lorem.paragraph()
        i1 = random.choice(clients)
        i2 = random.choice(projects[i1])
        i3 = random.choice(activities[i1])
        begin = random.choice(range(1, 15))
        used = ""
        # konnect = random.choice(konnections) if konnections and random.randint(1, 10) <= 4 else ""
        for i in range(random.randint(1,2)):
            u = random.choice(minutes)
            if random.choice(dates):
                e = start.strftime("%Y-%m-%d")
            else:
                e = (start + pendulum.duration(minutes=u)).strftime("%Y-%m-%d %I:%M%p")
            used += f"@u {u}m: {e} "

        if t == '*':
            if date:      # an event
                examples.append(f"{t} {summary} @s {s} @t {random.choice(tags)} @t lorem")
            else:
                x = random.choice(extent)
                examples.append(f"{t} {summary} @s {s} @e {x}m @i client {i1}/{i2}/{i3} {used} @d {d} @t {random.choice(tags)} @t lorem")
        elif t == '-' and random.choice(['h', 't']) == 'h':
            if start < now:
                examples.append(f"{t} {summary} @s {s} @i client {i1}/{i2}/{i3} @f {s} {used} @d {d} @t lorem")
            else:
                examples.append(f"{t} {summary} @s {s} @i client {i1}/{i2}/{i3} {used} @d {d} @b {begin} @t lorem")

        else:
            examples.append(f"{t} {summary} @i client {i1}/{i2}/{i3} {used} @d {d} @l {random.choice(locations)} @t {random.choice(tags)} @t lorem")

    if egfile:
        with open(egfile, 'w') as fo:
            fo.writelines("\n".join(examples))
    else:
        return examples

if __name__ == '__main__':
    if len(sys.argv) > 1:
        egfile = sys.argv.pop(1)
    else:
        egfile = None
    make_examples(egfile)

