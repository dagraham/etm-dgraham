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
from pendulum import duration
import itertools
from itertools import groupby
flatten = itertools.chain.from_iterable
from operator import itemgetter

ZERO = duration(minutes=0)
ONEMIN = duration(minutes=1)

finished_char = u"\u2713"  #  ✓

minus_regex = re.compile(r'\s+\-(?=[a-zA-Z])')
groupdate_regex = re.compile(r'\bW{1,4}\b|\bY{2}\b|\bY{4}\b|\b[M]{1,4}\b|\bd{1,4}\b|\b[D]{1,2}\b|\b[w]\b')

# supported date formats (subset of pendulum)
# YYYY        year 2019
# YY          year 19
# MMMM        month January
# MMM         month Jan
# MM          month 01
# M           month 1
# DD          month day 09
# D           month day 9
# dddd        week day Monday
# ddd         week day Mon
# dd          week day Mo
# week add ons, eg week 3 2020
# W           week number of year, 3
# WW          month days interval, Jan 13 - 19
# WWW         interval plus year,  Jan 13 - 19, 2020
# WWWW        interval, year and #, Jan 13 -19, 2020 #3

ETMDB = None
DBITEM = None
DBARCH = None

def daybeg():
    return pendulum.now().replace(hour=0, minute=0, second=0, microsecond=0)

def dayend():
    return daybeg() + duration(days=1)

def weekbeg():
    d = daybeg()
    return d - duration(days=d.weekday())

def weekend():
    d = daybeg()
    return d + duration(days=7-d.weekday())

def monthbeg():
    return daybeg().replace(day=1)

def monthend():
    return monthbeg() + duration(months=1)



date_shortcuts = {
        'daybeg': daybeg,
        'dayend': dayend,
        'weekbeg': weekbeg,
        'weekend': weekend,
        'monthbeg': monthbeg,
        'monthend': monthend,
        }


def parse_reldt(s):
    """
    s takes the form datetime str [+-] duration str
    """
    msg = []
    plus = r'\s[+]\s'
    minus = r'\s[-]\s'
    sign = ''
    if re.search(plus, s):
        sign = '+'
    elif re.search(minus, s):
        sign = '-'
    logger.debug(f"s: {s}; sign: {sign}")
    if sign:
        if s[0] in ['+', '-']:
            dtm = ''
            dur = s[1:]
        else:
            parts = [x.strip() for x in re.split(r'[+-]\s', s)]
            dtm = parts[0]
            dur = f"{sign}{parts[1]}" if len(parts) > 1 else ''
    else:
        dtm = s.strip()
        dur = ''
    logger.debug(f"dtm: {dtm}; dur: {dur}")
    if dtm in date_shortcuts:
        dt = date_shortcuts[dtm]()
    else:
        dt = pendulum.parse(dtm, strict=False, tz='local')
    logger.debug(f"dt: {dt}")
    if dur:
        ok, du = parse_duration(dur)
    else:
        du = pendulum.Duration()
    logger.debug(f"dt: {dt}, du: {du}, dt+du: {dt+du}")
    return dt + du


def _fmtdt(dt):
    # assumes dt is either a date or a datetime
    try:
        # this works if dt is a datetime
        return dt.format("YYYYMMDDHHmm")
    except:
        # this works if dt is a date by providing 00 for HH and mm
        return dt.format("YYYYMMDD0000")


def later(d1, d2):
    """
    True if d1 > d2
    """
    if not (isinstance(d1, pendulum.Date) and isinstance(d2, pendulum.Date)):
        # each must be a date or a datetime
        return "only pendulum dates or datetimes can be compared"
    return _fmtdt(d1) > _fmtdt(d2)

def earlier(d1, d2):
    """
    True if d1 < d2
    """
    if not (isinstance(d1, pendulum.Date) and isinstance(d2, pendulum.Date)):
        # each must be a date or a datetime
        return "only pendulum dates or datetimes can be compared"
    return _fmtdt(d1) < _fmtdt(d2)

def format_week(dt, fmt="WWW"):
    """
    """
    if fmt.endswith(','):
        add_comma = ','
        fmt = fmt[:-1]
    else:
        add_comma = ''

    if fmt == "W":
        return str(dt.week_of_year) + add_comma

    dt_year, dt_week = dt.isocalendar()[:2]

    if fmt == "WWW":
        year_week = f", {dt_year}"
    elif fmt == "WWWW":
        year_week = f", {dt_year} #{dt_week}"
    else:
        year_week = ""


    mfmt = "MMM D"

    wkbeg = pendulum.parse(f"{dt_year}-W{str(dt_week).rjust(2, '0')}")
    wkend = pendulum.parse(f"{dt_year}-W{str(dt_week).rjust(2, '0')}-7")
    week_begin = wkbeg.format(mfmt)
    if wkbeg.month == wkend.month:
        week_end = wkend.format("D")
    else:
        week_end = wkend.format(mfmt)
    return f"{week_begin} - {week_end}{year_week}{add_comma}"


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
        print('format_hours_and_tenths', e)
        print(obj)
        return None

