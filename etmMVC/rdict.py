#! /usr/bin/env python3
from model import TimeIt
from model import setup_logging
from collections import namedtuple

"""
Handle lists of path and value tuples and their conversion to tree structurs.
List format:

    (path1.path2. ... pathN, (typecode, summary, detail, uid))

Tree format:

    path1 -> path2 -> ... -> pathN -> [(typecode, summary, detail, uid)]

Examples
Agenda: year -> week -> day -> [(typecode, summary, times, uid)]
Index: path[0] -> path[1] -> ... -> (typecode, summary, datetime, uid)
"""

# FIXME
Instance = namedtuple('Instance', ['path', 'type', 'summary', 'time', 'calendar', 'uid'])
Item = namedtuple('Item', ['path', 'type', 'summary', 'relevant', 'created', 'modified', 'location', 'calendar', 'uid'])

class RDict(dict):
    tab = 3 * " "

    def __missing__(self, key):
            self[key] = RDict()
            return self[key]

    def add(self, tkeys, values=()):
        i = 0
        keys = tkeys.split('.')
        for key in keys:
            i = i + 1
            if i == len(keys):
                self.setdefault(key, []).append(values)
            self = self[key]

    def as_tree(self, t = None, depth = 0):
        """ print a tree """
        if t is None:
            t = self
        for k in t.keys():
            print("%s%s" % (depth * RDict.tab,  k))
            depth += 1
            if type(t[k]) == RDict:
                self.as_tree(t[k], depth)
            else:
                for v in t[k]:
                    print("%s%s" % (depth * RDict.tab, v))
            depth -= 1

import bisect
class SList(list):
    """
    List of lists. Compoents have the format: period delimited path string, tuple ending with uid. 
    """

    def add(self, path_tuple, values_tuple):
        """
        Use bisect to preserve order
        """
        bisect.insort(self, ('.'.join(path_tuple), values_tuple))

    def remove(self, uid):
        _len = len(self)
        tmp = [x for x in self if x[1][-1] != uid]
        print('removed: {} rows for {}'.format(_len - len(tmp), uid))
        self[:] = tmp

if __name__ == '__main__':

    from random import randint, choice
    from pprint import pprint

    # sample data
    types = [
            ['*', 'event', 'time'],
            ['-', 'task', 'due'],
            ['%', 'record', 'date'],
            ['!', 'inbox', ''],
            ]
    items = []
    uids = []
    for i in range(100):
        u = randint(100, 1000)
        items.append(tuple(choice(types) + [str(u)]))

    data = SList()
    for y in range(2016, 2019):
        year = "{}".format(y)
        for w in range(1, randint(5, 9)):
            week = "{:>2}".format(randint(1, 53))
            for d in range(1, randint(2, 6)):
                day = "{}".format(randint(0, 6))
                for j in range(1, randint(2, 5)):
                    item = choice(items)
                    uids.append(item[-1])
                    data.add((year, week, day), item)

    print()
    print("starting data:", len(data), "items")
    for i in range(4):
        uid = choice(uids)
        data.remove(uid)

    print()
    print("data as list:", len(data), "items")
    pprint(data)

    # create recursive dict from data
    index = RDict()
    for path, value in data:
        # add(index, path, value)
        index.add(path, value)

    print("\ndata as recursive dictionary")
    pprint(index)

    print("\ndata as tree")
    index.as_tree()

# starting data: 125 items
# removed: 3 rows for 824
# removed: 1 rows for 413
# removed: 3 rows for 602
# removed: 2 rows for 224

