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

import etm.view as view
from etm.view import ETMQuery
# from etm.model import parse_datetime, date_to_datetime

def parse_datetime(s):
    return parse(s, strict=False, tz='local')

ZERO = pendulum.duration(minutes=0)
ONEMIN = pendulum.duration(minutes=1)
DAY = pendulum.duration(days=1)

"""
From etm3
Report types
    a) action report (used time)
    c) custom report (non action)

Groupby
    l) location
    i) index
    t) tag
    dates)
        year: YYYY, YY
        quarter: Q
        month: MMMM, MMM, MM, M
        day of month: DD, D
        day of week: dddd, ddd, dd, d

Options
    -a append fields, eg 'd', 'l'
    -b begin date
    -e end date 
    -l location
    -d depth
    -i index
    -m missing
    -o omit ['$'], just inbox items by default
    -q query
        -q itemtype equals - and ~exists f
    -t tags

examples
    u i[0]; i[1:]; 

From get_usedtime
    for item in matching_items:
        used = item.get('u') # this will be a list of 'period, datetime' tuples 
        if not used:
            continue
        index = item.get('i', '~')
        # if index == '~':
        #     continue
        description = item.get('d', "")
        id_used = {}
        index_tup = index.split('/')
        doc_id = item.doc_id
        if item['itemtype'] == '-' and 'f' in item:
            itemtype = finished_char
        else:
            itemtype = item['itemtype'] 
        details = f"{itemtype} {item['summary']}"
        for period, dt in used:
            if isinstance(dt, pendulum.Date) and not isinstance(dt, pendulum.DateTime): 
                dt = pendulum.parse(dt.format("YYYYMMDD"), tz='local')
                dt.set(hour=23, minute=59, second=59)
            # for id2used
            if UT_MIN != 1:
                res = period.minutes % UT_MIN
                if res:
                    period += (UT_MIN - res) * ONEMIN

            monthday = dt.date()
            id_used.setdefault(monthday, ZERO)
            id_used[monthday] += period
            # for used_time
            month = dt.format("YYYY-MM")
            used_time.setdefault(tuple((month,)), ZERO)
            used_time[tuple((month, ))] += period
            for i in range(len(index_tup)):
                used_time.setdefault(tuple((month, *index_tup[:i+1])), ZERO)
                used_time[tuple((month, *index_tup[:i+1]))] += period
        for monthday in id_used:
            month = monthday.format("YYYY-MM")
            detail_rows.append({
                        'sort': (month, *index_tup, monthday, details),
                        'month': month,
                        'path': f"{monthday.format('MMMM YYYY')}/{index}",
                        'description': description,
                        'columns': [
                            details,
                            f"{format_hours_and_tenths(id_used[monthday])} {monthday.format('MMM D')}",
                            doc_id],
                        })

    detail_rows.sort(key=itemgetter('sort'))
    for month, items in groupby(detail_rows, key=itemgetter('month')):
        months.add(month)
        rdict = RDict()
        ddict = RDict()
        for row in items:
            summary = row['columns'][0][:summary_width]
            rhc = row['columns'][1]
            path = row['path']
            description = row['description']
            values = [f"{summary}: {rhc}", row['columns'][2]
                    ] 
            try:
                rdict.add(path, tuple(values))
            except Exception as e:
                logger.error(f"error adding path: {path}, values: {values}: {e}")
            if description:
                values.append(description)
            try:
                ddict.add(path, tuple(values))
            except Exception as e:
                logger.error(f"error adding path: {path}, values: {values}: {e}")
        tree, row2id = rdict.as_tree(rdict, level=0)
        used_details[month] = tree
        used_details2id[month] = row2id
        dtree, drow2id = ddict.as_tree(ddict, level=0)
        used_description[month] = dtree
        used_description2id[month] = drow2id

    keys = [x for x in used_time]
    keys.sort()
    for key in keys:
        period = used_time[key]
        month_rows.setdefault(key[0], [])
        indent = (len(key) - 1) * 3 * " "
        if len(key) == 1:
            yrmnth = pendulum.from_format(key[0] + "-01", "YYYY-MM-DD").format("MMMM YYYY")
            try:
                rhc = f"{format_hours_and_tenths(period)}"
                summary = f"{indent}{yrmnth}: {rhc}"[:summary_width]
                month_rows[key[0]].append(f"{summary}")
            except Exception as e:
                logger.error(f"e: {repr(e)}")

        else:
            rhc = f"{format_hours_and_tenths(period)}"
            summary = f"{indent}{key[-1]}: {rhc}"[:summary_width].ljust(summary_width, ' ')
            month_rows[key[0]].append(f"{summary}")

    for key, val in month_rows.items():
        used_summary[key] = "\n".join(val)

    return used_details, used_details2id, used_summary, used_description, used_description2id

Strategy:
    Prepare and execute query to fetch the appropriate records.
    * get records with @u entries
    * filter to match conditions
        * toss if if -b bdt is given and all @u entries occured before bdt
        * toss if -e edt is given and all @u entries occured after edt
        * toss if -i indx is given and either @i is missing or its value does not start with indx
        * toss if -t tags is given and either @t is missing or none of its values are in tags
        * toss if -l loc is given and either @l is missing or its value does not match loc
        * toss if -c cal is given and either @c is missing or it's value does not match cal
"""
def report(required_fields, filters):
    required_fields = ['u', 'i']


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
        print('format_duration', e)
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
    return ok_items


