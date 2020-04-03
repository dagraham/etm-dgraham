import os
import math
import sys
import shutil
import textwrap
import re
from pprint import pprint
from copy import deepcopy
from tinydb import where, Query
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
import etm.options as options
from etm import view
from etm.model import item_details
from etm.model import format_hours_and_tenths
import etm.data as data
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from pygments.lexer import RegexLexer
from pygments.token import Keyword
from pygments.token import Literal
from pygments.token import Operator
from pygments.token import Comment
import pendulum
from pendulum import parse
import itertools
from itertools import groupby
flatten = itertools.chain.from_iterable
from operator import itemgetter

# import etm.view as view
# from etm.model import parse_datetime, date_to_datetime

# ETMDB = view.ETMDB 
# DBITEM = view.DBITEM
# DBARCH = view.DBARCH

ZERO = pendulum.duration(minutes=0)
ONEMIN = pendulum.duration(minutes=1)
DAY = pendulum.duration(days=1)

# class TDBLexer(RegexLexer):

#     name = 'TDB'
#     aliases = ['tdb']
#     filenames = '*.*'
#     flags = re.MULTILINE | re.DOTALL

#     tokens = {
#             'root': [
#                 (r'(matches|search|equals|more|less|exists|any|all|one)\b', Keyword),
#                 (r'(itemtype|summary)\b', Literal),
#                 (r'(and|or|info)\b', Operator),
#                 ],
#             }

# class ETMQuery(object):

#     def __init__(self):
#         self.arg = { 'matches': self.matches,
#                 'search': self.search,
#                 'equals': self.equals,
#                 'more': self.more,
#                 'less': self.less,
#                 'exists': self.exists,
#                 'any': self.in_any,
#                 'all': self.in_all,
#                 'one': self.one_of,
#                 'info': self.info,
#                 'dt' : self.dt,
#                 }

#         self.op = {
#                 '=': self.maybe_equal,
#                 '>': self.maybe_later,
#                 '<': self.maybe_earlier
#                 }

#         self.lexer = PygmentsLexer(TDBLexer)
#         self.style = etm_style
#         self.Item = Query()

#         self.allowed_commands = ", ".join([x for x in self.arg])

#         self.command_details = """\
#     matches a b: return items in which field[a] begins
#         with regex b 
#     search a b: return items in which field[a] contains 
#         regex b
#     equals a b: return items in which field[a] == b
#     more a b: return items in which field[a] >= b
#     less a b: return items in which field[a] <= b
#     exists a: return items in which field[a] exists
#     any a b: return items in which at least one 
#         element of field[a] is an element of the list b 
#     all a b: return items in which the elements of 
#         field[a] contain all the elements of the list b 
#     one a b: return items in which the value of 
#         field[a] is one of the elements of list b
#     info a: return the details of the item whose 
#         document id equals the integer a
#     dt a b: return items in which the value of field[a] 
#         is a date if b = '? date' or a datetime if 
#         b = '? time'. Else if b begins with  '>', '='
#         or '<' followed by a string following the format 
#         'yyyy-mm-dd-HH-MM' then return items where the
#         date/time in field[a] bears the specified 
#         relation to the string. E.g., 
#             dt s < 2020-1-17 
#         would return items with @s date/times whose 
#         year <= 2020, month <= 1 and month day <= 17. 
#         Hours and minutes are ignored when field[a] is
#         a date."""

#         self.usage = f"""\
# Query has components in the format: [~]command a [b]
# where "a" is one of the etm fields: itemtype, summary,
# or one of the @keys and "command" is one of the 
# following:
# {self.command_details}
# E.g., find items where the summary contains "waldo":
#     query: search summary waldo
# Precede a command with "~" to negate it. E.g., find 
# reminders where the summary does not contain "waldo":
#     query: ~search summary waldo
# To enter a list of values for "b", simply separate the 
# components with spaces. Conversely, to enter a regex 
# with a space and avoid its being interpreted as a list, 
# replace the space with \s. Components can be joined the 
# using "or" or "and". E.g., find reminders where either 
# the summary or the entry for @d (description) contains 
# "waldo":
#     query: search summary waldo or search d waldo
# Press 'Enter' to submit a query, close the entry area
# and display the results. Press 'q' to reopen the entry
# area to submit another query. Submit '?' or 'help' 
# to show this display or nothing to quit. In the entry
# area, the 'up' and 'down' cursor keys scroll through
# previously submitted queries.
# """