def sort_dates_times(obj):
    if isinstance(obj, pendulum.Date):
        return obj.format("YYYY-MM-DD 00:00")
    if isinstance(obj, pendulum.DateTime):
        return obj.format("YYYY-MM-DD HH:mm")
    else:
        return obj


def apply_dates_filter(items, grpby, filters):
    logger.debug(f"starting len(items): {len(items)}; filters: {filters}")
    if grpby['report'] == 'u':
        def rel_dt(item, filters):
            rdts = []
            ok = False
            used_times = deepcopy(item['u'])
            drop = []
            if 'b' in filters and 'e' in filters: # both b and e
                for x in used_times:
                    if earlier(x[1], filters['b']) or later(x[1], filters['e']):
                        drop.append(x)
            elif 'b' in filters: # only b
                for x in used_times:
                    if earlier(x[1], filters['b']):
                        drop.append(x)
            elif 'e' in filters: # only e
                for x in used_times:
                    if later(x[1], filters['e']):
                        drop.append(x)
            if drop:
                for x in drop:
                    used_times.remove(x)
            items = []
            dt2ut = {}
            for x in used_times:
                rdt = x[1] if isinstance(x[1], pendulum.Date) else x[1].date()
                dt2ut.setdefault(rdt, ZERO)
                dt2ut[rdt] += maybe_round(x[0])
            for rdt in dt2ut:
                tmp = deepcopy(item)
                tmp['rdt'] = rdt
                tmp['u'] = [rdt, dt2ut[rdt]]
                items.append(tmp)
            return items

    elif grpby['report'] == 's':
        def rel_dt(item, filters):
            ok = False
            items = []
            tmp = deepcopy(item)
            rdt = None
            if 'f' in item:
                rdt = item['f'] if isinstance(item['f'], pendulum.Date) else item['f'].date()
                # e_ok = 'e' not in filters or item['f'] <= filters['e']
                e_ok = 'e' not in filters or not later(item['f'], filters['e'])
                # b_ok = 'b' not in filters or item['f'] >= filters['b']
                b_ok = not ('b' in filters and earlier(item['f'], filters['b']))
            elif 's' in item:
                rdt = item['s'] if isinstance(item['s'], pendulum.Date) else item['s'].date()
                # e_ok = 'e' not in filters or rdt <= filters['e']
                e_ok = not ('e' in filters and later(item['s'], filters['e']))
                # b_ok = 'b' not in filters or rdt >= filters['b']
                b_ok = 'b' not in filters or not earlier(item['s'], filters['b'])
            else:
                e_ok = b_ok = True
            if e_ok and b_ok:
                if grpby['dated']:
                    if rdt:
                        tmp['rdt'] = rdt
                        items.append(tmp)
                else:
                    # not dated, don't need rdt
                    items.append(tmp)
            return items

    elif grpby['report'] == 'c':
        def rel_dt(item, filters):
            ok = False
            items = []
            tmp = deepcopy(item)
            rdt = item['created']
            # e_ok = 'e' not in filters or rdt <= filters['e']
            e_ok = 'e' not in filters or not later(rdt, filters['e'])
            # b_ok = 'b' not in filters or rdt >= filters['b']
            b_ok = 'b' not in filters or not earlier(rdt, filters['b'])
            if e_ok and b_ok:
                if rdt:
                    tmp['rdt'] = rdt
                    items.append(tmp)
                else:
                    # not dated, don't need rdt
                    items.append(tmp)
            return items

    elif grpby['report'] == 'm':
        def rel_dt(item, filters):
            ok = False
            items = []
            tmp = deepcopy(item)
            rdt = item.get('modified', item['created'])
            # e_ok = 'e' not in filters or rdt <= filters['e']
            e_ok = 'e' not in filters or not later(rdt, filters['e'])
            # b_ok = 'b' not in filters or rdt >= filters['b']
            b_ok = 'b' not in filters or not earlier(rdt, filters['b'])
            if e_ok and b_ok:
                if rdt:
                    tmp['rdt'] = rdt
                    items.append(tmp)
                else:
                    # not dated, don't need rdt
                    items.append(tmp)
            return items

    ok_items = []
    for item in items:
        ok_items.extend(rel_dt(item, filters))
    logger.debug(f"ending len(ok_items): {len(ok_items)}")
    return ok_items