# data as list: 116 items
# [('2016. 4.2', ('!', 'inbox', '', '225')),
#  ('2016. 4.2', ('-', 'task', 'due', '345')),
#  ('2016. 4.2', ('-', 'task', 'due', '823')),
#  ('2016. 4.5', ('!', 'inbox', '', '282')),
#  ('2016.19.0', ('!', 'inbox', '', '403')),
#  ('2016.19.0', ('%', 'record', 'date', '762')),
#  ('2016.19.0', ('-', 'task', 'due', '815')),
#  ('2016.19.2', ('!', 'inbox', '', '880')),
#  ('2016.19.2', ('%', 'record', 'date', '446')),
#  ('2016.19.2', ('%', 'record', 'date', '892')),
#  ('2016.19.3', ('-', 'task', 'due', '204')),
#  ('2016.19.4', ('%', 'record', 'date', '282')),
#  ('2016.19.4', ('*', 'event', 'time', '963')),
#  ('2016.39.0', ('%', 'record', 'date', '592')),
#  ('2016.39.0', ('-', 'task', 'due', '988')),
#  ('2016.43.1', ('*', 'event', 'time', '237')),
#  ('2016.43.1', ('-', 'task', 'due', '204')),
#  ('2016.43.1', ('-', 'task', 'due', '397')),
#  ('2016.43.1', ('-', 'task', 'due', '670')),
#  ('2016.43.4', ('!', 'inbox', '', '568')),
#  ('2016.43.4', ('*', 'event', 'time', '963')),
#  ('2016.43.4', ('-', 'task', 'due', '823')),
#  ('2016.43.5', ('!', 'inbox', '', '688')),
#  ('2016.43.5', ('%', 'record', 'date', '198')),
#  ('2016.43.5', ('%', 'record', 'date', '905')),
#  ('2016.43.5', ('*', 'event', 'time', '257')),
#  ('2016.52.2', ('!', 'inbox', '', '219')),
#  ('2016.52.2', ('!', 'inbox', '', '688')),
#  ('2016.52.2', ('-', 'task', 'due', '646')),
#  ('2016.52.2', ('-', 'task', 'due', '815')),
#  ('2016.52.3', ('!', 'inbox', '', '257')),
#  ('2016.52.3', ('!', 'inbox', '', '880')),
#  ('2016.52.3', ('!', 'inbox', '', '880')),
#  ('2016.52.3', ('*', 'event', 'time', '257')),
#  ('2016.52.5', ('!', 'inbox', '', '850')),
#  ('2016.52.5', ('*', 'event', 'time', '728')),
#  ('2016.52.5', ('*', 'event', 'time', '754')),
#  ('2016.52.5', ('*', 'event', 'time', '963')),
#  ('2017. 3.1', ('*', 'event', 'time', '542')),
#  ('2017. 3.1', ('-', 'task', 'due', '345')),
#  ('2017. 3.1', ('-', 'task', 'due', '397')),
#  ('2017. 3.1', ('-', 'task', 'due', '918')),
#  ('2017. 3.2', ('!', 'inbox', '', '282')),
#  ('2017. 3.2', ('%', 'record', 'date', '666')),
#  ('2017. 3.2', ('*', 'event', 'time', '237')),
#  ('2017. 3.3', ('!', 'inbox', '', '593')),
#  ('2017. 3.3', ('%', 'record', 'date', '892')),
#  ('2017.24.0', ('*', 'event', 'time', '237')),
#  ('2017.24.0', ('-', 'task', 'due', '459')),
#  ('2017.47.3', ('!', 'inbox', '', '515')),
#  ('2017.47.3', ('%', 'record', 'date', '170')),
#  ('2017.47.3', ('-', 'task', 'due', '257')),
#  ('2017.47.4', ('!', 'inbox', '', '127')),
#  ('2017.47.4', ('*', 'event', 'time', '175')),
#  ('2017.47.4', ('-', 'task', 'due', '397')),
#  ('2017.47.6', ('!', 'inbox', '', '153')),
#  ('2017.47.6', ('*', 'event', 'time', '522')),
#  ('2017.49.4', ('!', 'inbox', '', '384')),
#  ('2017.49.4', ('!', 'inbox', '', '700')),
#  ('2017.49.4', ('!', 'inbox', '', '944')),
#  ('2017.49.4', ('%', 'record', 'date', '482')),
#  ('2018. 4.1', ('!', 'inbox', '', '540')),
#  ('2018. 4.1', ('*', 'event', 'time', '522')),
#  ('2018.11.0', ('*', 'event', 'time', '237')),
#  ('2018.11.1', ('!', 'inbox', '', '619')),
#  ('2018.11.1', ('-', 'task', 'due', '204')),
#  ('2018.11.2', ('%', 'record', 'date', '762')),
#  ('2018.11.2', ('*', 'event', 'time', '754')),
#  ('2018.11.2', ('-', 'task', 'due', '385')),
#  ('2018.11.3', ('!', 'inbox', '', '219')),
#  ('2018.11.3', ('%', 'record', 'date', '386')),
#  ('2018.11.3', ('%', 'record', 'date', '762')),
#  ('2018.11.3', ('%', 'record', 'date', '969')),
#  ('2018.11.3', ('*', 'event', 'time', '542')),
#  ('2018.11.3', ('-', 'task', 'due', '385')),
#  ('2018.11.4', ('*', 'event', 'time', '257')),
#  ('2018.11.4', ('-', 'task', 'due', '340')),
#  ('2018.11.4', ('-', 'task', 'due', '397')),
#  ('2018.11.6', ('!', 'inbox', '', '700')),
#  ('2018.11.6', ('!', 'inbox', '', '880')),
#  ('2018.11.6', ('%', 'record', 'date', '482')),
#  ('2018.11.6', ('*', 'event', 'time', '257')),
#  ('2018.13.2', ('%', 'record', 'date', '198')),
#  ('2018.13.2', ('%', 'record', 'date', '446')),
#  ('2018.13.2', ('*', 'event', 'time', '518')),
#  ('2018.13.2', ('*', 'event', 'time', '795')),
#  ('2018.13.2', ('-', 'task', 'due', '815')),
#  ('2018.15.0', ('%', 'record', 'date', '137')),
#  ('2018.15.0', ('*', 'event', 'time', '744')),
#  ('2018.15.1', ('!', 'inbox', '', '282')),
#  ('2018.15.1', ('!', 'inbox', '', '944')),
#  ('2018.15.1', ('*', 'event', 'time', '963')),
#  ('2018.15.1', ('-', 'task', 'due', '257')),
#  ('2018.15.3', ('!', 'inbox', '', '777')),
#  ('2018.15.3', ('-', 'task', 'due', '646')),
#  ('2018.15.3', ('-', 'task', 'due', '646')),
#  ('2018.20.5', ('*', 'event', 'time', '237')),
#  ('2018.30.4', ('%', 'record', 'date', '110')),
#  ('2018.30.5', ('!', 'inbox', '', '225')),
#  ('2018.30.5', ('%', 'record', 'date', '170')),
#  ('2018.30.5', ('*', 'event', 'time', '257')),
#  ('2018.30.5', ('*', 'event', 'time', '522')),
#  ('2018.51.1', ('-', 'task', 'due', '279')),
#  ('2018.51.2', ('!', 'inbox', '', '153')),
#  ('2018.51.2', ('!', 'inbox', '', '257')),
#  ('2018.51.2', ('!', 'inbox', '', '384')),
#  ('2018.51.2', ('*', 'event', 'time', '744')),
#  ('2018.51.4', ('!', 'inbox', '', '219')),
#  ('2018.51.4', ('!', 'inbox', '', '568')),
#  ('2018.51.4', ('-', 'task', 'due', '345')),
#  ('2018.51.4', ('-', 'task', 'due', '452')),
#  ('2018.51.4', ('-', 'task', 'due', '642')),
#  ('2018.51.4', ('-', 'task', 'due', '642')),
#  ('2018.51.5', ('!', 'inbox', '', '619')),
#  ('2018.51.5', ('%', 'record', 'date', '892')),
#  ('2018.51.5', ('-', 'task', 'due', '823'))]