#     def is_datetime(self, val):
#         return isinstance(val, pendulum.DateTime)

#     def is_date(self, val):
#         return isinstance(val, pendulum.Date) and not isinstance(val, pendulum.DateTime)

#     def maybe_equal(self, val, args):
#         """
#         args = year-month-...-minute
#         """
#         args = args.split("-")
#         # args = list(args)
#         if not isinstance(val, pendulum.Date):
#             # neither a date or a datetime
#             return False
#         if args and not val.year == int(args.pop(0)):
#             return False
#         if args and not val.month == int(args.pop(0)):
#             return False
#         if args and not val.day == int(args.pop(0)):
#             return False
#         if isinstance(val, pendulum.DateTime):
#             # val has hours and minutes
#             if args and not val.hour == int(args.pop(0)):
#                 return False
#             if args and not val.minute == int(args.pop(0)):
#                 return False
#         return True

#     def maybe_later(self, val, args):
#         """
#         args = year-month-...-minute
#         """
#         args = args.split("-")
#         # args = list(args)
#         if not isinstance(val, pendulum.Date):
#             # neither a date or a datetime
#             return False
#         if args and not val.year >= int(args.pop(0)):
#             return False
#         if args and not val.month >= int(args.pop(0)):
#             return False
#         if args and not val.day >= int(args.pop(0)):
#             return False
#         if isinstance(val, pendulum.DateTime):
#             # val has hours and minutes
#             if args and not val.hour >= int(args.pop(0)):
#                 return False
#             if args and not val.minute >= int(args.pop(0)):
#                 return False
#         return True

#     def maybe_earlier(self, val, args):
#         """
#         args = year-month-...-minute
#         """
#         args = args.split("-")
#         # args = list(args)
#         if not isinstance(val, pendulum.Date):
#             # neither a date or a datetime
#             return False
#         if args and not val.year <= int(args.pop(0)):
#             return False
#         if args and not val.month <= int(args.pop(0)):
#             return False
#         if args and not val.day <= int(args.pop(0)):
#             return False
#         if isinstance(val, pendulum.DateTime):
#             # val has hours and minutes
#             if args and not val.hour <= int(args.pop(0)):
#                 return False
#             if args and not val.minute <= int(args.pop(0)):
#                 return False
#         return True


#     def matches(self, a, b):
#         # the value of at least one element of field 'a' begins with the case-insensitive regex 'b'
#         return where(a).matches(b, flags=re.IGNORECASE)

#     def search(self, a, b):
#         # the value of at least one element of field 'a' contains the case-insensitive regex 'b'
#         return where(a).search(b, flags=re.IGNORECASE)

#     def equals(self, a, b):
#         # the value of at least one element of field 'a' equals 'b'
#         try:
#             b = int(b)
#         except:
#             pass
#         return where(a) == b

#     def more(self, a, b):
#         # the value of at least one element of field 'a' >= 'b'
#         try:
#             b = int(b)
#         except:
#             pass
#         return where(a) >= b

#     def less(self, a, b):
#         # the value of at least one element of field 'a' equals 'b'
#         try:
#             b = int(b)
#         except:
#             pass
#         return where(a) <= b

#     def exists(self, a):
#         # field 'a' exists
#         return where(a).exists()


#     def in_any(self, a, b):
#         """
#         the value of field 'a' is a list of values and at least 
#         one of them is an element from 'b'. Here 'b' should be a list with
#         2 or more elements. With only a single element, there is no 
#         difference between any and all.

#         With egs, "any,  blue, green" returns all three items.
#         """

#         if not isinstance(b, list):
#             b = [b]
#         return where(a).any(b)

#     def in_all(self, a, b):
#         """
#         the value of field 'a' is a list of values and among the list 
#         are all the elements in 'b'. Here 'b' should be a list with
#         2 or more elements. With only a single element, there is no 
#         difference between any and all.

