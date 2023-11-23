#!/usr/bin/env python3.12
from dateutil.parser import parse as dateutil_parse
from dateutil.parser import ParserError, parserinfo
from datetime import datetime, date, timedelta
from pytz import timezone
from icecream import ic
import re
import os

import logging
import logging.config
logger = logging.getLogger()

settings = {
    'dayfirst': False,
    'yearfirst': True,
    } #TODO: import these from options.py

def pr(s: str) -> None:
    if __name__ == '__main__':
        ic(s)

settings = {
    'yearfirst': True,
    'dayfirst': False
}

REGEX = {
    "ATAMP": re.compile(r'\s[@&][a-zA-Z+-]'),
    "RELDELTA": re.compile(r'^(.+)\s+([+-].+)?$'),
    "GEDAYS": re.compile(r'[dwM]'), # Is this used? 
}

TYPE_KEYS = {
    "*": "event",
    "-": "task",
    "%": "journal",
    "!": "inbox",
}    

DISPLAY_TYPE_KEYS = TYPE_KEYS.update({
    "✓": "finished",
    "~": "wrap",
})

FMTS = {
    "AWARE": '%Y%m%dT%H%MA',
    "NAIVE": '%Y%m%dT%H%MN',
    "DATE": '%y-%m-%d',
    "DATETIME": '%y-%m-%d %H:%M %Z',
}
def parse(s: str, z: str = 'local') -> (str | None, datetime):
    """
    Parse datetime string "s" applying "z" arguments and return a tuple containing a message describing the result and the python datetime object if successful and None otherwise.  
    >>> dt = parse('2p 23-10-26', z = 'US/Pacific')
    >>> dt[0]
    '23-10-26 14:00 PDT'
    >>> dt[1]
    datetime.datetime(2023, 10, 26, 14, 0, tzinfo=<DstTzInfo 'US/Pacific' PDT-1 day, 17:00:00 DST>)
    >>> dt = parse('2p 23-10-26', z = 'local')
    >>> dt[0]
    '23-10-26 14:00 EDT'
    >>> dt[1]
    datetime.datetime(2023, 10, 26, 14, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000), 'EDT'))
    >>> dt = parse('2p 23-10-26', z = 'float')
    >>> dt[0]
    '23-10-26 14:00'
    >>> dt[1]
    datetime.datetime(2023, 10, 26, 14, 0)
    >>> dt = parse('')
    >>> dt[0]
    "Enter a datetime expression such as '2p fri'"
    >>> dt[1]
    >>> dt = parse('fr')
    >>> dt[0]
    '"fr" is not yet a valid date or datetime'
    >>> dt[1]
    >>> dt = parse('2023-10-27')
    >>> dt[0]
    '23-10-27'
    >>> dt[1]
    datetime.date(2023, 10, 27)
    >>> dt = parse('2023-10-27 0:00:01')
    >>> dt[0]
    '23-10-27 00:00 EDT'
    >>> dt[1]
    datetime.datetime(2023, 10, 27, 0, 0, 1, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000), 'EDT'))
    """
    s = s.strip()
    if not s:
        return ("Enter a datetime expression such as '2p fri'", None)
    # we have an entry
    if settings:
        pi = parserinfo(
            dayfirst=settings.get('dayfirst', False),
            yearfirst=settings.get('yearfirst', True)
            )

    try:
        dt = dateutil_parse(s, parserinfo=pi)
    except ParserError as e:
        return (f"\"{s}\" is not yet a valid date or datetime", None)
    # we have a datetime object
    
    if z:
        if z == 'float':
            dt = dt.replace(tzinfo=None)
        elif z == 'local':
            dt = dt.astimezone()
        else:
            dt = timezone(z).localize(dt)
    else:
        dt = dt.astimezone()
    if dt.hour == dt.minute == dt.second == 0:
        return (dt.strftime(FMTS['DATE']).strip(), dt.date())
    else:
        return (dt.strftime(FMTS["DATETIME"]).strip(), dt)


def is_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

def add_zone_info(dt: datetime, zone: str = None) -> datetime:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        # naive date, return as is
        return dt
    elif isinstance(dt, datetime):
        if is_aware(dt):
            # already aware - convert to UTC
            dt = dt.astimezone(timezone('UTC'))
        elif zone:
            # naive - incorporate zone info if available
            if zone == 'float':
                # leave naive
                pass
            elif zone == 'local':
                # use local timezone
                dt = dt.astimezone().astimezone('UTC')
            else:
                # use the provided timezone
                dt = timezone(zone).localize(dt).astimezone(timezone('UTC'))
        else:
            # default to the local timezone
            dt = dt.astimezone().astimezone('UTC')
        return truncate_datetime(dt)
    else:
        raise ValueError(f"{dt} is not a date or datetime instance")


def truncate_datetime(dt: datetime) -> datetime:
    """ Remove seconds and microseconds from datetime.
    >>> dt = parse('2:01:15p 23-10-26', z = 'local')
    >>> dt[0]
    '23-10-26 14:01 EDT'
    >>> truncate_datetime(dt[1])
    datetime.datetime(2023, 10, 26, 14, 1, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000), 'EDT'))
    """
    return dt.replace(second=0, microsecond=0)

def truncate_timedelta(td: timedelta) -> timedelta:
    """ Return days and the largest number of seconds evenly divisable by 60, i.e., representable as an integer number of minutes.
    >>> td = timedelta(days=1, hours=1, minutes=1, seconds=30, microseconds=23456)
    >>> truncate_timedelta(td)
    datetime.timedelta(days=1, seconds=3660)
    """
    return timedelta(days=td.days, seconds=td.seconds-td.seconds%60)


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
        5: logging.CRITICAL
    }

    level = int(level)
    loglevel = log_levels.get(level, log_levels[3])

    # if we get here, we have an existing etmdir
    logfile = os.path.normpath(os.path.abspath(os.path.join(etmdir, "etm.log")))

    config = {'disable_existing_loggers': False,
              'formatters': {'simple': {
                  'format': '--- %(asctime)s - %(levelname)s - %(module)s.%(funcName)s\n    %(message)s'}},
              'handlers': {
                    'file': {
                        'backupCount': 7,
                        'class': 'logging.handlers.TimedRotatingFileHandler',
                        'encoding': 'utf8',
                        'filename': logfile,
                        'formatter': 'simple',
                        'level': loglevel,
                        'when': 'midnight',
                        'interval': 1}
              },
              'loggers': {
                  'etmmv': {
                    'handlers': ['file'],
                    'level': loglevel,
                    'propagate': False}
              },
              'root': {
                  'handlers': ['file'],
                  'level': loglevel},
              'version': 1}
    logging.config.dictConfig(config)
    # logger.critical("\n######## Initializing logging #########")
    if file:
        logger.critical(f'logging for file: {file}\n    logging at level: {loglevel}\n    logging to file: {logfile}')
    else:
        logger.critical(f'logging at level: {loglevel}\n    logging to file: {logfile}')