class QDict(dict):
    """
    Constructed from rows of (path, values) tuples. The path will be split using 'split_char' to produce the nodes leading to 'values'. The last element in values is presumed to be the 'id' of the item that generated the row.
    """

    tab = 2

    def __init__(self, used_time={}, row=0):
        self.width = shutil.get_terminal_size()[0] - 2 # -2 for query indent
        self.row = row
        self.row2id = {}
        self.output = []
        self.used_time = used_time

    def __missing__(self, key):
        self[key] = QDict()
        return self[key]

    def as_dict(self):
        return self

    def leaf_detail(self, detail, depth):
        dindent = QDict.tab * (depth + 1) * " "
        if isinstance(detail, str):
            paragraphs = detail.split('\n')
            ret = []
            for para in paragraphs:
                ret.extend(textwrap.fill(para, initial_indent=dindent, subsequent_indent=dindent, width=self.width - QDict.tab*(depth-1)).split('\n'))
        elif isinstance(detail, pendulum.DateTime):
            ret = [dindent + format_datetime(detail, short=True)[1]]
        elif isinstance(detail, pendulum.Duration):
            ret = [dindent + format_hours_and_tenths(detail)]
        elif isinstance(detail, list) and detail:
            if isinstance(detail[0], str):
                ret = [dindent + ", ".join(detail)]
            elif isinstance(detail[0], list):
                # u, e.g., will be a list of duration, datetime tuples
                ret = []
                detail.sort(key=lambda x: sort_dates_times(x[1]))
                for d in detail:
                    try:
                        tmp = f"{format_hours_and_tenths(d[0])}: {format_datetime(d[1], short=True)[1]}"
                        ret.append(dindent + tmp)
                    except Exception as e:
                        logger.error(f"error {e}, processing {d}")
                        ret.append(dindent + repr(d))
            else:
                ret = []
                try:
                    tmp = f"{format_datetime(detail[0], short=True)[1]}: {format_hours_and_tenths(detail[1])}"
                    ret.append(dindent + tmp)
                except Exception as e:
                    logger.error(f"error {e}, processing {detail}")
                    ret.append(dindent + repr(detail))

        else:
            ret = [dindent + repr(detail)]
        return ret


    def add(self, keys, values=()):
        for j in range(len(keys)):
            key = keys[j]
            keys_left = keys[j+1:]
            if not keys_left:
                try:
                    self.setdefault(key, []).append(values)
                except Exception as e:
                    logger.warning(f"error adding key: {key}, values: {values}\n self: {self}; e: {repr(e)}")
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
                self.output.append("%s%s: %s" % (indent,  k, format_hours_and_tenths(self.used_time.get(tuple(pre), ''))))
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
                        self.output.append("%s%s %s: %s" % (indent, leaf[0], leaf[1], format_hours_and_tenths(leaf[2])))
                        num_leafs = 3
                    else:
                        self.output.append("%s%s %s" % (indent, leaf[0], leaf[1]))
                        num_leafs = 2
                    self.row2id[self.row] = leaf[-1]
                    self.row += 1
                    # len(leaf) - 1 skips the last integer doc_id leaf
                    for i in range(num_leafs, len(leaf) - 1):
                        lines = self.leaf_detail(leaf[i], depth)
                        for line in lines:
                            self.output.append(line)
                            self.row += 1

            depth -= 1
        return "\n  ".join(self.output), self.row2id


