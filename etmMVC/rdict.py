#! /usr/bin/env python3

"""
Tree structure: recursive (nested) dict with leaves as lists of display columns plus uid tuples. Examples:
Agenda: year -> week -> day -> [(type code, summary, times, uid)]
Index: path[0] -> path[1] -> ... -> (type code, summary, relevant datetime, uid)
"""

class RDict(dict):
    tab = " " * 3

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

    def as_tree(self, t={}, depth = 0):
        """ print a tree """
        # tab = " "*3
        for k in t.keys():
            print("%s%s" % (depth * RDict.tab,  k))
            depth += 1
            if type(t[k]) == RDict:
                self.as_tree(t[k], depth)
            else:
                print("%s%s" % (depth * RDict.tab, t[k]))
            depth -= 1





if __name__ == '__main__':

    from random import randint
    from pprint import pprint
    import bisect

    # sample data
    data = []
    for y in range(2016, 2019):
        year = "{}".format(y)
        for w in range(1, randint(5, 9)):
            week = "{:>2}".format(randint(1, 53))
            for d in range(1, randint(2, 6)):
                day = "{}".format(randint(0, 6))
                for j in range(1, randint(2, 5)):
                    u = "{}".format(randint(1, 1000))
                    ###############################
                    # use bisect to preserve order
                    ###############################
                    bisect.insort(data, ((".".join([str(year), str(week), str(day)]), (u))))

    print("data:", len(data), "items")
    pprint(data)

    # create recursive dict from data
    index = RDict()
    for path, value in data:
        # add(index, path, value)
        index.add(path, value)

    pprint(index)

    # as_tree(index)
    index.as_tree()
