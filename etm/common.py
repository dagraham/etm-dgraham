# pyright: reportUndefinedVariable=false
from dateutil.parser import parse as dateutil_parse 
from dateutil.parser import parserinfo 
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
import platform
import sys
import os
import sys
import textwrap
import shutil
import re
from shlex import split as qsplit
import contextlib, io
import subprocess   # for check_output

from pygments.lexer import RegexLexer 
from pygments.token import Keyword 
from pygments.token import Literal 
from pygments.token import Operator 
from pygments.token import Comment 


import logging
import logging.config
logger = None
# settings = None

import etm.__version__ as version 
from ruamel.yaml import __version__ as ruamel_version 
from dateutil import __version__ as dateutil_version 
from tinydb import __version__ as tinydb_version 
from jinja2 import __version__ as jinja2_version 
from prompt_toolkit import __version__ as prompt_toolkit_version 

from time import perf_counter as timer
from etm.make_examples import make_examples 

ETMDB = DBITEM = DBARCH = dataview = data_changed = None

def is_aware(dt):
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

class TimeIt(object):
    def __init__(self, label='', loglevel=1):
        self.loglevel = loglevel
        self.label = label
        if self.loglevel == 1:
            msg = 'timer {0} started; loglevel: {1}'.format(
                self.label, self.loglevel
            )
            logger.debug(msg)
            self.start = timer()

    def stop(self, *args):
        if self.loglevel == 1:
            self.end = timer()
            self.secs = self.end - self.start
            self.msecs = self.secs * 1000  # millisecs
            msg = 'timer {0} stopped; elapsed time: {1} milliseconds'.format(
                self.label, self.msecs
            )
            logger.debug(msg)


# from etm.__main__ import ETMHOME
from etm import options

python_version = platform.python_version()
system_platform = platform.platform(terse=True)
etm_version = version.version
sys_platform = platform.system()
mac = sys.platform == 'darwin'
windoz = sys_platform in ('Windows', 'Microsoft')

WA = {}
parse_datetime = None
text_pattern = None
etmhome = None
timers_file = None

VERSION_INFO = f"""\
 etm version:        {etm_version}
 python:             {python_version}
 dateutil:           {dateutil_version}
 prompt_toolkit:     {prompt_toolkit_version}
 tinydb:             {tinydb_version}
 jinja2:             {jinja2_version}
 ruamel.yaml:        {ruamel_version}
 platform:           {system_platform}\
"""

def check_output(cmd):
    if not cmd:
        return
    res = ''
    try:
        res = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True,
            universal_newlines=True,
            encoding='UTF-8',
        )
        return True, res
    except subprocess.CalledProcessError as e:
        logger.warning(f"Error running {cmd}\n'{e.output}'")
        lines = e.output.strip().split('\n')
        msg = lines[-1]
        return False, msg

def db_replace(new):
    """
    Used with update to replace the original doc with new.
    """

    def transform(doc):
        # update doc to include key/values from new
        doc.update(new)
        # remove any key/values from doc that are not in new
        for k in list(doc.keys()):
            if k not in new:
                del doc[k]

    return transform

def import_file(import_file=None):
    import_file = import_file.strip()
    if not import_file:
        return False, ''
    if import_file.lower() == 'lorem':
        return True, import_examples()

    if not os.path.isfile(import_file):
        return (
            False,
            f'"{import_file}"\n   either does not exist or is not a regular file',
        )
    filename, extension = os.path.splitext(import_file)
    if extension == '.text':
        return True, import_text(import_file)
    else:
        return (
            False,
            f"Importing a file with the extension '{extension}' is not implemented. Only files with the extension '.text' are recognized",
        )


def import_examples():
    docs = []
    examples = make_examples(last_id=last_id)

    results = []
    good = []
    bad = []
    items = []

    logger.debug(f"starting import from last_id: {last_id}")
    count = 0
    for s in examples:
        ok = True
        count += 1
        if not s:
            continue
        item = Item()  # use ETMDB by default
        item.new_item()
        item.text_changed(s, 1)
        if item.item_hsh.get('itemtype', None) is None:
            ok = False

        if item.item_hsh.get('summary', None) is None:
            ok = False


        if ok:
            # don't check links because the ids won't yet exist
            item.update_item_hsh(check_links=False)
            good.append(f'{item.doc_id}')
        else:
            logger.debug(f"bad entry: {s}")
            bad.append(s)

    logger.debug("ending import")
    res = f'imported {len(good)} items'
    if good:
        res += f'\n  ids: {good[0]} - {good[-1]}'
    if bad:
        res += f'\nrejected {bad} items:\n  '
        res += '\n  '.join(results)
    return res


