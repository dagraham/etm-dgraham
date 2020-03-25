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
dates
    w) week
    y) year
    m) month
    d) day

Options
    -a append fields, eg 'd', 'l'
    -b begin date
    -e end date 
    -l location
    -d depth
    -i index
    -m missing
    -o omit
    -s summary
    -S search
    -t tags

examples
    u i[0]; i[1:]; 

"""

minus_regex = re.compile(r'\s+\-(?=[a-zA-Z])')
# group_regex = re.compile(r'^\s*(.*)\s+(\d+)/(\d+):\s*(.*)')
groupdate_regex = re.compile(r'\by{2}\b|\by{4}\b|\b[dM]{1,4}\b|\bw\b')
# options_regex = re.compile(r'^\s*(!?[fk](\[[:\d]+\])?)|(!?[clostu])\s*$')

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

    def ut_ok(self, a, b=None, e=None):
        return where('u').exists()

def str2opts(s, options=None):
    if not options:
        options = {}
    filters = {}
    op_str = s.split('#')[0]
    parts = minus_regex.split(op_str)
    head = parts.pop(0)
    report = head[0]
    groupbystr = head[1:].strip()
    if not report or report not in ['c', 'u'] or not groupbystr:
        return {}, {}, {}
    grpby = {'report': report}
    filters['dates'] = False
    dated = {'grpby': False}
    filters['report'] = report
    filters['omit'] = [True, []]
    filters['neg_fields'] = []
    filters['pos_fields'] = []
    groupbylst = [x.strip() for x in groupbystr.split(';')]
    grpby['lst'] = groupbylst
    for part in groupbylst:
        if groupdate_regex.search(part):
            dated['grpby'] = True
            filters['dates'] = True
        elif part not in ['c', 'l'] and part[0] not in ['i', 't']:
            term_print(
                str(_('Ignoring invalid grpby part: "{0}"'.format(part))))
            groupbylst.remove(part)
    if not groupbylst:
        return {}, {}, {}
        # we'll split cols on :: after applying fmts to the string
    grpby['cols'] = "::".join([f"{i}" for i in range(len(groupbylst))])
    grpby['fmts'] = []
    grpby['tuples'] = []
    filters['grpby'] = ['_summary']
    filters['missing'] = False
    include = {'y', 'm', 'd'}
    for group in groupbylst:
        d_lst = []
        if groupdate_regex.search(group):
            if 'w' in group:
                # groupby week or some other date spec,  not both
                group = "w"
                d_lst.append('w')
                # include.discard('w')
                if 'y' in group:
                    include.discard('y')
                if 'M' in group:
                    include.discard('m')
                if 'd' in group:
                    include.discard('d')
            else:
                if 'y' in group:
                    d_lst.append('yyyy')
                    include.discard('y')
                if 'M' in group:
                    d_lst.append('MM')
                    include.discard('m')
                if 'd' in group:
                    d_lst.append('dd')
                    include.discard('d')
            grpby['tuples'].append(" ".join(d_lst))
            grpby['fmts'].append(
                "d_to_str(tup[-3], '%s')" % group)

        elif '[' in group:
            if group[0] == 'i':
                if ':' in group:
                    grpby['fmts'].append(
                        "':'.join(rsplit(':', hsh['%s'])%s)" %
                        (group[0], group[1:]))
                    grpby['tuples'].append(
                        "':'.join(rsplit(':', hsh['%s'])%s)" %
                        (group[0], group[1:]))
                else:
                    grpby['fmts'].append(
                        "rsplit(':', hsh['%s'])%s" % (group[0], group[1:]))
                    grpby['tuples'].append(
                        "rsplit(':', hsh['%s'])%s" % (group[0], group[1:]))
            filters['grpby'].append(group[0])
        else:
            grpby['fmts'].append("hsh['%s']" % group.strip())
            grpby['tuples'].append("hsh['%s']" % group.strip())
            filters['grpby'].append(group[0])
        if include:
            if include == {'y', 'm', 'd'}:
                grpby['include'] = "yyyy-MM-dd"
            elif include == {'m', 'd'}:
                grpby['include'] = "MMM d"
            elif include == {'y', 'd'}:
                grpby['include'] = "yyyy-MM-dd"
            elif include == set(['y', 'w']):
                groupby['include'] = "w"
            elif include == {'d'}:
                grpby['include'] = "MMM dd"
            elif include == set(['w']):
                grpby['include'] = "w"
            else:
                grpby['include'] = ""
        else:
            grpby['include'] = ""
        # logger.debug('grpby final: {0}'.format(grpby))

    also = []
    for part in parts:
        key = part[0]
        if key == 'a':
            value = [x.strip() for x in part[1:].split(',')]
            also.extend(value)
        if key in ['b', 'e']:
            dt = parse_datetime(part[1:])
            dated[key] = dt

        elif key == 'm':
            value = part[1:].strip()
            if value == '1':
                filters['missing'] = True

        elif key == 's':
            value = part[1:].strip()
            if value[0] == '!':
                filters['search'] = (False, re.compile(r'%s' % value[1:],
                                                       re.IGNORECASE))
            else:
                filters['search'] = (True, re.compile(r'%s' % value,
                                                      re.IGNORECASE))
        elif key == 'S':
            value = part[1:].strip()
            if value[0] == '!':
                filters['search-all'] = (False, re.compile(r'%s' % value[1:], re.IGNORECASE | re.DOTALL))
            else:
                filters['search-all'] = (True, re.compile(r'%s' % value, re.IGNORECASE | re.DOTALL))
        elif key == 'd':
            if grpby['report'] == 'a':
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
            value = part[1:].strip()
            if value[0] == '!':
                filters['omit'][0] = False
                filters['omit'][1] = [x for x in value[1:]]
            else:
                filters['omit'][0] = True
                filters['omit'][1] = [x for x in value]
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
    grpby['lst'].append('summary')
    if also:
        grpby['lst'].extend(also)
    # logger.debug('grpby: {0}; dated: {1}; filters: {2}'.format(grpby, dated, filters))
    return grpby, dated, filters


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
            grpby, dated, filters = str2opts(text)
            print(f"grpby: {grpby}\ndated: {dated}\nfilters: {filters}")
            # ok, items = query.do_query('exists u')
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