def format_duration(obj, short=True):
    """
    if short report only hours and minutes, else include weeks and days
    >>> td = pendulum.duration(weeks=1, days=2, hours=3, minutes=27)
    >>> format_duration(td)
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
        print('format_duration', e)
        print(obj)
        return None

class RDict(dict):
    """
    Constructed from rows of (path, values) tuples. The path will be split using 'split_char' to produce the nodes leading to 'values'. The last element in values is presumed to be the 'id' of the item that generated the row. 
    """

    tab = 2

    # def __init__(self, split_char='/', used_time={}):
    def __init__(self, used_time={}):
        self.width = shutil.get_terminal_size()[0]
        self.row = 0
        self.row2id = {}
        self.output = []
        # self.split_char = split_char
        self.used_time = used_time

    def __missing__(self, key):
        self[key] = RDict()
        return self[key]

    def as_dict(self):
        return self

    def leaf_detail(self, detail, depth):
        dindent = RDict.tab * (depth + 1) * " "
        paragraphs = detail.split('\n')
        ret = []
        for para in paragraphs:
            ret.extend(textwrap.fill(para, initial_indent=dindent, subsequent_indent=dindent, width=self.width-RDict.tab*(depth-1)).split('\n'))
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
            indent = RDict.tab * depth * " "
            if self.used_time:
                self.output.append("%s%s: %s" % (indent,  k, format_duration(self.used_time.get(tuple(pre), ''))))
            else:
                self.output.append("%s%s" % (indent,  k))
            self.row += 1 
            depth += 1
            if level and depth > level:
                depth -= 1
                continue

            if type(t[k]) == RDict:
                self.as_tree(t[k], depth, level, pre)
            else:
                for leaf in t[k]:
                    indent = RDict.tab * depth * " "
                    if self.used_time:
                        self.output.append("%s%s %s: %s" % (indent, leaf[0], leaf[1], format_duration(leaf[2])))
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
        return "\n".join(self.output), self.row2id


def get_sort_and_path(items, grpby):
    used_time = {}
    ret = []
    sort_tups = [x for x in grpby.get('sort', [])]
    path_tups = [x for x in grpby.get('path', [])]
    dtls_tups  = [x for x in grpby.get('dtls', [])]
    # print("sort_tups:", sort_tups)
    # print("path_tups:", path_tups)
    # print("dtls_tups:", dtls_tups)
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
    # pprint(used_time)


    # create recursive dict from data
    index = RDict(used_time)
    for path, value in ret:
        index.add(path, value)

    # print("\nindex pprint")
    # pprint(index)

    # print("\nindex as_tree")
    output, row2id = index.as_tree(index)
    print(output)
    pprint(row2id)


def str2opts(s, options=None):

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
            dt = parse_datetime(part[1:])
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


def main():

    # view.item_details = item_details
    # settings = options.Settings(etmdir).settings
    # secret = settings.get('secret')
    # data.secret = secret

    # from etm.view import Query
    query = ETMQuery()

    session = PromptSession()

    again = True
    while again:

        text = session.prompt("query: ", lexer=query.lexer)
        if not text:
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
        print(f"query: {text}")
        if text.startswith('u') or text.startswith('c'):
            # if len(text.strip()) == 1:
            #     continue
            grpby, filters = str2opts(text)
            if not grpby:
                continue
            print(f"grpby: {grpby}\n\nfilters: {filters}")
            ok, items = query.do_query(filters.get('query'))
            if ok:
                items = apply_dates_filter(items, grpby, filters)
                get_sort_and_path(items, grpby)
                # for item in items:
                #     print(f"   {item['itemtype']} {item.get('summary', 'none')} {item.doc_id} {item.get('rdt')}")
            else:
                pass
                # print(items)
        else:
            ok, items = query.do_query(text)

            if ok:
                for item in items:
                    print(f"   {item['itemtype']} {item.get('summary', 'none')} {item.doc_id}")
            else:
                pass
                # print(items)

# text = prompt('query: ', lexer=PygmentsLexer(etm_style))
# print('You said: %s' % text)

if __name__ == "__main__":
    if not (len(sys.argv) == 2 and os.path.isdir(sys.argv[1])):
        sys.exit()
    etmdir = sys.argv[1]
    dbfile = os.path.normpath(os.path.join(etmdir, 'db.json'))
    ETMDB = data.initialize_tinydb(dbfile)
    DBITEM = ETMDB.table('items', cache_size=None)
    DBARCH = ETMDB.table('archive', cache_size=None)
    view.ETMDB = ETMDB
    view.DBITEM = DBITEM
    view.DBARCH = DBARCH
    # setup_logging = options.setup_logging
    # setup_logging(loglevel, logdir)
    # options.logger = logger
    settings = options.Settings(etmdir).settings
    UT_MIN = settings.get('usedtime_minutes', 1)
    # print(f"UT_MIN: {UT_MIN}")
    main()
