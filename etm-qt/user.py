#!/usr/bin/env python3.12

from common import *

def pr(s: str) -> None:
    if __name__ == '__main__':
        ic(s)


def process_entry(s: str) -> (dict, list):
    """
    Tokenize user string returning a dictionary 
        (token_beg, token_end) -> [key, value]
    together with a list of all (key, value) pairs.
    """
    s = s.lstrip()
    if not s:
        return {(0, 1): ('itemtype', '')}, [('itemtype', '')]
    elif s[0] not in type_keys:
        return {(0, len(s) + 1): ('itemtype', s[0])}, [('itemtype', s[0])]

    tups = []
    keyvals = []
    pos_hsh = {}  

    parts = [
        [match.span()[0] + 1, match.span()[1], match.group().strip()]
        for match in atamp_regex.finditer(s)
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
    if keyvals[0][0] in type_keys:
        k, v = keyvals.pop(0)
        keyvals.insert(0, ('summary', v))
        keyvals.insert(0, ('itemtype', k))

    return pos_hsh, keyvals

s = "* evnt @s 2p fri @e 90m @r m &w 2fr & @c dag"
pr(s)
pr(process_entry(s))