# data as recursive dictionary
# {'2016': {' 4': {'2': [('!', 'inbox', '', '225'),
#                        ('-', 'task', 'due', '345'),
#                        ('-', 'task', 'due', '823')],
#                  '5': [('!', 'inbox', '', '282')]},
#           '19': {'0': [('!', 'inbox', '', '403'),
#                        ('%', 'record', 'date', '762'),
#                        ('-', 'task', 'due', '815')],
#                  '2': [('!', 'inbox', '', '880'),
#                        ('%', 'record', 'date', '446'),
#                        ('%', 'record', 'date', '892')],
#                  '3': [('-', 'task', 'due', '204')],
#                  '4': [('%', 'record', 'date', '282'),
#                        ('*', 'event', 'time', '963')]},
#           '39': {'0': [('%', 'record', 'date', '592'),
#                        ('-', 'task', 'due', '988')]},
#           '43': {'1': [('*', 'event', 'time', '237'),
#                        ('-', 'task', 'due', '204'),
#                        ('-', 'task', 'due', '397'),
#                        ('-', 'task', 'due', '670')],
#                  '4': [('!', 'inbox', '', '568'),
#                        ('*', 'event', 'time', '963'),
#                        ('-', 'task', 'due', '823')],
#                  '5': [('!', 'inbox', '', '688'),
#                        ('%', 'record', 'date', '198'),
#                        ('%', 'record', 'date', '905'),
#                        ('*', 'event', 'time', '257')]},
#           '52': {'2': [('!', 'inbox', '', '219'),
#                        ('!', 'inbox', '', '688'),
#                        ('-', 'task', 'due', '646'),
#                        ('-', 'task', 'due', '815')],
#                  '3': [('!', 'inbox', '', '257'),
#                        ('!', 'inbox', '', '880'),
#                        ('!', 'inbox', '', '880'),
#                        ('*', 'event', 'time', '257')],
#                  '5': [('!', 'inbox', '', '850'),
#                        ('*', 'event', 'time', '728'),
#                        ('*', 'event', 'time', '754'),
#                        ('*', 'event', 'time', '963')]}},
#  '2017': {' 3': {'1': [('*', 'event', 'time', '542'),
#                        ('-', 'task', 'due', '345'),
#                        ('-', 'task', 'due', '397'),
#                        ('-', 'task', 'due', '918')],
#                  '2': [('!', 'inbox', '', '282'),
#                        ('%', 'record', 'date', '666'),
#                        ('*', 'event', 'time', '237')],
#                  '3': [('!', 'inbox', '', '593'),
#                        ('%', 'record', 'date', '892')]},
#           '24': {'0': [('*', 'event', 'time', '237'),
#                        ('-', 'task', 'due', '459')]},
#           '47': {'3': [('!', 'inbox', '', '515'),
#                        ('%', 'record', 'date', '170'),
#                        ('-', 'task', 'due', '257')],
#                  '4': [('!', 'inbox', '', '127'),
#                        ('*', 'event', 'time', '175'),
#                        ('-', 'task', 'due', '397')],
#                  '6': [('!', 'inbox', '', '153'),
#                        ('*', 'event', 'time', '522')]},
#           '49': {'4': [('!', 'inbox', '', '384'),
#                        ('!', 'inbox', '', '700'),
#                        ('!', 'inbox', '', '944'),
#                        ('%', 'record', 'date', '482')]}},
#  '2018': {' 4': {'1': [('!', 'inbox', '', '540'),
#                        ('*', 'event', 'time', '522')]},
#           '11': {'0': [('*', 'event', 'time', '237')],
#                  '1': [('!', 'inbox', '', '619'), ('-', 'task', 'due', '204')],
#                  '2': [('%', 'record', 'date', '762'),
#                        ('*', 'event', 'time', '754'),
#                        ('-', 'task', 'due', '385')],
#                  '3': [('!', 'inbox', '', '219'),
#                        ('%', 'record', 'date', '386'),
#                        ('%', 'record', 'date', '762'),
#                        ('%', 'record', 'date', '969'),
#                        ('*', 'event', 'time', '542'),
#                        ('-', 'task', 'due', '385')],
#                  '4': [('*', 'event', 'time', '257'),
#                        ('-', 'task', 'due', '340'),
#                        ('-', 'task', 'due', '397')],
#                  '6': [('!', 'inbox', '', '700'),
#                        ('!', 'inbox', '', '880'),
#                        ('%', 'record', 'date', '482'),
#                        ('*', 'event', 'time', '257')]},
#           '13': {'2': [('%', 'record', 'date', '198'),
#                        ('%', 'record', 'date', '446'),
#                        ('*', 'event', 'time', '518'),
#                        ('*', 'event', 'time', '795'),
#                        ('-', 'task', 'due', '815')]},
#           '15': {'0': [('%', 'record', 'date', '137'),
#                        ('*', 'event', 'time', '744')],
#                  '1': [('!', 'inbox', '', '282'),
#                        ('!', 'inbox', '', '944'),
#                        ('*', 'event', 'time', '963'),
#                        ('-', 'task', 'due', '257')],
#                  '3': [('!', 'inbox', '', '777'),
#                        ('-', 'task', 'due', '646'),
#                        ('-', 'task', 'due', '646')]},
#           '20': {'5': [('*', 'event', 'time', '237')]},
#           '30': {'4': [('%', 'record', 'date', '110')],
#                  '5': [('!', 'inbox', '', '225'),
#                        ('%', 'record', 'date', '170'),
#                        ('*', 'event', 'time', '257'),
#                        ('*', 'event', 'time', '522')]},
#           '51': {'1': [('-', 'task', 'due', '279')],
#                  '2': [('!', 'inbox', '', '153'),
#                        ('!', 'inbox', '', '257'),
#                        ('!', 'inbox', '', '384'),
#                        ('*', 'event', 'time', '744')],
#                  '4': [('!', 'inbox', '', '219'),
#                        ('!', 'inbox', '', '568'),
#                        ('-', 'task', 'due', '345'),
#                        ('-', 'task', 'due', '452'),
#                        ('-', 'task', 'due', '642'),
#                        ('-', 'task', 'due', '642')],
#                  '5': [('!', 'inbox', '', '619'),
#                        ('%', 'record', 'date', '892'),
#                        ('-', 'task', 'due', '823')]}}}

