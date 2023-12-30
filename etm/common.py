from dateutil.parser import parse as dateutil_parse
from dateutil.parser import parserinfo
import platform
import sys
import os
import sys
import logging
import logging.config

import etm.__version__ as version
from ruamel.yaml import __version__ as ruamel_version
from dateutil import __version__ as dateutil_version
from tinydb import __version__ as tinydb_version
from jinja2 import __version__ as jinja2_version
from prompt_toolkit import __version__ as prompt_toolkit_version

from time import perf_counter as timer


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

python_version = platform.python_version()
system_platform = platform.platform(terse=True)
etm_version = version.version
sys_platform = platform.system()
mac = sys.platform == 'darwin'
windoz = sys_platform in ('Windows', 'Microsoft')

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

logging.getLogger('asyncio').setLevel(logging.WARNING)
logger = logging.getLogger()


def parse(s, **kwd):
    # enable pi when read by main and settings is available
    pi = parserinfo(
        dayfirst=settings['dayfirst'], yearfirst=settings['yearfirst']
    )
    dt = dateutil_parse(s, parserinfo=pi)
    if 'tzinfo' in kwd:
        tzinfo = kwd['tzinfo']
        if tzinfo == 'float':
            return dt.replace(tzinfo=None)
        elif tzinfo == 'local':
            return dt.astimezone()
        else:
            return dt.replace(tzinfo=ZoneInfo(tzinfo))
    else:
        return dt.astimezone()


# in __main__ placed in model and view
ETM_CHAR = dict(
    VSEP='⏐',  # U+23D0  this will be a de-emphasized color
    FREE='─',  # U+2500  this will be a de-emphasized color
    HSEP='┈',  #
    BUSY='■',  # U+25A0 this will be busy (event) color
    CONF='▦',  # U+25A6 this will be conflict color
    TASK='▩',  # U+25A9 this will be busy (task) color
    ADAY='━',  # U+2501 for all day events ━
    USED='◦',  # U+25E6 for used time
    REPS='↻',  # Flag for repeating items
    FINISHED_CHAR='✓',
    SKIPPED_CHAR='✗',
    UPDATE_CHAR='𝕦',
    INBASKET_CHAR='𝕚',
    KONNECT_CHAR='k',
    LINK_CHAR='g',
    PIN_CHAR='p',
    ELLIPSiS_CHAR='…',
    LINEDOT=' · ',  # ܁ U+00B7 (middle dot),
)
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