#         With egs, "all, blue, green" returns just "blue and green"
#         """
#         if not isinstance(b, list):
#             b = [b]
#         return where(a).all(b)

#     def one_of(self, a, b):
#         """
#         the value of field 'a' is one of the elements in 'b'. 

#         With egs, "one, summary, blue, green" returns both "green" and "blue"
#         """
#         if not isinstance(b, list):
#             b = [b]
#         return where(a).one_of(b)

#     def info(self, a):
#         # field 'a' exists
#         item = DBITEM.get(doc_id=int(a))
#         return  f"{item_details(item, False)}"


#     def dt(self, a, b):
#         if b[0]  == '?':
#             if b[1] == 'time':
#                 return self.Item[a].test(self.is_datetime)
#             elif b[1] == 'date':
#                 return self.Item[a].test(self.is_date)

#         return self.Item[a].test(self.op[b[0]], b[1])

#     def process_query(self, query):

#         parts = [x.split() for x in re.split(r' (and|or) ', query)]

#         cmnds = []
#         for part in parts:
#             part = [x.strip() for x in part if x.strip()]
#             negation = part[0].startswith('~')
#             if part[0] not in ['and', 'or']:
#                 # we have a command
#                 if negation:
#                     # drop the ~
#                     part[0] = part[0][1:]
#                 if self.arg.get(part[0], None) is None:
#                     return False, f"""bad command: '{part[0]}'. Only commands in\n {self.allowed_commands}\nare allowed."""

#             if len(part) > 3:
#                 if negation:
#                     cmnds.append(~ self.arg[part[0]](part[1], [x.strip() for x in part[2:]]))
#                 else:
#                     cmnds.append(self.arg[part[0]](part[1], [x.strip() for x in part[2:]]))
#             elif len(part) > 2:
#                 if negation:
#                     cmnds.append(~ self.arg[part[0]](part[1], part[2]))
#                 else:
#                     cmnds.append(self.arg[part[0]](part[1], part[2]))
#             elif len(part) > 1:
#                 if negation:
#                     cmnds.append(~ self.arg[part[0]](part[1]))
#                 else:
#                     cmnds.append(self.arg[part[0]](part[1]))
#             else:
#                 cmnds.append(part[0])

#         test = cmnds[0]
#         for i in range(1, len(cmnds)):
#             if i % 2:
#                 if cmnds[i] == 'and' or cmnds[i] == 'or':
#                     andor = cmnds[i]
#                     continue
#             if andor == 'or':
#                 test = test | cmnds[i]
#             else:
#                 test = test & cmnds[i]
#         return True, test

#     def do_query(self, query):
#         """
#         For internal usage
#         """
#         if query == "?" or query == "help":
#             return False, self.usage
#         elif query.startswith('u') or query.startswith('c'):
#             show_report_items(query)
#             ok, 
#         try:
#             ok, test = self.process_query(query)
#             if not ok:
#                 return False, test
#             if isinstance(test, str): 
#                 # info
#                 return False, test
#             else:
#                 items = DBITEM.search(test)
#                 logger.debug(f"search items: {items}")
#                 return True, items 
#         except Exception as e:
#             return False, f"exception processing '{query}':\n{e}"

# query = ETMQuery()
# query_area = TextArea(
#     height=3, 
#     style='class:query', 
#     # style=query.style,
#     lexer=query.lexer,
#     multiline=False,
#     prompt='query: ', 
#     focusable=True,
#     # wrap_lines=True,
#     )

# ############# end query ################################

minus_regex = re.compile(r'\s+\-(?=[a-zA-Z])')
groupdate_regex = re.compile(r'\bY{2}\b|\bY{4}\b|\b[M]{1,4}\b|\b[d]{2,4}\b|\b[D]{1,2}\b|\b[w]\b')

# supported date formats (subset of pendulum)
# 'YYYY',     # year 2019
# 'YY',       # year 19
# 'Q',        # quarter 1, .., 4
# 'MMMM',     # month January
# 'MMM',      # month Jan
# 'MM',       # month 01
# 'M',        # month 1
# 'DD',       # month day 09
# 'D',        # month day 9
# 'dddd',     # week day Monday
# 'ddd',      # week day Mon
# 'dd',       # week day Mo