# data as tree
# 2016
#     4
#       2
#          ('!', 'inbox', '', '225')
#          ('-', 'task', 'due', '345')
#          ('-', 'task', 'due', '823')
#       5
#          ('!', 'inbox', '', '282')
#    19
#       0
#          ('!', 'inbox', '', '403')
#          ('%', 'record', 'date', '762')
#          ('-', 'task', 'due', '815')
#       2
#          ('!', 'inbox', '', '880')
#          ('%', 'record', 'date', '446')
#          ('%', 'record', 'date', '892')
#       3
#          ('-', 'task', 'due', '204')
#       4
#          ('%', 'record', 'date', '282')
#          ('*', 'event', 'time', '963')
#    39
#       0
#          ('%', 'record', 'date', '592')
#          ('-', 'task', 'due', '988')
#    43
#       1
#          ('*', 'event', 'time', '237')
#          ('-', 'task', 'due', '204')
#          ('-', 'task', 'due', '397')
#          ('-', 'task', 'due', '670')
#       4
#          ('!', 'inbox', '', '568')
#          ('*', 'event', 'time', '963')
#          ('-', 'task', 'due', '823')
#       5
#          ('!', 'inbox', '', '688')
#          ('%', 'record', 'date', '198')
#          ('%', 'record', 'date', '905')
#          ('*', 'event', 'time', '257')
#    52
#       2
#          ('!', 'inbox', '', '219')
#          ('!', 'inbox', '', '688')
#          ('-', 'task', 'due', '646')
#          ('-', 'task', 'due', '815')
#       3
#          ('!', 'inbox', '', '257')
#          ('!', 'inbox', '', '880')
#          ('!', 'inbox', '', '880')
#          ('*', 'event', 'time', '257')
#       5
#          ('!', 'inbox', '', '850')
#          ('*', 'event', 'time', '728')
#          ('*', 'event', 'time', '754')
#          ('*', 'event', 'time', '963')
# 2017
#     3
#       1
#          ('*', 'event', 'time', '542')
#          ('-', 'task', 'due', '345')
#          ('-', 'task', 'due', '397')
#          ('-', 'task', 'due', '918')
#       2
#          ('!', 'inbox', '', '282')
#          ('%', 'record', 'date', '666')
#          ('*', 'event', 'time', '237')
#       3
#          ('!', 'inbox', '', '593')
#          ('%', 'record', 'date', '892')
#    24
#       0
#          ('*', 'event', 'time', '237')
#          ('-', 'task', 'due', '459')
#    47
#       3
#          ('!', 'inbox', '', '515')
#          ('%', 'record', 'date', '170')
#          ('-', 'task', 'due', '257')
#       4
#          ('!', 'inbox', '', '127')
#          ('*', 'event', 'time', '175')
#          ('-', 'task', 'due', '397')
#       6
#          ('!', 'inbox', '', '153')
#          ('*', 'event', 'time', '522')
#    49
#       4
#          ('!', 'inbox', '', '384')
#          ('!', 'inbox', '', '700')
#          ('!', 'inbox', '', '944')
#          ('%', 'record', 'date', '482')
# 2018
#     4
#       1
#          ('!', 'inbox', '', '540')
#          ('*', 'event', 'time', '522')
#    11
#       0
#          ('*', 'event', 'time', '237')
#       1
#          ('!', 'inbox', '', '619')
#          ('-', 'task', 'due', '204')
#       2
#          ('%', 'record', 'date', '762')
#          ('*', 'event', 'time', '754')
#          ('-', 'task', 'due', '385')
#       3
#          ('!', 'inbox', '', '219')
#          ('%', 'record', 'date', '386')
#          ('%', 'record', 'date', '762')
#          ('%', 'record', 'date', '969')
#          ('*', 'event', 'time', '542')
#          ('-', 'task', 'due', '385')
#       4
#          ('*', 'event', 'time', '257')
#          ('-', 'task', 'due', '340')
#          ('-', 'task', 'due', '397')
#       6
#          ('!', 'inbox', '', '700')
#          ('!', 'inbox', '', '880')
#          ('%', 'record', 'date', '482')
#          ('*', 'event', 'time', '257')
#    13
#       2
#          ('%', 'record', 'date', '198')
#          ('%', 'record', 'date', '446')
#          ('*', 'event', 'time', '518')
#          ('*', 'event', 'time', '795')
#          ('-', 'task', 'due', '815')
#    15
#       0
#          ('%', 'record', 'date', '137')
#          ('*', 'event', 'time', '744')
#       1
#          ('!', 'inbox', '', '282')
#          ('!', 'inbox', '', '944')
#          ('*', 'event', 'time', '963')
#          ('-', 'task', 'due', '257')
#       3
#          ('!', 'inbox', '', '777')
#          ('-', 'task', 'due', '646')
#          ('-', 'task', 'due', '646')
#    20
#       5
#          ('*', 'event', 'time', '237')
#    30
#       4
#          ('%', 'record', 'date', '110')
#       5
#          ('!', 'inbox', '', '225')
#          ('%', 'record', 'date', '170')
#          ('*', 'event', 'time', '257')
#          ('*', 'event', 'time', '522')
#    51
#       1
#          ('-', 'task', 'due', '279')
#       2
#          ('!', 'inbox', '', '153')
#          ('!', 'inbox', '', '257')
#          ('!', 'inbox', '', '384')
#          ('*', 'event', 'time', '744')
#       4
#          ('!', 'inbox', '', '219')
#          ('!', 'inbox', '', '568')
#          ('-', 'task', 'due', '345')
#          ('-', 'task', 'due', '452')
#          ('-', 'task', 'due', '642')
#          ('-', 'task', 'due', '642')
#       5
#          ('!', 'inbox', '', '619')
#          ('%', 'record', 'date', '892')
#          ('-', 'task', 'due', '823')