def get_output_and_row2id(items, grpby, header=""):
    logger.debug(f"grpby: {grpby}; header: {header}")
    used_time = {}
    ret = []
    report = grpby['report']
    sort_tups = [x for x in grpby.get('sort', [])]
    path_tups = [x for x in grpby.get('path', [])]
    dtls_tups  = [x for x in grpby.get('dtls', [])]
    for item in items:
        for x in ['i', 'c', 'l']:
            item.setdefault(x, '~') # make ~ the default
        item.setdefault('modified', item['created'])
        if 'f' in item:
            item['itemtype'] = '-' if report == 'u' else finished_char
        st = [eval(x, {'item': item, 're': re, 'format_week': format_week}) for x in sort_tups if x]
        # pt = [eval(x, {'item': item, 're': re, 'format_week': format_week}) for x in path_tups if x]
        pt = []
        for y in path_tups:
            if not y:
                continue
            if isinstance(y, list):
                pt.append(" ".join([eval(x, {'item': item, 're': re, 'format_week': format_week}) for x in y if x]))
            else:
                pt.append(eval(y, {'item': item, 're': re, 'format_week': format_week}))

        dt = []
        for x in dtls_tups:
            if not x:
                continue
            try:
                dt.append(eval(x, {'item': item, 're': re}))
            except Exception as e:
                logger.error(f"error: {e}, evaluating {x}")
        if grpby['report'] == 'u':
            dt[2] = ut = maybe_round(dt[2])
            for i in range(len(pt)):
                key = tuple(pt[:i+1])
                used_time.setdefault(key, ZERO)
                used_time[key] += ut
        ret.append((st, pt, dt))
    ret.sort(key=lambda x: x[0])

    ret = [x[1:] for x in ret]

    # create recursive dict from data
    row = 1 if header else 0
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
    logger.debug(f"report: {report}")
    if not (report and report in ['s', 'u', 'm', 'c']):
        return {}, {}
    grpby['report'] = report
    filters['dates'] = False
    grpby['dated'] = False
    filters['query'] = "exists u" if report == 'u' else "exists itemtype"
    groupbylst = []
    if groupbystr:
        groupbylst = [x.strip() for x in groupbystr.split(';')]
        for comp in groupbylst:
            comp_parts = comp.split(' ')
            for part in comp_parts:
                if groupdate_regex.match(part):
                    grpby['dated'] = True
                    filters['dates'] = True
                elif not (
                    part[0] == 'i'
                    or part
                    in ['c', 'l', 'itemtype', 'created', 'modified', 'summary']
                ):
                    print(f"Ignoring invalid groupby part: {part}")
                    groupbylst.remove(comp)
        grpby['args'] = groupbylst
    grpby['path'] = []
    grpby['sort'] = []
    include = {'W', 'Y', 'M', 'D'}
    if groupbylst:
        for group in groupbylst:
            logger.debug(f"group: {group}")
            if groupdate_regex.search(group):
                gparts = group.split(' ')
                this_sort = []
                this_path = []
                for part in gparts:
                    if 'W' in part:
                        this_sort.append("item['rdt'].strftime('%W')")
                        this_path.append(f"format_week(item['rdt'], '{part}')")
                    if 'Y' in part:
                        this_sort.append("item['rdt'].format('YYYY')")
                        this_path.append(f"item['rdt'].format('{part}')")
                    if 'M' in part:
                        this_sort.append("item['rdt'].format('MM')")
                        this_path.append(f"item['rdt'].format('{part}')")
                    if 'D' in part:
                        this_sort.append("item['rdt'].format('DD')")
                        this_path.append(f"item['rdt'].format('{part}')")
                    if 'd' in part:
                        this_path.append(f"item['rdt'].format('{part}')")
                grpby['sort'].extend(this_sort)
                grpby['path'].append(this_path)


            elif '[' in group and group[0] == 'i':
                logger.debug(f"i group: {group[0]}, {group[1:]}")
                if ':' in group:
                    grpby['path'].append(
                            f"'/'.join(re.split('/', item['{group[0]}']){group[1:]}) or '~'")
                    grpby['sort'].append(
                            f"'/'.join(re.split('/', item['{group[0]}']){group[1:]}) or '~'")
                else:
                    logger.warning(f"non slice use of i: {group}")
            else:
                grpby['path'].append("item['%s']" % group.strip())
                grpby['sort'].append(f"item['{group.strip()}']")

        if grpby['dated'] or grpby['report'] in ['u', 'm', 'c']:
            grpby['sort'].append(f"item['rdt'].format('YYYYMMDD')")
    also = []
    for part in parts:
        key = part[0]
        if key == 'a':
            value = [x.strip() for x in part[1:].split(',')]
            also.extend(value)
        elif key in ['b', 'e']:
            # dt = parse(part[1:], strict=False, tz='local')
            dt = parse_reldt(part[1:])
            filters[key] = dt
        elif key == 'q':
            value = part[1:].strip()
            filters['query'] += f" and {value}"
        elif key == 't':
            value = [x.strip() for x in part[1:].split(',')]
    details = ["item['itemtype']", "item['summary']"]
    if report == 'u':
        details.append("item['u'][1]")
    else:
        details.append("")
    if also:
        details.extend([f"item.get('{x}', '~')" for x in also])
    details.append("item.doc_id")
    grpby['dtls'] = details
    logger.debug(f'get_grpby_and_filters: rgrpby: {grpby}; filters: {filters}')
    return grpby, filters

def show_query_results(text, grpby, items):
    width = shutil.get_terminal_size()[0] - 7
    rows = []
    item_count = f" [{len(items)}]"
    summary_width = width - 6 - len(item_count)
    if not (items and isinstance(items, list)):
        return f"query: {text}\n   none matching", {}
    header = f"query: {text[:summary_width]}{item_count}"
    output, row2id = get_output_and_row2id(items, grpby, header)
    return output, row2id


def main(etmdir, args):

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
        if len(self.query_text) > 1 and self.query_text[1] == ' ' and self.query_text[0] in ['s', 'u', 'm', 'c']:
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