def import_text(import_file=None):
    docs = []
    with open(import_file, 'r') as fo:
        logger.debug(f"opened for reading: '{import_file}'")
        results = []
        good = []
        bad = 0
        reminders = []
        reminder = []
        for line in fo:
            s = line.strip()
            if s and s[0] in ['!', '*', '-', '%']:
                if reminder:
                    # append it to reminders and reset it
                    reminders.append(reminder)
                    reminder = []
                reminder = [s]
            else:
                # append to the existing reminder
                reminder.append(s)
        if reminder:
            reminders.append(reminder)
    count = 0
    for reminder in reminders:
        count += 1
        logger.debug(f"reminder number {count}: {reminder}")
        ok = True
        s = '\n'.join(reminder)
        if not s:
            continue
        logger.debug(f"adding item for {s}")
        item = Item()  # use ETMDB by default
        item.new_item()
        item.text_changed(s, 1)
        if item.item_hsh.get('itemtype', None) is None:
            ok = False

        if item.item_hsh.get('summary', None) is None:
            ok = False

        if ok:
            # don't check links because the ids won't yet exist
            item.update_item_hsh(check_links=False)
            good.append(f'{item.doc_id}')
        else:
            logger.debug(f"bad entry: {s}")
            bad.append(s)

        # if not ok:
        #     bad += 1
        #     results.append(f'   {s}')
        #     continue

        # update_item_hsh stores the item in ETMDB
        # item.update_item_hsh()
        # good.append(f'{item.doc_id}')

    res = f'imported {len(good)} items'
    if good:
        res += f'\n  ids: {good[0]} - {good[-1]}'
    if bad:
        res += f'\nrejected {bad} items:\n  '
        res += '\n  '.join(results)
    logger.debug(f"returning: {res}")
    return res


