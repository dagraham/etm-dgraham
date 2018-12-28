#! /usr/bin/env python3
from model import TimeIt
from model import setup_logging
from collections import namedtuple

"""
Handle lists of path and value tuples and their conversion to tree structurs.
List format:

    ((path1, path2, ... pathN), (typecode, summary, detail, uid))

Tree format:

    path1 -> path2 -> ... -> pathN -> [(typecode, summary, detail, uid)]

Examples
Agenda: year -> week -> day -> [(typecode, summary, times, uid)]
Index: path[0] -> path[1] -> ... -> (typecode, summary, datetime, uid)
"""

# TODO
Instance = namedtuple('Instance', ['path', 'type', 'summary', 'time', 'calendar', 'uid'])
Item = namedtuple('Item', ['path', 'type', 'summary', 'relevant', 'created', 'modified', 'location', 'calendar', 'uid'])

class RDict(dict):
    tab = 3 * " "

    def __missing__(self, key):
            self[key] = RDict()
            self.rows = []
            self.num2id = {}
            return self[key]

    def add(self, keys, values=()):
        i = 0
        for key in keys:
            i = i + 1
            if i == len(keys):
                self.setdefault(key, []).append(values)
            self = self[key]

    def as_tree(self, t = None, depth = 0):
        """ return a tree as row tuples """
        if t is None:
            t = self
        for k in t.keys():
            # self.rows.append("%s%s" % (depth * RDict.tab,  k))
            self.rows.append((depth * RDict.tab,  k))
            depth += 1
            if type(t[k]) == RDict:
                self.as_tree(t=t[k], depth=depth)
            else:
                for v in t[k]:
                    self.rows.append((depth * RDict.tab, v))
            depth -= 1

    def tree_as_string(self, width):
        self.as_tree()
        num = -1
        num2id = {}
        output = []
        for row in self.rows:
            num += 1
            indent = row[0]
            if isinstance(row[-1], tuple):
                summary_width = width - len(indent) - 18 
                num2id[num] = row[-1][-1]
                item_type, summary, rhc = row[1][:-1]
                summary = summary.ljust(summary_width, ' ')
                rhc = rhc.center(16, ' ')
                output.append(f"{indent}{item_type} {summary}{rhc}")
            else:
                output.append(f"{row[0]}{row[1]}")

        return "\n".join(output), num2id

import bisect
class SList(list):
    """
    List of lists. Compoents have the format: sort tuple, tuple of path components, 4 tuple of (type char, summary, rhc, uid). 
    """

    def add(self, sort_tuple, path_tuple, values_tuple):
        """
        Use bisect to preserve order
        """
        bisect.insort(self, (sort_tuple, path_tuple, values_tuple))

    def remove(self, uid):
        _len = len(self)
        tmp = [x for x in self if x[2][-1] != uid]
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
            ['<', 'pastdue', 'days'],
            ['>', 'soon', 'days'],
            ]
    sort_order = {
            '!': 0,
            '<': 1,
            '>': 2,
            '*': 3,
            '-': 3,
            '%': 3,
            }
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
                    h = randint(0, 23)
                    sort_tup = (year, week, day, sort_order[item[0]], h)
                    data.add(sort_tup, (year, week, day), item)

    print()
    print("starting data:", len(data), "items")
    for i in range(4):
        uid = choice(uids)
        data.remove(uid)


    sample_uids = []
    for i in range(4):
        sample_uids.append(choice(uids))

    print()
    print("data as list for uids:", sample_uids)
    # pprint([[x for x in data if x[2][-1] == str(y)] for y in sample_uids])
    pprint([[x for x in data if str(y) in x[2]] for y in sample_uids])


    # print()
    # print("data as list:", len(data), "items")
    # pprint(data)

    # create recursive dict from data
    index = RDict()
    for sort, path, value in data:
        # add(index, path, value)
        index.add(path, value)

    print("\ndata as recursive dictionary")
    pprint(index)

    print("\ndata as tree")
    output, num2id = index.tree_as_string(58)
    print(output)
    pprint(num2id)

