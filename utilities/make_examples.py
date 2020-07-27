#!/usr/bin/python3
import random
import lorem
from dateutil.rrule import *
from datetime import *
import pendulum

def parse(s, **kwd):
    # logger.debug(f"parse: {s} {kwd}")
    return pendulum.parse(s, strict=False, **kwd)

num_items = 160
num_konnections = 40
start = parse('9a 1') - pendulum.duration(months=2)
until = parse('9a 1') + pendulum.duration(months=3)
now = parse('9a') - pendulum.duration(days=7)

def phrase(minlen=24):
    # drop the ending period
    s = lorem.sentence()[:-1]
    tmp = ""
    words = s.split(' ')
    while words and len(tmp) < minlen:
        tmp += f"{words.pop(0)} "

    return tmp.strip()

datetimes = list(rrule(DAILY, byweekday=range(7), byhour=range(8, 20), dtstart=start, until=until))

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
minutes = range(10, 90, 6)
days = range(7)
extent = range(30, 120, 30)

client_contacts = {}
client_id = {}
doc_id = 0
for client in clients:
    # client records
    num_contacts = random.randint(1, 4)
    contact_ids = [x for x in range(doc_id + 1, doc_id + 1 + num_contacts)]
    client_contacts[client] = contact_ids
    # add links from client to contacts
    for i in range(len(contact_ids)):
        doc_id += 1
        # add contact records
        print(f"% contact {client}{i+1} @i contact/client {client} @d {lorem.sentence()[:-1]}")
    doc_id += 1
    client_id[client] = doc_id
    # add clients with links from client to contacts
    tmp = ' '.join([f'@k {x}' for x in contact_ids])
    print(f"% client {client} @i clients @d {lorem.sentence()[:-1]} {tmp}")

konnections = []
for _ in range(num_konnections):
    client = random.choice(clients)
    num_contacts = random.randint(1, len(client_contacts[client]))
    # print(client_contacts, num_contacts)
    contacts = random.sample(client_contacts[client], k=num_contacts)
    contacts.sort()
    tmp = ' '.join([f'@k {x}' for x in contacts])

    konnections.append(f"@k {client_id[client]} {tmp}")



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
    used = ""
    konnect = random.choice(konnections) if random.randint(1, 10) <= 4 else ""
    for i in range(random.randint(1,2)):
        u = random.choice(minutes)
        if random.choice(dates):
            e = start.strftime("%Y-%m-%d")
        else:
            e = (start + pendulum.duration(minutes=u)).strftime("%Y-%m-%d %I:%M%p")
        used += f"@u {u}m: {e} "

    if t == '*':
        if date:      # an event
            print(f"{t} {summary} @s {s} @t {random.choice(tags)} {konnect}")
        else:
            x = random.choice(minutes)
            print(f"{t} {summary} @s {s} @e {x}m @i client {i1}/{i2}/{i3} {used} @d {d} @t {random.choice(tags)} {konnect}")
    elif t == '-' and random.choice(['h', 't']) == 'h':
        if start < now:
            print(f"{t} {summary} @s {s} @i client {i1}/{i2}/{i3} @f {s} {used} @d {d} {konnect}")
        else:
            print(f"{t} {summary} @s {s} @i client {i1}/{i2}/{i3} {used} @d {d} @b 21 {konnect}")

    else:
        print(f"{t} {summary} @i client {i1}/{i2}/{i3} {used} @d {d} @l {random.choice(locations)} @t {random.choice(tags)}")