ETMDB = None
DBITEM = None
DBARCH = None

etm_style = Style.from_dict({
    'pygments.comment':   '#888888 bold',
    'pygments.keyword': '#009900 bold',
    'pygments.literal':   '#0066ff bold',  #blue
    'pygments.operator':  '#e62e00 bold',  #red
    # 'pygments.keyword':   '#e62e00 bold',  #red
})


class TDBLexer(RegexLexer):

    name = 'TDB'
    aliases = ['tdb']
    filenames = '*.*'
    flags = re.MULTILINE | re.DOTALL

    tokens = {
            'root': [
                (r'(matches|search|equals|more|less|exists|any|all|one|dt)\b', Keyword),
                (r'(itemtype|summary)\b', Literal),
                (r'(and|or|info)\b', Operator),
                ],
            }


def maybe_round(obj):
    """
    round up to the nearest UT_MIN minutes.
    """
    if not isinstance(obj, pendulum.Duration):
        return None
    try:
        if UT_MIN == 1:
            return obj
        minutes = 0
        if obj.weeks:
            minutes += obj.weeks * 7 * 24 * 60
        if obj.remaining_days:
            minutes += obj.remaining_days * 24 * 60
        if obj.hours:
            minutes += obj.hours * 60
        if obj.minutes:
            minutes += obj.minutes
        if minutes: 
            minutes = math.ceil(minutes/UT_MIN)*(UT_MIN)
            return minutes * ONEMIN
        else:
            return ZERO

    except Exception as e:
        print('format_usedtime', e)
        print(obj)
        return None

def apply_dates_filter(items, grpby, filters):
    if grpby['report'] == 'u':
        def rel_dt(item, filters):
            rdts = []
            ok = False
            used_times = deepcopy(item['u'])
            if 'b' in filters and 'e' in filters: # both b and e
                for x in used_times:
                    if x[1] < filters['b'] or x[1] > filters['e']:
                        item['u'].remove(x)
            elif 'b' in filters: # only b
                for x in used_times:
                    if x[1] < filters['b']:
                        item['u'].remove(x)
            elif 'e' in filters: # only e
                for x in item['u']:
                    if x[1] > filters['e']:
                        item['u'].remove(x)
            items = []
            dt2ut = {}
            for x in item['u']:
                rdt = x[1].date()
                dt2ut.setdefault(rdt, ZERO)
                dt2ut[rdt] += maybe_round(x[0])
            for rdt in dt2ut:
                tmp = deepcopy(item)
                tmp['rdt'] = rdt
                tmp['u'] = (rdt, dt2ut[rdt])
                items.append(tmp)
            return items

    elif grpby['report'] == 'c':
        def rel_dt(item, filters):
            ok = False
            items = []
            tmp = deepcopy(item)
            if 'f' in item:
                rdt = item['f'].date()
                e_ok = 'e' not in filters or item['f'] <= filters['e'] 
                b_ok = 'b' not in filters or item['f'] >= filters['b']
            elif 's' in item:
                rdt = item['s'].date()
                e_ok = 'e' not in filters or item['s'] <= filters['e'] 
                b_ok = 'b' not in filters or item['s'] >= filters['b']
            else:
                e_ok = b_ok = False
            if e_ok and b_ok:
                tmp['rdt'] = rdt
                items.append(tmp)
            return items

    ok_items = []
    for item in items:
        ok_items.extend(rel_dt(item, filters))
    ok = len(ok_items) > 0
    return ok_items


def format_usedtime(obj, short=True):
    """
    if short report only hours and minutes, else include weeks and days
    >>> td = pendulum.duration(weeks=1, days=2, hours=3, minutes=27)
    >>> format_usedtime(td)
    '1w2d3h27m'
    """
    if not isinstance(obj, pendulum.Duration):
        return None
    hours = obj.hours
    try:
        until =[]
        if obj.weeks:
            if short: 
                hours += obj.weeks * 7 * 24
            else:
                until.append(f"{obj.weeks}w")

        if obj.remaining_days:
            if short:
                hours += obj.remaining_days * 24
            else:
                until.append(f"{obj.remaining_days}d")
        if hours:
            until.append(f"{hours}h")
        if obj.minutes:
            until.append(f"{obj.minutes}m")
        if not until and not short:
            until.append("0m")
        return "".join(until)
    except Exception as e:
        print('format_usedtime', e)
        print(obj)
        return None