"""
starting data: 142 items
removed: 2 rows for 649
removed: 3 rows for 462
removed: 3 rows for 346
removed: 2 rows for 471

data as list: 132 items
[(('2016', ' 5', '0', 2, 8), ('2016', ' 5', '0'), ('>', 'soon', 'days', '735')),
 (('2016', ' 5', '0', 3, 3),
  ('2016', ' 5', '0'),
  ('%', 'record', 'date', '490')),
 (('2016', ' 5', '0', 3, 4),
  ('2016', ' 5', '0'),
  ('*', 'event', 'time', '903')),
 (('2016', ' 5', '0', 3, 13),
  ('2016', ' 5', '0'),
  ('*', 'event', 'time', '903')),
 (('2016', ' 5', '0', 3, 17),
  ('2016', ' 5', '0'),
  ('%', 'record', 'date', '114')),
 (('2016', ' 5', '0', 3, 20),
  ('2016', ' 5', '0'),
  ('*', 'event', 'time', '642')),
 (('2016', ' 5', '2', 3, 5), ('2016', ' 5', '2'), ('-', 'task', 'due', '917')),
 (('2016', ' 5', '2', 3, 13),
  ('2016', ' 5', '2'),
  ('*', 'event', 'time', '747')),
 (('2016', ' 5', '4', 2, 6), ('2016', ' 5', '4'), ('>', 'soon', 'days', '167')),
 (('2016', ' 5', '4', 3, 12), ('2016', ' 5', '4'), ('-', 'task', 'due', '257')),
 (('2016', ' 5', '5', 1, 0),
  ('2016', ' 5', '5'),
  ('<', 'pastdue', 'days', '360')),
 (('2016', ' 5', '5', 3, 8),
  ('2016', ' 5', '5'),
  ('%', 'record', 'date', '287')),
 (('2016', ' 5', '5', 3, 23),
  ('2016', ' 5', '5'),
  ('%', 'record', 'date', '570')),
 (('2016', '11', '0', 0, 11), ('2016', '11', '0'), ('!', 'inbox', '', '340')),
 (('2016', '11', '0', 0, 15), ('2016', '11', '0'), ('!', 'inbox', '', '301')),
 (('2016', '11', '0', 0, 17), ('2016', '11', '0'), ('!', 'inbox', '', '390')),
 (('2016', '11', '0', 0, 18), ('2016', '11', '0'), ('!', 'inbox', '', '418')),
 (('2016', '11', '0', 1, 3),
  ('2016', '11', '0'),
  ('<', 'pastdue', 'days', '876')),
 (('2016', '11', '0', 1, 16),
  ('2016', '11', '0'),
  ('<', 'pastdue', 'days', '642')),
 (('2016', '11', '0', 2, 3), ('2016', '11', '0'), ('>', 'soon', 'days', '650')),
 (('2016', '11', '0', 3, 3),
  ('2016', '11', '0'),
  ('*', 'event', 'time', '747')),
 (('2016', '11', '0', 3, 9), ('2016', '11', '0'), ('-', 'task', 'due', '544')),
 (('2016', '11', '0', 3, 15),
  ('2016', '11', '0'),
  ('%', 'record', 'date', '162')),
 (('2016', '11', '0', 3, 15), ('2016', '11', '0'), ('-', 'task', 'due', '269')),
 (('2016', '11', '0', 3, 22),
  ('2016', '11', '0'),
  ('*', 'event', 'time', '287')),
 (('2016', '11', '2', 1, 16),
  ('2016', '11', '2'),
  ('<', 'pastdue', 'days', '698')),
 (('2016', '11', '2', 2, 12),
  ('2016', '11', '2'),
  ('>', 'soon', 'days', '934')),
 (('2016', '11', '3', 1, 9),
  ('2016', '11', '3'),
  ('<', 'pastdue', 'days', '881')),
 (('2016', '15', '0', 1, 8),
  ('2016', '15', '0'),
  ('<', 'pastdue', 'days', '466')),
 (('2016', '15', '0', 3, 8), ('2016', '15', '0'), ('-', 'task', 'due', '625')),
 (('2016', '15', '1', 0, 14), ('2016', '15', '1'), ('!', 'inbox', '', '747')),
 (('2016', '15', '1', 3, 8), ('2016', '15', '1'), ('-', 'task', 'due', '257')),
 (('2016', '15', '1', 3, 9),
  ('2016', '15', '1'),
  ('%', 'record', 'date', '196')),
 (('2016', '15', '1', 3, 20), ('2016', '15', '1'), ('-', 'task', 'due', '605')),
 (('2016', '15', '1', 3, 21), ('2016', '15', '1'), ('-', 'task', 'due', '354')),
 (('2016', '30', '4', 3, 9),
  ('2016', '30', '4'),
  ('*', 'event', 'time', '409')),
 (('2016', '30', '5', 3, 22),
  ('2016', '30', '5'),
  ('%', 'record', 'date', '385')),
 (('2016', '37', '1', 1, 17),
  ('2016', '37', '1'),
  ('<', 'pastdue', 'days', '289')),
 (('2016', '37', '2', 3, 1), ('2016', '37', '2'), ('-', 'task', 'due', '849')),
 (('2016', '37', '5', 3, 14),
  ('2016', '37', '5'),
  ('*', 'event', 'time', '431')),
 (('2016', '42', '0', 0, 21), ('2016', '42', '0'), ('!', 'inbox', '', '886')),
 (('2016', '42', '0', 2, 18),
  ('2016', '42', '0'),
  ('>', 'soon', 'days', '851')),
 (('2016', '42', '0', 3, 3), ('2016', '42', '0'), ('-', 'task', 'due', '605')),
 (('2016', '42', '0', 3, 10), ('2016', '42', '0'), ('-', 'task', 'due', '626')),
 (('2016', '42', '1', 0, 11), ('2016', '42', '1'), ('!', 'inbox', '', '756')),
 (('2016', '42', '1', 1, 3),
  ('2016', '42', '1'),
  ('<', 'pastdue', 'days', '876')),
 (('2016', '42', '1', 3, 1), ('2016', '42', '1'), ('-', 'task', 'due', '849')),
 (('2016', '42', '2', 0, 18), ('2016', '42', '2'), ('!', 'inbox', '', '220')),
 (('2016', '42', '2', 2, 1), ('2016', '42', '2'), ('>', 'soon', 'days', '506')),
 (('2016', '42', '4', 3, 11), ('2016', '42', '4'), ('-', 'task', 'due', '838')),
 (('2016', '42', '5', 0, 14), ('2016', '42', '5'), ('!', 'inbox', '', '108')),
 (('2016', '42', '5', 1, 18),
  ('2016', '42', '5'),
  ('<', 'pastdue', 'days', '910')),
 (('2016', '42', '5', 3, 15),
  ('2016', '42', '5'),
  ('%', 'record', 'date', '490')),
 (('2016', '43', '0', 0, 12), ('2016', '43', '0'), ('!', 'inbox', '', '756')),
 (('2016', '43', '0', 0, 17), ('2016', '43', '0'), ('!', 'inbox', '', '418')),
 (('2016', '43', '0', 1, 4),
  ('2016', '43', '0'),
  ('<', 'pastdue', 'days', '360')),
 (('2016', '43', '0', 2, 14),
  ('2016', '43', '0'),
  ('>', 'soon', 'days', '206')),
 (('2016', '43', '5', 1, 0),
  ('2016', '43', '5'),
  ('<', 'pastdue', 'days', '722')),
 (('2016', '43', '5', 2, 14),
  ('2016', '43', '5'),
  ('>', 'soon', 'days', '626')),
 (('2016', '43', '5', 3, 9),
  ('2016', '43', '5'),
  ('*', 'event', 'time', '903')),
 (('2016', '43', '5', 3, 17), ('2016', '43', '5'), ('-', 'task', 'due', '451')),
 (('2016', '43', '6', 0, 8), ('2016', '43', '6'), ('!', 'inbox', '', '475')),
 (('2016', '43', '6', 1, 21),
  ('2016', '43', '6'),
  ('<', 'pastdue', 'days', '466')),
 (('2016', '43', '6', 2, 10),
  ('2016', '43', '6'),
  ('>', 'soon', 'days', '905')),
 (('2016', '43', '6', 3, 10),
  ('2016', '43', '6'),
  ('%', 'record', 'date', '162')),
 (('2017', '19', '6', 0, 6), ('2017', '19', '6'), ('!', 'inbox', '', '340')),
 (('2017', '19', '6', 1, 17),
  ('2017', '19', '6'),
  ('<', 'pastdue', 'days', '910')),
 (('2017', '19', '6', 3, 10),
  ('2017', '19', '6'),
  ('%', 'record', 'date', '419')),
 (('2017', '19', '6', 3, 16),
  ('2017', '19', '6'),
  ('%', 'record', 'date', '141')),
 (('2017', '21', '2', 0, 8), ('2017', '21', '2'), ('!', 'inbox', '', '301')),
 (('2017', '21', '2', 2, 18),
  ('2017', '21', '2'),
  ('>', 'soon', 'days', '854')),
 (('2017', '21', '2', 3, 13), ('2017', '21', '2'), ('-', 'task', 'due', '849')),
 (('2017', '21', '2', 3, 21),
  ('2017', '21', '2'),
  ('%', 'record', 'date', '490')),
 (('2017', '21', '4', 0, 8), ('2017', '21', '4'), ('!', 'inbox', '', '957')),
 (('2017', '21', '4', 0, 19), ('2017', '21', '4'), ('!', 'inbox', '', '108')),
 (('2017', '21', '4', 1, 4),
  ('2017', '21', '4'),
  ('<', 'pastdue', 'days', '942')),
 (('2017', '21', '6', 0, 18), ('2017', '21', '6'), ('!', 'inbox', '', '747')),
 (('2017', '21', '6', 1, 3),
  ('2017', '21', '6'),
  ('<', 'pastdue', 'days', '698')),
 (('2017', '21', '6', 1, 5),
  ('2017', '21', '6'),
  ('<', 'pastdue', 'days', '698')),
 (('2017', '30', '0', 2, 3), ('2017', '30', '0'), ('>', 'soon', 'days', '854')),
 (('2017', '30', '0', 3, 20),
  ('2017', '30', '0'),
  ('%', 'record', 'date', '287')),
 (('2017', '30', '0', 3, 21),
  ('2017', '30', '0'),
  ('%', 'record', 'date', '288')),
 (('2017', '30', '1', 0, 0), ('2017', '30', '1'), ('!', 'inbox', '', '108')),
 (('2017', '30', '1', 0, 19), ('2017', '30', '1'), ('!', 'inbox', '', '340')),
 (('2017', '30', '1', 1, 1),
  ('2017', '30', '1'),
  ('<', 'pastdue', 'days', '360')),
 (('2017', '30', '1', 1, 1),
  ('2017', '30', '1'),
  ('<', 'pastdue', 'days', '876')),
 (('2017', '30', '2', 2, 7), ('2017', '30', '2'), ('>', 'soon', 'days', '650')),
 (('2017', '30', '2', 2, 9), ('2017', '30', '2'), ('>', 'soon', 'days', '905')),
 (('2017', '30', '2', 3, 6),
  ('2017', '30', '2'),
  ('*', 'event', 'time', '287')),
 (('2017', '30', '2', 3, 18),
  ('2017', '30', '2'),
  ('%', 'record', 'date', '162')),
 (('2017', '49', '3', 2, 10),
  ('2017', '49', '3'),
  ('>', 'soon', 'days', '513')),
 (('2017', '49', '3', 3, 14),
  ('2017', '49', '3'),
  ('%', 'record', 'date', '352')),
 (('2017', '53', '0', 0, 3), ('2017', '53', '0'), ('!', 'inbox', '', '559')),
 (('2017', '53', '0', 1, 14),
  ('2017', '53', '0'),
  ('<', 'pastdue', 'days', '942')),
 (('2017', '53', '0', 2, 6), ('2017', '53', '0'), ('>', 'soon', 'days', '513')),
 (('2017', '53', '0', 2, 9), ('2017', '53', '0'), ('>', 'soon', 'days', '111')),
 (('2017', '53', '0', 3, 16),
  ('2017', '53', '0'),
  ('%', 'record', 'date', '419')),
 (('2017', '53', '0', 3, 17), ('2017', '53', '0'), ('-', 'task', 'due', '269')),
 (('2017', '53', '6', 1, 1),
  ('2017', '53', '6'),
  ('<', 'pastdue', 'days', '636')),
 (('2017', '53', '6', 3, 12),
  ('2017', '53', '6'),
  ('%', 'record', 'date', '114')),
 (('2017', '53', '6', 3, 20),
  ('2017', '53', '6'),
  ('*', 'event', 'time', '355')),
 (('2017', '53', '6', 3, 20), ('2017', '53', '6'), ('-', 'task', 'due', '917')),
 (('2018', ' 1', '2', 1, 6),
  ('2018', ' 1', '2'),
  ('<', 'pastdue', 'days', '360')),
 (('2018', ' 1', '2', 2, 22),
  ('2018', ' 1', '2'),
  ('>', 'soon', 'days', '206')),
 (('2018', ' 1', '4', 1, 5),
  ('2018', ' 1', '4'),
  ('<', 'pastdue', 'days', '642')),
 (('2018', ' 1', '4', 2, 14),
  ('2018', ' 1', '4'),
  ('>', 'soon', 'days', '167')),
 (('2018', ' 1', '4', 3, 19),
  ('2018', ' 1', '4'),
  ('%', 'record', 'date', '141')),
 (('2018', ' 1', '4', 3, 20),
  ('2018', ' 1', '4'),
  ('*', 'event', 'time', '431')),
 (('2018', ' 6', '0', 1, 5),
  ('2018', ' 6', '0'),
  ('<', 'pastdue', 'days', '289')),
 (('2018', ' 6', '0', 2, 10),
  ('2018', ' 6', '0'),
  ('>', 'soon', 'days', '167')),
 (('2018', ' 6', '0', 3, 19), ('2018', ' 6', '0'), ('-', 'task', 'due', '298')),
 (('2018', ' 6', '1', 1, 10),
  ('2018', ' 6', '1'),
  ('<', 'pastdue', 'days', '722')),
 (('2018', ' 6', '1', 3, 1), ('2018', ' 6', '1'), ('-', 'task', 'due', '605')),
 (('2018', ' 6', '1', 3, 23), ('2018', ' 6', '1'), ('-', 'task', 'due', '605')),
 (('2018', ' 6', '4', 0, 9), ('2018', ' 6', '4'), ('!', 'inbox', '', '886')),
 (('2018', ' 6', '4', 3, 3),
  ('2018', ' 6', '4'),
  ('%', 'record', 'date', '385')),
 (('2018', ' 6', '4', 3, 4),
  ('2018', ' 6', '4'),
  ('%', 'record', 'date', '490')),
 (('2018', ' 6', '4', 3, 7),
  ('2018', ' 6', '4'),
  ('*', 'event', 'time', '287')),
 (('2018', '21', '0', 0, 0), ('2018', '21', '0'), ('!', 'inbox', '', '747')),
 (('2018', '21', '0', 2, 14),
  ('2018', '21', '0'),
  ('>', 'soon', 'days', '513')),
 (('2018', '21', '0', 3, 5), ('2018', '21', '0'), ('-', 'task', 'due', '425')),
 (('2018', '21', '0', 3, 23), ('2018', '21', '0'), ('-', 'task', 'due', '625')),
 (('2018', '21', '3', 0, 8), ('2018', '21', '3'), ('!', 'inbox', '', '714')),
 (('2018', '21', '3', 1, 16),
  ('2018', '21', '3'),
  ('<', 'pastdue', 'days', '881')),
 (('2018', '21', '3', 2, 8), ('2018', '21', '3'), ('>', 'soon', 'days', '905')),
 (('2018', '21', '3', 3, 11),
  ('2018', '21', '3'),
  ('%', 'record', 'date', '162')),
 (('2018', '21', '6', 0, 22), ('2018', '21', '6'), ('!', 'inbox', '', '390')),
 (('2018', '21', '6', 2, 7), ('2018', '21', '6'), ('>', 'soon', 'days', '905')),
 (('2018', '30', '4', 3, 5), ('2018', '30', '4'), ('-', 'task', 'due', '838')),
 (('2018', '40', '5', 1, 13),
  ('2018', '40', '5'),
  ('<', 'pastdue', 'days', '942')),
 (('2018', '40', '5', 1, 20),
  ('2018', '40', '5'),
  ('<', 'pastdue', 'days', '360')),
 (('2018', '40', '5', 3, 15), ('2018', '40', '5'), ('-', 'task', 'due', '626'))]

data as recursive dictionary
{'2016': {' 5': {'0': [('>', 'soon', 'days', '735'),
                       ('%', 'record', 'date', '490'),
                       ('*', 'event', 'time', '903'),
                       ('*', 'event', 'time', '903'),
                       ('%', 'record', 'date', '114'),
                       ('*', 'event', 'time', '642')],
                 '2': [('-', 'task', 'due', '917'),
                       ('*', 'event', 'time', '747')],
                 '4': [('>', 'soon', 'days', '167'),
                       ('-', 'task', 'due', '257')],
                 '5': [('<', 'pastdue', 'days', '360'),
                       ('%', 'record', 'date', '287'),
                       ('%', 'record', 'date', '570')]},
          '11': {'0': [('!', 'inbox', '', '340'),
                       ('!', 'inbox', '', '301'),
                       ('!', 'inbox', '', '390'),
                       ('!', 'inbox', '', '418'),
                       ('<', 'pastdue', 'days', '876'),
                       ('<', 'pastdue', 'days', '642'),
                       ('>', 'soon', 'days', '650'),
                       ('*', 'event', 'time', '747'),
                       ('-', 'task', 'due', '544'),
                       ('%', 'record', 'date', '162'),
                       ('-', 'task', 'due', '269'),
                       ('*', 'event', 'time', '287')],
                 '2': [('<', 'pastdue', 'days', '698'),
                       ('>', 'soon', 'days', '934')],
                 '3': [('<', 'pastdue', 'days', '881')]},
          '15': {'0': [('<', 'pastdue', 'days', '466'),
                       ('-', 'task', 'due', '625')],
                 '1': [('!', 'inbox', '', '747'),
                       ('-', 'task', 'due', '257'),
                       ('%', 'record', 'date', '196'),
                       ('-', 'task', 'due', '605'),
                       ('-', 'task', 'due', '354')]},
          '30': {'4': [('*', 'event', 'time', '409')],
                 '5': [('%', 'record', 'date', '385')]},
          '37': {'1': [('<', 'pastdue', 'days', '289')],
                 '2': [('-', 'task', 'due', '849')],
                 '5': [('*', 'event', 'time', '431')]},
          '42': {'0': [('!', 'inbox', '', '886'),
                       ('>', 'soon', 'days', '851'),
                       ('-', 'task', 'due', '605'),
                       ('-', 'task', 'due', '626')],
                 '1': [('!', 'inbox', '', '756'),
                       ('<', 'pastdue', 'days', '876'),
                       ('-', 'task', 'due', '849')],
                 '2': [('!', 'inbox', '', '220'), ('>', 'soon', 'days', '506')],
                 '4': [('-', 'task', 'due', '838')],
                 '5': [('!', 'inbox', '', '108'),
                       ('<', 'pastdue', 'days', '910'),
                       ('%', 'record', 'date', '490')]},
          '43': {'0': [('!', 'inbox', '', '756'),
                       ('!', 'inbox', '', '418'),
                       ('<', 'pastdue', 'days', '360'),
                       ('>', 'soon', 'days', '206')],
                 '5': [('<', 'pastdue', 'days', '722'),
                       ('>', 'soon', 'days', '626'),
                       ('*', 'event', 'time', '903'),
                       ('-', 'task', 'due', '451')],
                 '6': [('!', 'inbox', '', '475'),
                       ('<', 'pastdue', 'days', '466'),
                       ('>', 'soon', 'days', '905'),
                       ('%', 'record', 'date', '162')]}},
 '2017': {'19': {'6': [('!', 'inbox', '', '340'),
                       ('<', 'pastdue', 'days', '910'),
                       ('%', 'record', 'date', '419'),
                       ('%', 'record', 'date', '141')]},
          '21': {'2': [('!', 'inbox', '', '301'),
                       ('>', 'soon', 'days', '854'),
                       ('-', 'task', 'due', '849'),
                       ('%', 'record', 'date', '490')],
                 '4': [('!', 'inbox', '', '957'),
                       ('!', 'inbox', '', '108'),
                       ('<', 'pastdue', 'days', '942')],
                 '6': [('!', 'inbox', '', '747'),
                       ('<', 'pastdue', 'days', '698'),
                       ('<', 'pastdue', 'days', '698')]},
          '30': {'0': [('>', 'soon', 'days', '854'),
                       ('%', 'record', 'date', '287'),
                       ('%', 'record', 'date', '288')],
                 '1': [('!', 'inbox', '', '108'),
                       ('!', 'inbox', '', '340'),
                       ('<', 'pastdue', 'days', '360'),
                       ('<', 'pastdue', 'days', '876')],
                 '2': [('>', 'soon', 'days', '650'),
                       ('>', 'soon', 'days', '905'),
                       ('*', 'event', 'time', '287'),
                       ('%', 'record', 'date', '162')]},
          '49': {'3': [('>', 'soon', 'days', '513'),
                       ('%', 'record', 'date', '352')]},
          '53': {'0': [('!', 'inbox', '', '559'),
                       ('<', 'pastdue', 'days', '942'),
                       ('>', 'soon', 'days', '513'),
                       ('>', 'soon', 'days', '111'),
                       ('%', 'record', 'date', '419'),
                       ('-', 'task', 'due', '269')],
                 '6': [('<', 'pastdue', 'days', '636'),
                       ('%', 'record', 'date', '114'),
                       ('*', 'event', 'time', '355'),
                       ('-', 'task', 'due', '917')]}},
 '2018': {' 1': {'2': [('<', 'pastdue', 'days', '360'),
                       ('>', 'soon', 'days', '206')],
                 '4': [('<', 'pastdue', 'days', '642'),
                       ('>', 'soon', 'days', '167'),
                       ('%', 'record', 'date', '141'),
                       ('*', 'event', 'time', '431')]},
          ' 6': {'0': [('<', 'pastdue', 'days', '289'),
                       ('>', 'soon', 'days', '167'),
                       ('-', 'task', 'due', '298')],
                 '1': [('<', 'pastdue', 'days', '722'),
                       ('-', 'task', 'due', '605'),
                       ('-', 'task', 'due', '605')],
                 '4': [('!', 'inbox', '', '886'),
                       ('%', 'record', 'date', '385'),
                       ('%', 'record', 'date', '490'),
                       ('*', 'event', 'time', '287')]},
          '21': {'0': [('!', 'inbox', '', '747'),
                       ('>', 'soon', 'days', '513'),
                       ('-', 'task', 'due', '425'),
                       ('-', 'task', 'due', '625')],
                 '3': [('!', 'inbox', '', '714'),
                       ('<', 'pastdue', 'days', '881'),
                       ('>', 'soon', 'days', '905'),
                       ('%', 'record', 'date', '162')],
                 '6': [('!', 'inbox', '', '390'),
                       ('>', 'soon', 'days', '905')]},
          '30': {'4': [('-', 'task', 'due', '838')]},
          '40': {'5': [('<', 'pastdue', 'days', '942'),
                       ('<', 'pastdue', 'days', '360'),
                       ('-', 'task', 'due', '626')]}}}

data as tree
2016
    5
      0
         > soon                                 days 
         % record                               date 
         * event                                time 
         * event                                time 
         % record                               date 
         * event                                time 
      2
         - task                                 due 
         * event                                time 
      4
         > soon                                 days 
         - task                                 due 
      5
         < pastdue                              days 
         % record                               date 
         % record                               date 
   11
      0
         ! inbox 
         ! inbox 
         ! inbox 
         ! inbox 
         < pastdue                              days 
         < pastdue                              days 
         > soon                                 days 
         * event                                time 
         - task                                 due 
         % record                               date 
         - task                                 due 
         * event                                time 
      2
         < pastdue                              days 
         > soon                                 days 
      3
         < pastdue                              days 
   15
      0
         < pastdue                              days 
         - task                                 due 
      1
         ! inbox 
         - task                                 due 
         % record                               date 
         - task                                 due 
         - task                                 due 
   30
      4
         * event                                time 
      5
         % record                               date 
   37
      1
         < pastdue                              days 
      2
         - task                                 due 
      5
         * event                                time 
   42
      0
         ! inbox 
         > soon                                 days 
         - task                                 due 
         - task                                 due 
      1
         ! inbox 
         < pastdue                              days 
         - task                                 due 
      2
         ! inbox 
         > soon                                 days 
      4
         - task                                 due 
      5
         ! inbox 
         < pastdue                              days 
         % record                               date 
   43
      0
         ! inbox 
         ! inbox 
         < pastdue                              days 
         > soon                                 days 
      5
         < pastdue                              days 
         > soon                                 days 
         * event                                time 
         - task                                 due 
      6
         ! inbox 
         < pastdue                              days 
         > soon                                 days 
         % record                               date 
2017
   19
      6
         ! inbox 
         < pastdue                              days 
         % record                               date 
         % record                               date 
   21
      2
         ! inbox 
         > soon                                 days 
         - task                                 due 
         % record                               date 
      4
         ! inbox 
         ! inbox 
         < pastdue                              days 
      6
         ! inbox 
         < pastdue                              days 
         < pastdue                              days 
   30
      0
         > soon                                 days 
         % record                               date 
         % record                               date 
      1
         ! inbox 
         ! inbox 
         < pastdue                              days 
         < pastdue                              days 
      2
         > soon                                 days 
         > soon                                 days 
         * event                                time 
         % record                               date 
   49
      3
         > soon                                 days 
         % record                               date 
   53
      0
         ! inbox 
         < pastdue                              days 
         > soon                                 days 
         > soon                                 days 
         % record                               date 
         - task                                 due 
      6
         < pastdue                              days 
         % record                               date 
         * event                                time 
         - task                                 due 
2018
    1
      2
         < pastdue                              days 
         > soon                                 days 
      4
         < pastdue                              days 
         > soon                                 days 
         % record                               date 
         * event                                time 
    6
      0
         < pastdue                              days 
         > soon                                 days 
         - task                                 due 
      1
         < pastdue                              days 
         - task                                 due 
         - task                                 due 
      4
         ! inbox 
         % record                               date 
         % record                               date 
         * event                                time 
   21
      0
         ! inbox 
         > soon                                 days 
         - task                                 due 
         - task                                 due 
      3
         ! inbox 
         < pastdue                              days 
         > soon                                 days 
         % record                               date 
      6
         ! inbox 
         > soon                                 days 
   30
      4
         - task                                 due 
   40
      5
         < pastdue                              days 
         < pastdue                              days 
         - task                                 due 
"""