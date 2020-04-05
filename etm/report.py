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

ZERO = pendulum.duration(minutes=0)
ONEMIN = pendulum.duration(minutes=1)
DAY = pendulum.duration(days=1)

finished_char = u"\u2713"  #  ✓

minus_regex = re.compile(r'\s+\-(?=[a-zA-Z])')
groupdate_regex = re.compile(r'\bY{2}\b|\bY{4}\b|\b[M]{1,4}\b|\b[d]{2,4}\b|\b[D]{1,2}\b|\b[w]\b')

# supported date formats (subset of pendulum)
# 'YYYY',     # year 2019
# 'YY',       # year 19
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
                tmp['u'] = [rdt, dt2ut[rdt]]
                items.append(tmp)
            return items

    elif grpby['report'] == 'c':
        def rel_dt(item, filters):
            ok = False
            items = []
            tmp = deepcopy(item)
            rdt = None
            if 'f' in item:
                rdt = item['f'].date()
                e_ok = 'e' not in filters or item['f'] <= filters['e'] 
                b_ok = 'b' not in filters or item['f'] >= filters['b']
            elif 's' in item:
                rdt = item['s'].date()
                e_ok = 'e' not in filters or item['s'] <= filters['e'] 
                b_ok = 'b' not in filters or item['s'] >= filters['b']
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

    ok_items = []
    for item in items:
        ok_items.extend(rel_dt(item, filters))
    ok = len(ok_items) > 0
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
        elif isinstance(detail, list):
            if isinstance(detail[0], str):
                # logger.debug(f"detail list of str: {detail}")
                ret = [dindent + ", ".join(detail)]
            elif isinstance(detail[0], list):
                # u, e.g., will be a list of duration, datetime tuples
                ret = []
                detail.sort(key=lambda x: x[1])
                # logger.debug(f"detail list of lists: {detail}")
                for d in detail:
                    try:
                        tmp = f"{format_hours_and_tenths(d[0])}: {format_datetime(d[1], short=True)[1]}"
                        ret.append(dindent + tmp)
                    except Exception as e:
                        logger.error(f"error {e}, processing {d}")
                        ret.append(dindent + repr(d))
            else:
                ret = []
                # logger.debug(f"detail list: {detail}")
                try:
                    tmp = f"{format_datetime(detail[0], short=True)[1]}: {format_hours_and_tenths(detail[1])}"
                    ret.append(dindent + tmp)
                except Exception as e:
                    logger.error(f"error {e}, processing {detail}")
                    ret.append(dindent + repr(detail))

        else:
            # logger.debug(f"detail tyoe: {type(detail)}")
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
    # logger.debug(f"dtls_tups: {dtls_tups}")
    for item in items:
        for x in ['i', 'c', 'l']:
            item.setdefault(x, '~') # make ~ the default 
        if 'f' in item:
            item['itemtype'] = finished_char 
        st = [eval(x, {'item': item, 're': re}) for x in sort_tups if x]
        pt = [eval(x, {'item': item, 're': re}) for x in path_tups if x]
        dt = []
        for x in dtls_tups:
            if not x:
                continue
            try:
                dt.append(eval(x, {'item': item, 're': re}))
            except Exception as e:
                logger.error(f"error: {e}, evaluating {x}")
        if grpby['report'] == 'u':
            # logger.debug(f"dt: {dt}")
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
    filters['query'] = "exists u" if report == 'u' else "exists itemtype"
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
                elif part[0] not in ['i', 'c', 'l']:
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

            elif '[' in group and group[0] == 'i':
                logger.debug(f"i group: {group[0]}, {group[1:]}")
                if ':' in group:
                    grpby['path'].append(
                            f"'/'.join(re.split('/', item['{group[0]}']){group[1:]}) or '~'")
                    grpby['sort'].append(
                            f"'/'.join(re.split('/', item['{group[0]}']){group[1:]}) or '~'")
                else:
                    logger.warn(f"non slice use of i: {group}")
                    # # replace, e.g., i[1] with i[1:2]
                    # s = f"{group[1]}[1:-1]"
                    # tmp = f"{group[1][:-1]}:{group[1][-1]}"
                    # grpby['path'].append(
                    #         f"re.split('/', item['{group[0]}']){tmp}" )
                    # grpby['sort'].append(
                    #         f"re.split('/', item['{group[0]}']){tmp}")
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
            # logger.debug(f"also value: {value}, also: {also}")
        elif key in ['b', 'e']:
            dt = parse(part[1:], strict=False, tz='local')
            filters[key] = dt
        elif key == 'q':
            value = part[1:].strip()
            filters['query'] += f" and {value}"
        elif key == 't':
            value = [x.strip() for x in part[1:].split(',')]
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
        details.extend([f"item.get('{x}', '~')" for x in also])
        # logger.debug(f"details: {details}")
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

