#!/usr/bin/env python3.12

from common import *

def pr(s: str) -> None:
    if __name__ == '__main__':
        ic(s)


def process_entry(s: str) -> (dict, list):
    """
    Tokenize user string returning a dictionary 
        (token_beg, token_end) -> (key, value)
    together with a list of all (key, value) pairs.
    """
    s = s.lstrip()
    if not s:
        return {(0, 1): ('itemtype', '')}, [('itemtype', '')]
    elif s[0] not in TYPE_KEYS:
        return {(0, len(s) + 1): ('itemtype', s[0])}, [('itemtype', s[0])]

    tups = []
    keyvals = []
    pos_hsh = {}  

    parts = [
        [match.span()[0] + 1, match.span()[1], match.group().strip()]
        for match in REGEX['ATAMP'].finditer(s)
    ]
    if not parts:
        tups.append((s[0], s[1:].strip(), 0, len(s)+1))

    lastbeg = 0
    lastend = 1
    lastkey = s[0]
    for beg, end, key in parts:
        tups.append([lastkey, s[lastend:beg].strip(), lastbeg, beg])
        pos_hsh[tups[-1][2], tups[-1][3]] = (tups[-1][0], tups[-1][1])
        lastkey = key
        lastbeg = beg
        lastend = end
    tups.append([lastkey, s[lastend:].strip(), lastbeg, len(s)+1])
    pos_hsh[tups[-1][2], tups[-1][3]] = (tups[-1][0], tups[-1][1])

    # add (@?, '') and (&?, '') tups for @ and & entries without keys
    aug_tups = []
    for key, value, beg, end in tups:
        if beg == 0:
            aug_tups.append(('itemtype', key, beg, 1))
            if value.endswith(' @') or value.endswith(' &'):
                aug_key = f"{value[-1]}?"
                end -= 2
                value = value[:-2]
                aug_tups.extend((('summary', value, 1, end), (aug_key, '', end, end + 2)))
            else:
                aug_tups.append(('summary', value, 1, end))
        elif value.endswith(' @') or value.endswith(' &'):
            aug_key = f"{value[-1]}?"
            end -= 2
            value = value[:-2]
            aug_tups.extend(((key, value, beg, end), (aug_key, '', end, end + 2)))
        else:
            aug_tups.append((key, value, beg, end))

    for key, value, beg, end in aug_tups:
        if key in ['@r', '@j']:
            pos_hsh[beg, end] = (f"{key[-1]}{key[-1]}", value)
            adding = key[-1]
        elif key in ['@a', '@u']:
            pos_hsh[beg, end] = (key[-1], value)
            adding = None
        elif key.startswith('&'):
            if adding:
                pos_hsh[beg, end] = (f"{adding}{key[-1]}", value)
        elif key in ['itemtype', 'summary']:
            adding = None
            pos_hsh[beg, end] = (key, value)
        else:
            adding = None
            pos_hsh[beg, end] = (key[-1], value)

    keyvals = [(k, v) for pos, (k, v) in pos_hsh.items()]
    if keyvals[0][0] in TYPE_KEYS:
        k, v = keyvals.pop(0)
        keyvals.insert(0, ('summary', v))
        keyvals.insert(0, ('itemtype', k))

    return pos_hsh, keyvals

s = "* evnt @s 2p fri @e 90m @r m &w 2fr & @c dag"
pr(s)
pr(process_entry(s))
# ic| s: '* evnt @s 2p fri @e 90m @r m &w 2fr & @c dag'
# ic| s: ({(0, 1): ('itemtype', '*'),
#          (0, 7): ('*', 'evnt'),
#          (1, 7): ('summary', 'evnt'),
#          (7, 17): ('s', '2p fri'),
#          (17, 24): ('e', '90m'),
#          (24, 29): ('rr', 'm'),
#          (29, 36): ('rw', '2fr'),
#          (29, 38): ('&w', '2fr &'),
#          (36, 38): ('r?', ''),
#          (38, 45): ('c', 'dag')},
#         [('itemtype', '*'),
#          ('summary', 'evnt'),
#          ('s', '2p fri'),
#          ('e', '90m'),
#          ('rr', 'm'),
#          ('&w', '2fr &'),
#          ('c', 'dag'),
#          ('itemtype', '*'),
#          ('summary', 'evnt'),
#          ('rw', '2fr'),
#          ('r?', '')])


def active_from_pos(process_entry_tup: tuple, position: int) -> tuple:
    """
    From the tuple produced by process_entry, return the element at position.
    """
    for p, v in process_entry_tup[0].items():
        if p[0] <= position < p[1]:
            return p, v
    # else return the last p, v pair
    return p, v

s = "* evnt @s 2p fri @e 90m @r w &w 2fr &u 6/1 9a @c dag @l home"
pr(s)
t = process_entry(s)
for _ in [3,  18, 45]: 
    pr(_)
    pr(active_from_pos(t, _))
# ic| s: '* evnt @s 2p fri @e 90m @r w &w 2fr &u 6/1 9a @c dag @l home'
# ic| s: 3
# ic| s: ((0, 7), ('*', 'evnt'))
# ic| s: 18
# ic| s: ((17, 24), ('e', '90m'))
# ic| s: 45
# ic| s: ((36, 46), ('ru', '6/1 9a'))