class QDict(dict):
    """
    Constructed from rows of (path, values) tuples. The path will be split using 'split_char' to produce the nodes leading to 'values'. The last element in values is presumed to be the 'id' of the item that generated the row. 
    """

    tab = 2

    # def __init__(self, split_char='/', used_time={}):
    def __init__(self, used_time={}, row=0):
        self.width = shutil.get_terminal_size()[0]
        self.row = row
        self.row2id = {}
        self.output = []
        # self.split_char = split_char
        self.used_time = used_time

    def __missing__(self, key):
        self[key] = QDict()
        return self[key]

    def as_dict(self):
        return self

    def leaf_detail(self, detail, depth):
        dindent = QDict.tab * (depth + 1) * " "
        paragraphs = detail.split('\n')
        ret = []
        for para in paragraphs:
            ret.extend(textwrap.fill(para, initial_indent=dindent, subsequent_indent=dindent, width=self.width-QDict.tab*(depth-1)).split('\n'))
        return ret


    def add(self, keys, values=()):
        # keys = tkeys.split(self.split_char)
        # if isinstance(keys, str):
        #     keys = keys.split(self.split_char)
        for j in range(len(keys)):
            key = keys[j]
            keys_left = keys[j+1:]
            if not keys_left:
                try:
                    self.setdefault(key, []).append(values)
                except Exception as e:
                    logger.warn(f"error adding key: {key}, values: {values}\n self: {self}; e: {repr(e)}")
            if isinstance(self[key], dict):
                self = self[key]
            elif keys_left:
                self.setdefault(":".join(keys[j:]), []).append(values)
                break

    def as_tree(self, t={}, depth = 0, level=0, pre=[]):
        """ return an indented tree """
        for k in t.keys():
            del pre[depth:]
            pre.append(k)
            indent = QDict.tab * depth * " "
            if self.used_time:
                self.output.append("%s%s: %s" % (indent,  k, format_usedtime(self.used_time.get(tuple(pre), ''))))
            else:
                self.output.append("%s%s" % (indent,  k))
            self.row += 1 
            depth += 1
            if level and depth > level:
                depth -= 1
                continue

            if type(t[k]) == QDict:
                self.as_tree(t[k], depth, level, pre)
            else:
                for leaf in t[k]:
                    indent = QDict.tab * depth * " "
                    if self.used_time:
                        self.output.append("%s%s %s: %s" % (indent, leaf[0], leaf[1], format_usedtime(leaf[2])))
                        num_leafs = 3
                    else:
                        self.output.append("%s%s %s" % (indent, leaf[0], leaf[1]))
                        num_leafs = 2
                    self.row2id[self.row] = leaf[-1]
                    self.row += 1 
                    if len(leaf) > num_leafs + 1:
                        if leaf[num_leafs]:
                            lines = self.leaf_detail(leaf[num_leafs], depth)
                            for line in lines:
                                self.output.append(line)
                                self.row += 1
            depth -= 1
        return "\n  ".join(self.output), self.row2id


def get_output_and_row2id(items, grpby, header=""):
    used_time = {}
    ret = []
    sort_tups = [x for x in grpby.get('sort', [])]
    path_tups = [x for x in grpby.get('path', [])]
    dtls_tups  = [x for x in grpby.get('dtls', [])]
    for item in items:
        st = [eval(x, {'item': item, 're': re}) for x in sort_tups]
        pt = [eval(x, {'item': item, 're': re}) for x in path_tups]
        try:
            dt = [eval(x, {'item': item, 're': re}) for x in dtls_tups if x]
        except:
            print(f"error processing {dtls_tups}")
        if grpby['report'] == 'u':
            dt[2] = ut = maybe_round(dt[2])
            for i in range(len(pt)):
                key = tuple(pt[:i+1])
                used_time.setdefault(key, ZERO) 
                used_time[key] += ut
        ret.append((st, pt, dt))
    ret.sort()
    ret = [x[1:] for x in ret]

    # create recursive dict from data
    if header:
        row = 1
    else:
        row = 0
    index = QDict(used_time, row)
    for path, value in ret:
        index.add(path, value)

    output, row2id = index.as_tree(index)
    return f"{header}\n  {output}", row2id

