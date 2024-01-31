import os

# import math
import sys
import shutil
import textwrap
import re
import csv
from dateutil.parser import parse as dateutil_parse
from dateutil.parser import parserinfo

from copy import deepcopy

# from etm.__main__ import setup_logging

from tinydb import where, Query

from prompt_toolkit import PromptSession

from etm.view import ETMQuery, format_week

from etm.model import format_datetime, parse, parse_duration, fmt_week

from etm.model import format_hours_and_tenths
import etm.data as data
from etm.common import (
    parse,
    ETM_CHAR,
    Period,
)
import itertools
from itertools import groupby

flatten = itertools.chain.from_iterable
from operator import itemgetter
from datetime import datetime, date, timedelta

ZERO = timedelta(seconds=0)
ONEMIN = timedelta(seconds=60)

finished_char = '\u2713'  #  ✓

minus_regex = re.compile(r'\s+\-(?=[a-zA-Z])')
groupdate_regex = re.compile(
    r'\bW{1,4}\b|\bY{1,4}\b|\b[M]{1,4}\b|\bd{3,4}\b|\b[D]{1,2}\b|\b[w]\b'
)


ETMDB = None
DBITEM = None
DBARCH = None

# pendulum to datetime format conversions
p2d = {
    'YY': '%y',
    'YYYY': '%Y',
    'M': '%-m',
    'MM': '%m',
    'MMM': '%b',
    'MMMM': '%B',
    'D': '%-d',
    'DD': '%d',
    'ddd': '%a',
    'dddd': '%A',
}


def daybeg():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


def dayend():
    return datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)


def weekbeg():
    d = daybeg()
    return d - timedelta(days=d.weekday())


def weekend():
    d = dayend()
    return d + timedelta(days=6 - d.weekday())


def monthbeg():
    d = daybeg()
    return d.replace(day=1)


def monthend():
    mb = monthbeg()
    (y, m) = (mb.year, mb.month + 1) if mb.month < 12 else (mb.year + 1, 1)
    return mb.replace(year=y, month=m) - timedelta(seconds=1)


def prevmonthend():
    return monthbeg() - timedelta(seconds=1)


def prevmonthbeg():
    me = prevmonthend()
    return me.replace(day=1)


