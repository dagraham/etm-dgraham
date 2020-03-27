import os
import sys
import re
from tinydb import where, Query
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
import etm.options as options
from etm import view
from etm.model import item_details
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

import etm.view as view
from etm.view import ETMQuery
# from etm.model import parse_datetime, date_to_datetime

def parse_datetime(s):
    return parse(s, strict=False, tz='local')


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
# options_regex = re.compile(r'^\s*(!?[fk](\[[:\d]+\])?)|(!?[clostu])\s*$')

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

class Query(ETMQuery):

    def __init__(self):
        super().__init__()
        self.arg['ut'] = self.ut_ok

        self.allowed_commands = ", ".join([x for x in self.arg])

        self.command_details += """
    ut_ok a b: return items in which @u exists and blah
        """ 
    def all(self):
        return where('itemtype').exists()

    def ut_ok(self, a, b=None, e=None):
        return where('u').exists()

def apply_dates_filter(items, grpby, filters):
    if 'b' not in filters and 'e' not in filters:
        return items
    ok_items = []
    if grpby['report'] == 'u':
        def rel_dt(item, filters):
            l = [x[1] for x in item['u']]
            e_ok = 'e' not in filters or min(l) <= filters['e']
            b_ok = 'b' not in filters or max(l) >= filters['b']
            return e_ok and b_ok 
    elif grpby['report'] == 'c':
        def rel_dt(item, filters):
            if 'f' in item:
                e_ok = 'e' not in filters or item['f'] <= filters['e'] 
                b_ok = 'b' not in filters or item['f'] >= filters['b']
            elif 's' in item:
                e_ok = 'e' not in filters or item['s'] <= filters['s'] 
                b_ok = 'b' not in filters or item['s'] >= filters['s']
            else:
                e_ok = b_ok = True
            return e_ok and b_ok

    for item in items:
        if rel_dt(item, filters):
            ok_items.append(item)
    return ok_items


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
        print(f"groupbylst: {groupbylst}")
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
    grpby['tups'] = []
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
                grpby['sort'].append(f"rel_dt.format('{tmp}')")
                grpby['tups'].append(
                    f"rel_dt.format('{group}')")

            elif '[' in group:
                if group[0] == 'i':
                    if ':' in group:
                        grpby['tups'].append(
                                f"'/'.join(re.split('/', hsh['{group[0]}']){group[1:]})")
                        grpby['sort'].append(
                                f"'/'.join(re.split('/', hsh[{group[0]}]){group[1:]})")
                    else:
                        grpby['tups'].append(
                                f"re.split('/', hsh['{group[0]}']){group[1:]}" )
                        grpby['sort'].append(
                                f"re.split('/', hsh['{group[0]}']){group[1:]}")
            else:
                grpby['tups'].append("hsh['%s']" % group.strip())
                grpby['sort'].append(f"hsh['{group.strip()}']")
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
    grpby.setdefault('lst', []).append('summary')
    if omit:
        tmp = [f" and ~equals itemtype {key}" for key in omit]
        filters['query'] += "".join(tmp)

    if also:
        grpby['also'] = also
    # logger.debug('grpby: {0}; dated: {1}; filters: {2}'.format(grpby, dated, filters))
    return grpby, filters


def main():

    # view.item_details = item_details
    # settings = options.Settings(etmdir).settings
    # secret = settings.get('secret')
    # data.secret = secret

    # from etm.view import Query
    query = Query()

    session = PromptSession()

    again = True
    while again:

        text = session.prompt("query: ", lexer=query.lexer)
        if not text:
            again = False
            continue
        if text.startswith('u') or text.startswith('c'):
            # if len(text.strip()) == 1:
            #     continue
            grpby, filters = str2opts(text)
            if not grpby:
                continue
            # print(f"grpby: {grpby}")
            # print(f"grpby: {grpby}\nfilters: {filters}")
            print(f"grpby: {grpby}\n\nfilters: {filters}")
            ok, items = query.do_query(filters.get('query'))
            if ok:
                if 'b' in filters or 'e' in filters:
                    items = apply_dates_filter(items, grpby, filters)
                for item in items:
                    print(f"   {item['itemtype']} {item.get('summary', 'none')} {item.doc_id}")
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
    main()