def get_grpby_and_filters(s, options=None):

    if not options:
        options = {}
    grpby = {}
    filters = {}
    op_str = s.split('#')[0]
    parts = minus_regex.split(op_str)
    head = parts.pop(0)
    report = head[0]
    groupbystr = head[1:].strip()
    if not report or report not in ['c', 'u']:
        return {}, {}
    grpby['report'] = report
    filters['dates'] = False
    grpby['dated'] = False
    filters['query'] = f"exists {report}" if report == 'u' else "exists itemtype"
    filters['neg_fields'] = []
    filters['pos_fields'] = []
    groupbylst = []
    if groupbystr:
        groupbylst = [x.strip() for x in groupbystr.split(';')]
        # print(f"groupbylst: {groupbylst}")
        for comp in groupbylst:
            comp_parts = comp.split(' ')
            for part in comp_parts:
                if groupdate_regex.match(part):
                    grpby['dated'] = True
                    filters['dates'] = True
                elif part not in ['c', 'l'] and part[0] not in ['i', 't']:
                    print(f"Ignoring invalid groupby part: {part}")
                    groupbylst.remove(comp)
        grpby['args'] = groupbylst
    grpby['path'] = []
    grpby['sort'] = []
    filters['missing'] = False
    include = {'Y', 'M', 'D'}
    if groupbylst:
        for group in groupbylst:
            d_lst = []
            if groupdate_regex.search(group):
                if 'w' in group:
                    # groupby week or some other date spec,  not both
                    group = "w"
                    d_lst.append('w')
                    # include.discard('w')
                    if 'Y' in group:
                        include.discard('Y')
                    if 'M' in group:
                        include.discard('M')
                    if 'D' in group:
                        include.discard('D')
                else:
                    if 'Y' in group:
                        d_lst.append('YYYY')
                        include.discard('Y')
                    if 'M' in group:
                        d_lst.append('MM')
                        include.discard('M')
                    if 'D' in group:
                        d_lst.append('DD')
                        include.discard('D')
                tmp = " ".join(d_lst)
                grpby['sort'].append(f"item['rdt'].format('{tmp}')")
                grpby['path'].append(
                    f"item['rdt'].format('{group}')")

            elif '[' in group:
                if group[0] == 'i':
                    if ':' in group:
                        grpby['path'].append(
                                f"'/'.join(re.split('/', item['{group[0]}']){group[1:]})")
                        grpby['sort'].append(
                                f"'/'.join(re.split('/', item['{group[0]}']){group[1:]})")
                    else:
                        grpby['path'].append(
                                f"re.split('/', item['{group[0]}']){group[1:]}" )
                        grpby['sort'].append(
                                f"re.split('/', item['{group[0]}']){group[1:]}")
            else:
                grpby['path'].append("item['%s']" % group.strip())
                grpby['sort'].append(f"item['{group.strip()}']")
            if include:
                if include == {'Y', 'M', 'D'}:
                    grpby['include'] = "YYYY-MM-DD"
                elif include == {'M', 'D'}:
                    grpby['include'] = "MMM D"
                elif include == {'y', 'd'}:
                    grpby['include'] = "YYYY-MM-DD"
                elif include == set(['Y', 'w']):
                    groupby['include'] = "w"
                elif include == {'D'}:
                    grpby['include'] = "MMM D"
                elif include == set(['w']):
                    grpby['include'] = "w"
                else:
                    grpby['include'] = ""
            else:
                grpby['include'] = ""
            # logger.debug('grpby final: {0}'.format(grpby))

    also = []
    omit = ['$']
    for part in parts:
        key = part[0]
        if key == 'a':
            value = [x.strip() for x in part[1:].split(',')]
            also.extend(value)
        elif key in ['b', 'e']:
            dt = parse(part[1:], strict=False, tz='local')
            filters[key] = dt

        elif key == 'm':
            value = part[1:].strip()
            if value == '1':
                filters['missing'] = True

        elif key == 'q':
            value = part[1:].strip()
            filters['query'] += f" and {value}"

        elif key == 'd':
            if grpby['report'] == 'u':
                d = int(part[1:])
                if d:
                    d += 1
                grpby['depth'] = d

        elif key == 't':
            value = [x.strip() for x in part[1:].split(',')]
            for t in value:
                if t[0] == '!':
                    filters['neg_fields'].append((
                        't', re.compile(r'%s' % t[1:], re.IGNORECASE)))
                else:
                    filters['pos_fields'].append((
                        't', re.compile(r'%s' % t, re.IGNORECASE)))
        elif key == 'o':
            omit = [x.strip() for x in part[1:].split(',') if x.strip() in ['$', '*', '-', '%']]
        elif key == 'w':
            grpby['width1'] = int(part[1:])
        elif key == 'W':
            grpby['width2'] = int(part[1:])
        else:
            value = part[1:].strip()
            if value[0] == '~':
                filters['neg_fields'].append((
                    key, re.compile(r'%s' % value[1:], re.IGNORECASE)))
            else:
                filters['pos_fields'].append((
                    key, re.compile(r'%s' % value, re.IGNORECASE)))
    if omit:
        tmp = [f" and ~equals itemtype {key}" for key in omit]
        filters['query'] += "".join(tmp)

    details = []
    details.append("item['itemtype']")
    details.append("item['summary']")
    if report == 'u':
        details.append("item['u'][1]")
    else:
        details.append("")
    if also:
        details.extend([f"item.get('{x}', 'none')" for x in also])
    details.append("item.doc_id")
    grpby['dtls'] = details
    # logger.debug('grpby: {0}; dated: {1}; filters: {2}'.format(grpby, dated, filters))
    return grpby, filters