date_shortcuts = {
    'daybeg': daybeg,
    'dayend': dayend,
    'weekbeg': weekbeg,
    'weekend': weekend,
    'monthbeg': monthbeg,
    'monthend': monthend,
    'prevmonthbeg': prevmonthbeg,
    'prevmonthend': prevmonthend,
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
    if sign:
        if s[0] in ['+', '-']:
            dtm = ''
            dur = s[1:]
        else:
            parts = [x.strip() for x in re.split(r'[+-]\s', s)]
            dtm = parts[0]
            dur = parts[1] if len(parts) > 1 else ''
    else:
        dtm = s.strip()
        dur = ''
    if dtm in date_shortcuts:
        dt = date_shortcuts[dtm]()
    else:
        dt = parse(dtm)
    if dur:
        ok, du = parse_duration(dur)
    else:
        du = ZERO
    return dt + du if sign == '+' else dt - du


def _fmtdt(dt):
    # assumes dt is either a date or a datetime
    try:
        # this works if dt is a datetime
        # return dt.format("%YMMDDHHmm")
        return dt.strftime('%Y%m%d%H%M')
    except:
        # this works if dt is a date by providing 00 for HH and mm
        # return dt.format("%YMMDD0000")
        return dt.strftime('%Y%m%d0000')


def later(d1, d2):
    """
    True if d1 > d2
    """
    if not (isinstance(d1, date) and isinstance(d2, date)):
        # each must be a date or a datetime
        return 'only dates or datetimes can be compared'
    return _fmtdt(d1) > _fmtdt(d2)


def earlier(d1, d2):
    """
    True if d1 < d2
    """
    if not (isinstance(d1, date) and isinstance(d2, date)):
        # each must be a date or a datetime
        return 'only dates or datetimes can be compared'
    return _fmtdt(d1) < _fmtdt(d2)


def maybe_round(obj):
    """
    round up to the nearest UT_MIN minutes.
    """

    if isinstance(obj, Period):
        obj = obj.diff
    if not isinstance(obj, timedelta):
        return None
    if UT_MIN == 0:
        return obj
    seconds = int(obj.total_seconds()) % 60
    if seconds:
        # round up to the next minute
        obj = obj + timedelta(seconds=60 - seconds)

    res = (obj.total_seconds() // 60) % UT_MIN
    if res:
        obj += (UT_MIN - res) * ONEMIN
    return obj


def sort_dates_times(obj):
    if isinstance(obj, date):
        return obj.strftime('%Y-%m-%d 00:00')
    if isinstance(obj, dateTime):
        return obj.strftime('%Y-%m-%d %H:%M')
    else:
        return obj


def apply_dates_filter(items, grpby, filters):
    if grpby['report'] in ['u', 'v']:

        def rel_dt(item, filters):
            rdts = []
            ok = False
            used_times = deepcopy(item['u'])
            drop = []
            if 'b' in filters and 'e' in filters:   # both b and e
                for x in used_times:
                    if earlier(x[1], filters['b']) or later(
                        x[1], filters['e']
                    ):
                        drop.append(x)
            elif 'b' in filters:   # only b
                for x in used_times:
                    if earlier(x[1], filters['b']):
                        drop.append(x)
            elif 'e' in filters:   # only e
                for x in used_times:
                    if later(x[1], filters['e']):
                        drop.append(x)
            if drop:
                for x in drop:
                    used_times.remove(x)
            items = []
            dt2ut = {}
            for x in used_times:
                rdt = x[1] if isinstance(x[1], date) else x[1].date()
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
                rdt = (
                    item['f']
                    if isinstance(item['f'], date)
                    else item['f'].date()
                )
                # e_ok = 'e' not in filters or item['f'] <= filters['e']
                e_ok = 'e' not in filters or not later(item['f'], filters['e'])
                # b_ok = 'b' not in filters or item['f'] >= filters['b']
                b_ok = not (
                    'b' in filters and earlier(item['f'], filters['b'])
                )
            elif 's' in item:
                rdt = (
                    item['s']
                    if isinstance(item['s'], date)
                    else item['s'].date()
                )
                # e_ok = 'e' not in filters or rdt <= filters['e']
                e_ok = not ('e' in filters and later(item['s'], filters['e']))
                # b_ok = 'b' not in filters or rdt >= filters['b']
                b_ok = 'b' not in filters or not earlier(
                    item['s'], filters['b']
                )
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
    return ok_items


class QDict(dict):
    """
    Constructed from rows of (path, values) tuples. The path will be split using 'split_char' to produce the nodes leading to 'values'. The last element in values is presumed to be the 'id' of the item that generated the row.
    """

    tab = 2

    def __init__(self, used_time={}, row=0, needs=[]):
        self.width = shutil.get_terminal_size()[0] - 4   # -2 for query indent
        self.row = row
        self.needs = needs
        self.row2id = {}
        self.output = []
        self.csv = []   # list of hsh col_num -> value
        self.used_time = used_time

        self.fmt = ''
        if self.needs:
            fmts = {'y': '%y', 'm': '%-m', 'd': '%-d'}
            tmp = []
            if settings['yearfirst'] and not settings['dayfirst']:
                for x in ['y', 'm', 'd']:
                    if x in self.needs:
                        tmp.append(fmts[x])
            else:
                for x in ['d', 'm', 'y']:
                    if x in self.needs:
                        tmp.append(fmts[x])
            self.fmt = '/'.join(tmp)
            if settings['ampm']:
                self.fmt += ' %-I:%M%p'
            else:
                self.fmt += '%H:%M'

    def __missing__(self, key):
        self[key] = QDict()
        return self[key]

    def as_dict(self):
        logger.debug(f'as dict: {self}')
        return self

    def leaf_detail(self, detail, depth):
        dindent = QDict.tab * (depth + 1) * ' '
        if isinstance(detail, str):
            paragraphs = detail.split('\n')
            ret = []
            for para in paragraphs:
                ret.extend(
                    textwrap.fill(
                        para,
                        initial_indent=dindent,
                        subsequent_indent=dindent,
                        width=self.width - QDict.tab * (depth - 1),
                    ).split('\n')
                )
        elif isinstance(detail, datetime):
            ret = [dindent + format_datetime(detail, short=True)[1]]
        elif isinstance(detail, timedelta):
            ret = [dindent + format_hours_and_tenths(detail)]
        elif isinstance(detail, list) and detail:
            if isinstance(detail[0], str):
                ret = [dindent + ', '.join(detail)]
            elif isinstance(detail[0], list):
                # u, e.g., will be a list of duration, datetime tuples
                ret = []
                detail.sort(key=lambda x: sort_dates_times(x[1]))
                for d in detail:
                    try:
                        tmp = f'{format_hours_and_tenths(d[0])}: {format_datetime(d[1], short=True)[1]}'
                        ret.append(dindent + tmp)
                    except Exception as e:
                        # logger.error(f'error {e}, processing {d}')
                        ret.append(dindent + repr(d))
            else:
                ret = []
                try:
                    tmp = f'{format_datetime(detail[0], short=True)[1]}: {format_hours_and_tenths(detail[1])}'
                    ret.append(dindent + tmp)
                except Exception as e:
                    # logger.error(f'error {e}, processing {detail}')
                    ret.append(dindent + repr(detail))

        else:
            ret = [dindent + repr(detail)]
        return ret

    def add(self, keys, values=()):
        for j in range(len(keys)):
            key = keys[j]
            keys_left = keys[j + 1 :]
            if not keys_left:
                try:
                    self.setdefault(key, []).append(values)
                except Exception as e:
                    logger.warning(
                        f'error adding key: {key}, values: {values}\n self: {self}; e: {repr(e)}'
                    )
            if isinstance(self[key], dict):
                self = self[key]
            elif keys_left:
                self.setdefault(':'.join(keys[j:]), []).append(values)
                break

    def as_tree(self, t={}, depth=0, level=0, pre=[]):
        """return an indented tree"""
        for k in t.keys():
            del pre[depth:]
            pre.append(k)
            indent = QDict.tab * depth * ' '
            if self.used_time:
                self.output.append(
                    '%s%s %s'
                    % (
                        indent,
                        k,
                        format_hours_and_tenths(
                            self.used_time.get(tuple(pre), '')
                        ),
                    )
                )
            else:
                self.output.append('%s%s' % (indent, k))
            self.row += 1
            depth += 1
            if level and depth > level:
                depth -= 1
                continue

            if type(t[k]) == QDict:
                self.as_tree(t[k], depth, level, pre)
            else:
                for leaf in t[k]:
                    indent = QDict.tab * depth * ' '
                    l_indent = len(indent)
                    ut = format_hours_and_tenths(leaf[2])
                    # dt = leaf[3].strftime('%d %H:%M')
                    # dt = format_datetime(leaf[3], short=True)[1]
                    dt = leaf[3].strftime(self.fmt).rstrip('M').lower()
                    avail = self.width - l_indent - len(ut) - len(dt) - 4
                    if len(leaf[1]) > avail:
                        leaf[1] = (
                            leaf[1][: avail - 1] + ETM_CHAR['ELLIPSiS_CHAR']
                            if len(leaf[1]) >= avail
                            else leaf[1]
                        )
                    if self.used_time:
                        self.output.append(
                            f'{indent}{leaf[0]} {ut} {dt} {leaf[1]}'
                            # '%s%s %s: %s %s'
                            # % (indent, leaf[0], dt, leaf[1], ut)
                        )
                        num_leafs = 4
                    else:
                        self.output.append(
                            '%s%s %s' % (indent, leaf[0], leaf[1])
                        )
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
        return '\n  '.join(self.output), self.row2id

    def as_csv(self, t={}, depth=0, level=0, pre=[]):
        """return a list of CSV rows"""
        # pre will contain the header elements to begin each row
        for k in t.keys():
            del pre[depth:]
            pre.append(k)
            # indent = depth * [
            #     ' ',
            # ]
            # tmp.extend(indent)
            if self.used_time:
                header = f"{'/'.join(tuple(pre))} {format_hours_and_tenths(self.used_time.get(tuple(pre), ''))}"
                # header = f"{pre} {format_hours_and_tenths(self.used_time.get(tuple(pre), ''))}"

            else:
                header = f'{pre}'
            # self.csv.append(tmp)
            # self.row += 1
            depth += 1
            if level and depth > level:
                depth -= 1
                continue

            if type(t[k]) == QDict:
                self.as_csv(t[k], depth, level, pre)
            else:
                for leaf in t[k]:
                    row = []
                    row.append(header)
                    ut = format_hours_and_tenths(leaf[2])
                    dt = leaf[3].strftime('%Y-%m-%d %H:%M')
                    if self.used_time:
                        row.extend([ut, dt, leaf[0], leaf[1]])
                        num_leafs = 4
                    else:
                        row.extend([leaf[0], leaf[1]])
                        num_leafs = 2
                    for i in range(num_leafs, len(leaf) - 1):
                        row.append(leaf[i])
                    row.append(leaf[-1])
                    self.csv.append(row)
            depth -= 1
        return self.csv


def get_output_and_row2id(items, grpby, header='', needs=[]):
    used_time = {}
    ret = []
    report = grpby['report']
    sort_tups = [x for x in grpby.get('sort', [])]
    path_tups = [x for x in grpby.get('path', [])]
    dtls_tups = [x for x in grpby.get('dtls', [])]
    mode = header[0]
    for item in items:
        for x in ['i', 'c', 'l']:
            item.setdefault(x, '~')   # make ~ the default
        item.setdefault('modified', item['created'])
        if 'f' in item:
            item['itemtype'] = '-' if report in ['u', 'v'] else finished_char
        st = [
            eval(x, {'item': item, 're': re, 'format_week': format_week})
            for x in sort_tups
            if x
        ]
        pt = []
        for y in path_tups:
            if not y:
                continue
            if isinstance(y, list):
                pt.append(
                    ' '.join(
                        [
                            eval(
                                x,
                                {
                                    'item': item,
                                    're': re,
                                    'format_week': format_week,
                                },
                            )
                            for x in y
                            if x
                        ]
                    )
                )
            else:
                pt.append(
                    eval(
                        y, {'item': item, 're': re, 'format_week': format_week}
                    )
                )

        dt = []
        for x in dtls_tups:
            if not x:
                continue
            try:
                dt.append(eval(x, {'item': item, 're': re}))
            except Exception as e:
                logger.error(f'error: {e}, evaluating {x}')
        if grpby['report'] in ['u', 'v']:
            dt[2] = ut = maybe_round(dt[2])
            for i in range(len(pt)):
                key = tuple(pt[: i + 1])
                used_time.setdefault(key, ZERO)
                used_time[key] += ut
        ret.append((st, pt, dt))
    ret.sort(key=lambda x: x[0])

    # drop the sort key
    ret = [x[1:] for x in ret]
    # logger.debug(ret)

    # create recursive dict from data
    row = 1 if header else 0
    # need to pass 'needs' to QDict
    index = QDict(used_time, row, needs)
    for path, value in ret:
        index.add(path, value)

    if mode == 'v':
        # CVS stuff
        csv_rows = index.as_csv(index)
        now = datetime.now().astimezone().strftime('%y%m%dT%H%M%S')
        csvfile = os.path.join(csvdir, f'{now}.csv')
        header_row = [
            f'etm query: {header}',
            'hours',
            'datetime',
            'type',
            'summary',
        ]
        for x in dtls_tups[4:-1]:
            header_row.append(x)
        header_row.append('doc_id')

        csv_output = [
            header_row,
        ]
        csv_output.extend(csv_rows)
        with open(csvfile, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(csv_output)
        return (
            f'csv output saved to {csvfile}',
            {},
        )
    else:
        header = textwrap.fill(
            f'query: {header}',
            width=shutil.get_terminal_size()[0] - 2,
            initial_indent='',
            subsequent_indent='   ',
        )
        output, row2id = index.as_tree(index)
        return f'{header}\n  {output}', row2id


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
    if not (report and report in ['s', 'u', 'm', 'c', 'v']):
        return {}, {}
    grpby['report'] = report
    filters['dates'] = False
    grpby['dated'] = False
    grpby['path'] = False
    filters['query'] = (
        'exists u' if report in ['u', 'v'] else 'exists itemtype'
    )
    groupbylst = []
    if groupbystr:
        groupbylst = [x.strip() for x in groupbystr.split(';')]
        for comp in groupbylst:
            comp_parts = comp.split(' ')
            for part in comp_parts:
                if part[0] == 'i':
                    grpby['path'] = True
                elif groupdate_regex.match(part):
                    grpby['dated'] = True
                    filters['dates'] = True
                elif not (
                    part
                    in ['c', 'l', 'itemtype', 'created', 'modified', 'summary']
                ):
                    print(f'Ignoring invalid groupby part: {part}')
                    groupbylst.remove(comp)
        grpby['args'] = groupbylst
    grpby['path'] = []
    grpby['sort'] = []
    needs = ['y', 'm', 'd']
    if groupbylst:
        if grpby['path']:
            grpby['sort'].append()
        if grpby['dated'] or grpby['report'] in ['u', 'v', 'm', 'c']:
            grpby['sort'].append(f"item['rdt'].strftime('%Y%m%d')")
        for group in groupbylst:
            if groupdate_regex.search(group):
                gparts = group.split(' ')
                this_sort = []
                this_path = []
                for part in gparts:
                    if 'W' in part:
                        this_sort.append("item['rdt'].strftime('%W')")
                        this_path.append(
                            f"format_week(item['rdt'], {p2d[part]})"
                        )
                    if 'Y' in part:
                        needs.remove('y')
                        this_sort.append("item['rdt'].strftime('%Y')")
                        this_path.append(
                            f"item['rdt'].strftime('{p2d[part]}')"
                        )
                    if 'M' in part:
                        needs.remove('m')
                        this_sort.append("item['rdt'].strftime('%m')")
                        this_path.append(
                            f"item['rdt'].strftime('{p2d[part]}')"
                        )
                    if 'D' in part:
                        needs.remove('d')
                        this_sort.append("item['rdt'].strftime('%d')")
                        this_path.append(
                            f"item['rdt'].strftime('{p2d[part]}')"
                        )
                    if 'd' in part:
                        this_path.append(
                            f"item['rdt'].strftime('{p2d[part]}')"
                        )
                grpby['sort'].extend(this_sort)
                grpby['path'].append(this_path)

            elif '[' in group and group[0] == 'i':
                if ':' in group:
                    grpby['path'].append(
                        f"'/'.join(re.split('/', item['{group[0]}']){group[1:]}) or '~'"
                    )
                    grpby['sort'].append(
                        f"'/'.join(re.split('/', item['{group[0]}']){group[1:]}) or '~'"
                    )
            else:
                grpby['path'].append("item['%s']" % group.strip())
                grpby['sort'].append(f"item['{group.strip()}']")

    also = []
    for part in parts:
        key = part[0]
        if key == 'a':
            value = [x.strip() for x in part[1:].split(',')]
            also.extend(value)
        elif key in ['b', 'e']:
            dt = parse_reldt(part[1:])
            filters[key] = dt
        elif key == 'q':
            value = part[1:].strip()
            filters['query'] += f' and {value}'
        elif key == 't':
            value = [x.strip() for x in part[1:].split(',')]
    details = ["item['itemtype']", "item['summary']"]
    if report in ['u', 'v']:
        details.append("item['u'][1]")
        details.append("item['u'][0]")
    else:
        details.append('')
    if also:
        details.extend([f"item.get('{x}', '~')" for x in also])
    details.append('item.doc_id')
    grpby['dtls'] = details
    return grpby, filters, needs


def show_query_results(text, grpby, items, needs):
    # called by dataview to set query
    item_count = f'[{len(items)} records]'
    if not (items and isinstance(items, list)):
        return f'query: {text}\n   none matching', {}
    header = f'{text} {item_count}'
    # need to pass 'needs' to get_output_and_row2id
    output, row2id = get_output_and_row2id(items, grpby, header, needs)
    return output, row2id


def main(etmdir, args):

    query = ETMQuery()
    session = PromptSession()
    again = True
    while again:
        print("Enter 'quit', 'stop', 'exit' or '' to exit loop")
        text = session.prompt('query: ', lexer=query.lexer)
        if not text or text in ['quit', 'stop', 'exit']:
            again = False
            continue
        if text == 'd':   # with descriptions
            text = 'u i[0]; MMM YYYY; i[1:]; ddd D -b 3/1 -e 4/1 -a d'
        elif text == 'p':   # without descriptions
            text = 'u i[0]; MMM YYYY; i[1:]; ddd D -b 3/1 -e 4/1'
        elif text == 'w':   # without descriptions and days
            text = 'u i[0]; MMM YYYY; i[1:] -b 1/1 -e 3/1'
        elif text == 'a':   # client a only
            text = 'u i[0]; MMM YYYYY; i[1:] -q matches i client\\sa -b 1/1 -e 3/1 -a d'
        elif len(text.strip()) == 1:
            print('missing report arguments')
            continue
        print(f'query: {text}')
        if (
            len(text) > 1
            and text[1] == ' '
            and text[0] in ['s', 'u', 'm', 'c']
        ):
            grpby, filters = get_grpby_and_filters(text)
            if not grpby:
                continue
            print(f'grpby: {grpby}\n\nfilters: {filters}')
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
                    print(
                        f"   {item['itemtype']} {item.get('summary', 'none')} {item.doc_id}"
                    )
            else:
                print(items)


if __name__ == '__main__':
    print('This module should only be imported')
    sys.exit()
    # main(*sys.argv[1:])