def import_json(import_file=None):
    import json
    with open(import_file, 'r') as fo:
        import_hsh = json.load(fo)
    items = import_hsh['items']
    docs = []
    dups = 0
    add = 0
    for id in items:
        item_hsh = items[id]
        itemtype = item_hsh.get('itemtype')
        if not itemtype:
            continue
        summary = item_hsh.get('summary')
        if not summary:
            continue
        z = item_hsh.get('z', 'Factory')
        bad_keys = [x for x in item_hsh if not item_hsh[x]]
        for key in bad_keys:
            del item_hsh[key]
        if 's' in item_hsh:
            item_hsh['s'] = pen_from_fmt(item_hsh['s'], z)
        if 'f' in item_hsh:
            item_hsh['f'] = period_from_fmt(item_hsh['f'], z)
        item_hsh['created'] = datetime.now('UTC')
        if 'h' in item_hsh:
            item_hsh['h'] = [period_from_fmt(x, z) for x in item_hsh['h']]
        if '+' in item_hsh:
            item_hsh['+'] = [pen_from_fmt(x, z) for x in item_hsh['+']]
        if '-' in item_hsh:
            item_hsh['-'] = [pen_from_fmt(x, z) for x in item_hsh['-']]
        if 'e' in item_hsh:
            item_hsh['e'] = parse_duration(item_hsh['e'])[1]
        if 'w' in item_hsh:
            wrps = [parse_duration(x)[1] for x in item_hsh['w']]
            item_hsh['w'] = wrps
        if 'a' in item_hsh:
            alerts = []
            for alert in item_hsh['a']:
                # drop the True from parse_duration
                tds = [parse_duration(x)[1] for x in alert[0]]
                # put the largest duration first
                tds.sort(reverse=True)
                cmds = alert[1:2]
                args = ''
                if len(alert) > 2 and alert[2]:
                    args = ', '.join(alert[2])
                for cmd in cmds:
                    if args:
                        row = (tds, cmd, args)
                    else:
                        row = (tds, cmd)
                    alerts.append(row)
            item_hsh['a'] = alerts
        if 'j' in item_hsh:
            jbs = []
            for jb in item_hsh['j']:
                if 'h' in jb:
                    if 'f' not in jb:
                        jb['f'] = jb['h'][-1]
                    del jb['h']
                jbs.append(jb)
            ok, lofh, last_completed = jobs(jbs, item_hsh)

            if ok:
                item_hsh['j'] = lofh
            else:
                print('using jbs', jbs)
                print(
                    'ok:',
                    ok,
                    ' lofh:',
                    lofh,
                    ' last_completed:',
                    last_completed,
                )

        if 'r' in item_hsh:
            ruls = []
            for rul in item_hsh['r']:
                if 'r' in rul and rul['r'] == 'l':
                    continue
                elif 'f' in rul:
                    if rul['f'] == 'l':
                        continue
                    else:
                        rul['r'] = rul['f']
                        del rul['f']
                if 'u' in rul:
                    if 't' in rul:
                        del rul['t']
                    if 'c' in rul:
                        del rul['c']
                elif 't' in rul:
                    rul['c'] = rul['t']
                    del rul['t']
                if 'u' in rul:
                    if type(rul['u']) == str:
                        try:
                            rul['u'] = parse(rul['u'], tz=z)
                        except Exception as e:
                            logger.error(
                                f"error parsing rul['u']: {rul['u']}. {e}"
                            )
                if 'w' in rul:
                    if isinstance(rul['w'], list):
                        rul['w'] = [
                            '{0}:{1}'.format('{W}', x.upper())
                            for x in rul['w']
                        ]
                    else:
                        rul['w'] = '{0}:{1}'.format('{W}', rul['w'].upper())
                bad_keys = []
                for key in rul:
                    if not rul[key]:
                        bad_keys.append(key)
                if bad_keys:
                    for key in bad_keys:
                        del rul[key]
                if rul:
                    ruls.append(rul)
            if ruls:
                item_hsh['r'] = ruls
            else:
                del item_hsh['r']

        docs.append(item_hsh)
    # now check for duplicates. If an item to be imported has the same type, summary and starting time as an existing item, regard it as a duplicate and do not import it.
    exst = []
    new = []
    dups = 0
    for x in ETMDB:
        exst.append(
            {
                'itemtype': x.get('itemtype'),
                'summary': x.get('summary'),
                's': x.get('s'),
            }
        )
    i = 0
    for x in docs:
        i += 1
        y = {
            'itemtype': x.get('itemtype'),
            'summary': x.get('summary'),
            's': x.get('s'),
        }
        if exst and y in exst:
            dups += 1
        else:
            new.append(x)

    ids = []
    if new:
        ids = ETMDB.insert_multiple(new)
        ETMDB.close()
    msg = f'imported {len(new)} items'
    if ids:
        msg += f'\n  ids: {ids[0]}-{ids[-1]}.'
    if dups:
        msg += f'\n  rejected {dups} items as duplicates'
    return msg

def update_db(db, doc_id, hsh={}):
    old = db.get(doc_id=doc_id)
    if not old:
        logger.error(
            f'Could not get document corresponding to doc_id {doc_id}'
        )
        return
    if old == hsh:
        return
    hsh['modified'] = datetime.now()
    logger.debug(f"starting db.update")
    try:
        db.update(db_replace(hsh), doc_ids=[doc_id])
    except Exception as e:
        logger.error(
            f'Error updating document corresponding to doc_id {doc_id}\nhsh {hsh}\nexception: {repr(e)}'
        )

def write_back(db, docs):
    logger.debug(f"starting write_back")
    for doc in docs:
        try:
            doc_id = doc.doc_id
            update_db(db, doc_id, doc)
        except Exception as e:
            logger.error(f'write_back exception: {e}')


def setup_logging(level, etmdir, file=None):
    """
    Setup logging configuration. Override root:level in
    logging.yaml with default_level.
    """

    if not os.path.isdir(etmdir):
        return

    log_levels = {
        1: logging.DEBUG,
        2: logging.INFO,
        3: logging.WARN,
        4: logging.ERROR,
        5: logging.CRITICAL,
    }

    level = int(level)
    loglevel = log_levels.get(level, log_levels[3])

    # if we get here, we have an existing etmdir
    logfile = os.path.normpath(
        os.path.abspath(os.path.join(etmdir, 'etm.log'))
    )

    config = {
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '--- %(asctime)s - %(levelname)s - %(module)s.%(funcName)s\n    %(message)s'
            }
        },
        'handlers': {
            'file': {
                'backupCount': 7,
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'encoding': 'utf8',
                'filename': logfile,
                'formatter': 'simple',
                'level': loglevel,
                'when': 'midnight',
                'interval': 1,
            }
        },
        'loggers': {
            'etmmv': {
                'handlers': ['file'],
                'level': loglevel,
                'propagate': False,
            }
        },
        'Redirectoot': {'handlers': ['file'], 'level': loglevel},
        'version': 1,
    }
    logging.config.dictConfig(config)
    # logger = logging.getLogger('asyncio').setLevel(logging.WARNING)
    logger = logging.getLogger('etmmv')

    logger.critical('\n######## Initializing logging #########')
    if logfile:
        logger.critical(
            f'logging for file: {file}\n    logging at level: {loglevel}\n    logging to file: {logfile}'
        )
    else:
        logger.critical(
            f'logging at level: {loglevel}\n    logging to file: {logfile}'
        )
    return logger