def show_query_results(text, grpby, items):
    width = shutil.get_terminal_size()[0] - 7 
    rows = []
    summary_width = width - 6 
    if not items or not isinstance(items, list):
        return f"query: {text}\n   none matching", {}
    header = f"query: {text[:summary_width]}"
    output, row2id = get_output_and_row2id(items, grpby, header)
    return output, row2id


def main(etmdir, args):

    # view.item_details = item_details
    # settings = options.Settings(etmdir).settings
    # secret = settings.get('secret')
    # data.secret = secret

    # from etm.view import Query
    query = ETMQuery()

    session = PromptSession()

    again = True
    while again:

        print("Enter 'quit', 'stop', 'exit' or '' to exit loop")
        text = session.prompt("query: ", lexer=query.lexer)
        if not text or text in ['quit', 'stop', 'exit']:
            again = False
            continue
        if text == "d": # with descriptions
            text = "u i[0]; MMM YYYY; i[1:]; ddd D -b 3/1 -e 4/1 -a d"
        elif text == "p": # without descriptions
            text = "u i[0]; MMM YYYY; i[1:]; ddd D -b 3/1 -e 4/1"
        elif text == "w": # without descriptions and days
            text = "u i[0]; MMM YYYY; i[1:] -b 1/1 -e 3/1"
        elif text == "a": # client a only
            text = "u i[0]; MMM YYYY; i[1:] -q matches i client\sa -b 1/1 -e 3/1 -a d"
        elif len(text.strip()) == 1:
            print("missing report arguments")
            continue
        print(f"query: {text}")
        if text.startswith('u') or text.startswith('c'):
            # if len(text.strip()) == 1:
            #     continue
            grpby, filters = get_grpby_and_filters(text)
            if not grpby:
                continue
            print(f"grpby: {grpby}\n\nfilters: {filters}")
            ok, items = query.do_query(filters.get('query'))
            if ok:
                items = apply_dates_filter(items, grpby, filters)
                output, row2id = get_output_and_row2id(items, grpby)
                print(output)
            else:
                print(items)
        else:
            ok, items = query.do_query(text)
            if ok:
                for item in items:
                    print(f"   {item['itemtype']} {item.get('summary', 'none')} {item.doc_id}")
            else:
                print(items)

# text = prompt('query: ', lexer=PygmentsLexer(etm_style))
# print('You said: %s' % text)

if __name__ == '__main__':
    sys.exit('report.py should only be imported')