def openWithDefault(path):
    if ' ' in path:
        parts = qsplit(path)
        if parts:
            # wrapper to catch 'Exception Ignored' messages
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                # the pid business is evidently needed to avoid waiting
                pid = subprocess.Popen(
                    parts,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ).pid
                res = output.getvalue()
                if res:
                    logger.error(f"caught by contextlib:\n'{res}'")

    else:
        path = os.path.normpath(os.path.expanduser(path))
        sys_platform = platform.system()
        if platform.system() == 'Darwin':       # macOS
            subprocess.run(
                ('open', path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif platform.system() == 'Windows':    # Windows
            os.startfile(path)
        else:                                   # linux
            subprocess.run(
                ('xdg-open', path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    return


class TDBLexer(RegexLexer):

    name = 'TDB'
    aliases = ['tdb']
    filenames = '*.*'
    flags = re.MULTILINE | re.DOTALL

    tokens = {
        'root': [
            (
                r'\b(begins|includes|in|equals|more|less|exists|any|all|one)\b',
                Keyword,
            ),
            (
                r'\b(replace|remove|archive|delete|set|provide|attach|detach)\b',
                Keyword,
            ),
            (r'\b(itemtype|summary)\b', Literal),
            (r'\b(and|or|info)\b', Keyword),
        ],
    }

def nowrap(txt, indent=3, width=shutil.get_terminal_size()[0] - 3):
    return txt

def wrap(txt, indent=1, width=shutil.get_terminal_size()[0] - 3):
    """
    Wrap text to terminal width using indent spaces before each line.
    >>> txt = "Now is the time for all good men to come to the aid of their country. " * 5
    >>> res = wrap(txt, 4, 60)
    >>> print(res)
    Now is the time for all good men to come to the aid of
        their country. Now is the time for all good men to
        come to the aid of their country. Now is the time
        for all good men to come to the aid of their
        country. Now is the time for all good men to come
        to the aid of their country. Now is the time for
        all good men to come to the aid of their country.
    """
    para = [x.rstrip() for x in txt.split('\n')]
    tmp = []
    first = True
    for p in para:
        if first:
            initial_indent = ''
            first = False
        else:
            initial_indent = ' ' * indent
        tmp.append(
            textwrap.fill(
                p,
                initial_indent=initial_indent,
                subsequent_indent=' ' * indent,
                width=width - indent - 1,
            )
        )
    return '\n'.join(tmp)


def parse(s, **kwd):
    # enable pi when read by main and settings is available
    pi = parserinfo(
        dayfirst=settings['dayfirst'], yearfirst=settings['yearfirst']
    )
    # logger.debug(f"parsing {s = } with {kwd = }")
    dt = dateutil_parse(s, parserinfo=pi)
    if 'tzinfo' in kwd:
        tzinfo = kwd['tzinfo']
        # logger.debug(f"using {tzinfo = } with {dt = }")
        if tzinfo == None:
            return dt.replace(tzinfo=None)
        elif tzinfo == 'local':
            return dt.astimezone()
        else:
            return dt.replace(tzinfo=ZoneInfo(tzinfo))
    else:
        return dt.astimezone()


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"'AttrDict' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        self[key] = value

    # Initializing AttrDict with a dictionary
    # d = AttrDict({'attr': 'value', 'another': 123})
    # print(d.attr)  # Outputs: value

class EtmChar:
    VSEP='⏐'  # U+23D0  this will be a de-emphasized color
    FREE='─'  # U+2500  this will be a de-emphasized color
    HSEP='┈'  #
    BUSY='■'  # U+25A0 this will be busy (event) color
    CONF='▦'  # U+25A6 this will be conflict color
    TASK='▩'  # U+25A9 this will be busy (task) color
    ADAY='━'  # U+2501 for all day events ━
    RSKIP = '▶'   # U+25E6 for used time
    LSKIP = '◀'   # U+25E6 for used time
    USED='◦'  # U+25E6 for used time
    REPS='↻'  # Flag for repeating items
    FINISHED_CHAR='✓'
    SKIPPED_CHAR='✗'
    SLOW_CHAR='∾'
    LATE_CHAR='∿'
    INACTIVE_CHAR= '≁'
    # INACTIVE_CHAR='∽'
    ENDED_CHAR='≀'
    UPDATE_CHAR='𝕦'
    INBASKET_CHAR='𝕚'
    KONNECT_CHAR='k'
    LINK_CHAR='g'
    PIN_CHAR='p'
    ELLIPSIS_CHAR='…'
    LINEDOT=' · '  # ܁ U+00B7 (middle dot),
    ELECTRIC='⌁'



#  model, data and ical
#  with integer prefixes
WKDAYS_DECODE = {
    '{0}{1}'.format(n, d): '{0}({1})'.format(d, n) if n else d
    for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']
}

WKDAYS_ENCODE = {
    '{0}({1})'.format(d, n): '{0}{1}'.format(n, d) if n else d
    for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    for n in ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4']
}

# without integer prefixes
for wkd in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
    WKDAYS_ENCODE[wkd] = wkd

# print(f'WKDAYS_DECODE:\n{WKDAYS_DECODE}')
# print(f'WKDAYS_ENCODE:\n{WKDAYS_ENCODE}')
# WKDAYS_DECODE:
# {'-4MO': 'MO(-4)', '-3MO': 'MO(-3)', '-2MO': 'MO(-2)', '-1MO': 'MO(-1)', 'MO': 'MO', '1MO': 'MO(1)', '2MO': 'MO(2)', '3MO': 'MO(3)', '4MO': 'MO(4)', '-4TU': 'TU(-4)', '-3TU': 'TU(-3)', '-2TU': 'TU(-2)', '-1TU': 'TU(-1)', 'TU': 'TU', '1TU': 'TU(1)', '2TU': 'TU(2)', '3TU': 'TU(3)', '4TU': 'TU(4)', '-4WE': 'WE(-4)', '-3WE': 'WE(-3)', '-2WE': 'WE(-2)', '-1WE': 'WE(-1)', 'WE': 'WE', '1WE': 'WE(1)', '2WE': 'WE(2)', '3WE': 'WE(3)', '4WE': 'WE(4)', '-4TH': 'TH(-4)', '-3TH': 'TH(-3)', '-2TH': 'TH(-2)', '-1TH': 'TH(-1)', 'TH': 'TH', '1TH': 'TH(1)', '2TH': 'TH(2)', '3TH': 'TH(3)', '4TH': 'TH(4)', '-4FR': 'FR(-4)', '-3FR': 'FR(-3)', '-2FR': 'FR(-2)', '-1FR': 'FR(-1)', 'FR': 'FR', '1FR': 'FR(1)', '2FR': 'FR(2)', '3FR': 'FR(3)', '4FR': 'FR(4)', '-4SA': 'SA(-4)', '-3SA': 'SA(-3)', '-2SA': 'SA(-2)', '-1SA': 'SA(-1)', 'SA': 'SA', '1SA': 'SA(1)', '2SA': 'SA(2)', '3SA': 'SA(3)', '4SA': 'SA(4)', '-4SU': 'SU(-4)', '-3SU': 'SU(-3)', '-2SU': 'SU(-2)', '-1SU': 'SU(-1)', 'SU': 'SU', '1SU': 'SU(1)', '2SU': 'SU(2)', '3SU': 'SU(3)', '4SU': 'SU(4)'}
# WKDAYS_ENCODE:
# {'MO(-4)': '-4MO', 'MO(-3)': '-3MO', 'MO(-2)': '-2MO', 'MO(-1)': '-1MO', 'MO(+1)': '+1MO', 'MO(+2)': '+2MO', 'MO(+3)': '+3MO', 'MO(+4)': '+4MO', 'TU(-4)': '-4TU', 'TU(-3)': '-3TU', 'TU(-2)': '-2TU', 'TU(-1)': '-1TU', 'TU(+1)': '+1TU', 'TU(+2)': '+2TU', 'TU(+3)': '+3TU', 'TU(+4)': '+4TU', 'WE(-4)': '-4WE', 'WE(-3)': '-3WE', 'WE(-2)': '-2WE', 'WE(-1)': '-1WE', 'WE(+1)': '+1WE', 'WE(+2)': '+2WE', 'WE(+3)': '+3WE', 'WE(+4)': '+4WE', 'TH(-4)': '-4TH', 'TH(-3)': '-3TH', 'TH(-2)': '-2TH', 'TH(-1)': '-1TH', 'TH(+1)': '+1TH', 'TH(+2)': '+2TH', 'TH(+3)': '+3TH', 'TH(+4)': '+4TH', 'FR(-4)': '-4FR', 'FR(-3)': '-3FR', 'FR(-2)': '-2FR', 'FR(-1)': '-1FR', 'FR(+1)': '+1FR', 'FR(+2)': '+2FR', 'FR(+3)': '+3FR', 'FR(+4)': '+4FR', 'SA(-4)': '-4SA', 'SA(-3)': '-3SA', 'SA(-2)': '-2SA', 'SA(-1)': '-1SA', 'SA(+1)': '+1SA', 'SA(+2)': '+2SA', 'SA(+3)': '+3SA', 'SA(+4)': '+4SA', 'SU(-4)': '-4SU', 'SU(-3)': '-3SU', 'SU(-2)': '-2SU', 'SU(-1)': '-1SU', 'SU(+1)': '+1SU', 'SU(+2)': '+2SU', 'SU(+3)': '+3SU', 'SU(+4)': '+4SU', 'MO': 'MO', 'TU': 'TU', 'WE': 'WE', 'TH': 'TH', 'FR': 'FR', 'SA': 'SA', 'SU': 'SU'}


AWARE_FMT = '%Y%m%dT%H%MA'
NAIVE_FMT = '%Y%m%dT%H%MN'
DATE_FMT = '%Y%m%d'


def normalize_timedelta(delta):
    total_seconds = delta.total_seconds()
    sign = '-' if total_seconds < 0 else ''
    minutes, remainder = divmod(abs(int(total_seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    until = []
    if weeks:
        until.append(f'{weeks}w')
    if days:
        until.append(f'{days}d')
    if hours:
        until.append(f'{hours}h')
    if minutes:
        until.append(f'{minutes}m')
    if not until:
        until.append('0m')

    return sign + ''.join(until)


# Test
td = timedelta(days=-1, hours=2, minutes=30)
normalized_td = normalize_timedelta(td)

td = timedelta(days=1, hours=-2, minutes=-30)
normalized_td = normalize_timedelta(td)


def encode_datetime(obj):
    if not isinstance(obj, datetime):
        raise ValueError(f'{obj} is not a datetime instance')
    if is_aware(obj):
        return obj.astimezone(ZoneInfo('UTC')).strftime(AWARE_FMT)
    else:
        return obj.strftime(NAIVE_FMT)


def decode_datetime(s):
    if s[-1] not in 'AN' or len(s) != 14:
        raise ValueError(f'{s} is not a datetime string')
    if s[-1] == 'A':
        return (
            datetime.strptime(s, AWARE_FMT)
            .replace(tzinfo=ZoneInfo('UTC'))
            .astimezone()
        )
    else:
        return datetime.strptime(s, NAIVE_FMT).astimezone(None)


class Period:
    def __init__(self, datetime1, datetime2):
        # datetime1: done/start; datetime2: due/end. On time => period positive
        # Ensure both inputs are datetime.datetime instances
        if not isinstance(datetime1, datetime) or not isinstance(
            datetime2, datetime
        ):
            raise ValueError('Both inputs must be datetime instances')

        aware1 = is_aware(datetime1)
        aware2 = is_aware(datetime2)

        if aware1 != aware2:
            raise ValueError(
                f'start: {datetime1.tzinfo}, end: {datetime2.tzinfo}. Both datetimes must either be naive or both must be aware.'
            )

        if aware1:
            self.start = datetime1.astimezone(ZoneInfo('UTC'))
            self.end = datetime2.astimezone(ZoneInfo('UTC'))
        else:
            self.start = datetime1.replace(tzinfo=None)
            self.end = datetime2.replace(tzinfo=None)

        self.diff = self.end - self.start

    def __repr__(self):
        return f'Period({encode_datetime(self.start)} -> {encode_datetime(self.end)}, {normalize_timedelta(self.diff)})'

    def __eq__(self, other):
        if isinstance(other, Period):
            return self.start == other.start
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Period):
            return self.start < other.start
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Period):
            return self.start > other.start
        return NotImplemented

    # Optionally, define __le__ and __ge__
    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def start(self):
        return self.start

    def end(self):
        return self.end

    def diff(self):
        return self.diff
