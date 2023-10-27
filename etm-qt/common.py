#!/usr/bin/env python3.12
from dateutil.parser import parse as dateutil_parse
from dateutil.parser import ParserError
from datetime import datetime, date, timedelta
from pytz import timezone
from icecream import ic
import re

def pr(s: str) -> None:
    if __name__ == '__main__':
        ic(s)

REGEX = {
    "ATAMP": re.compile(r'\s[@&][a-zA-Z+-]'),
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
    "DATE": '%Y%m%d',
    "DATETIME": '%y-%m-%d %H:%M %Z',
}
def parse(s: str, **kwd: any) -> (str | None, datetime):
    """
    Parse datetime string "s" applying any "**kwd" arguments and return a tuple containing a message describing the result and the python datetime object if successful and None otherwise. 
    >>> dt = parse('2p 23-10-26', **{'timezone': 'US/Pacific'})
    >>> dt[0]
    '26-10-23 14:00 PDT'
    >>> dt[1]
    datetime.datetime(2026, 10, 23, 14, 0, tzinfo=<DstTzInfo 'US/Pacific' PDT-1 day, 17:00:00 DST>)
    >>> dt = parse('')
    >>> dt[0]
    "Enter a datetime expression such as '2p fri'"
    >>> dt[1]
    >>> dt = parse('2023-10-27')
    >>> dt[0]
    "Enter a datetime expression such as '2p fri'"
    >>> dt[1]
    
    """
    s = s.strip()
    if not s:
        return ("Enter a datetime expression such as '2p fri'", None)
    # we have an entry
    try:
        dt = dateutil_parse(s)
    except ParserError as e:
        return (f"\"{s}\" is not yet a valid date or datetime", None)
    # we have a datetime object
    if 'timezone' in kwd:
        tzinfo = kwd['timezone']
        if tzinfo == 'float':
            pass
        elif tzinfo == 'local':
            dt = dt.astimezone()
        else:
            dt = timezone(tzinfo).localize(dt)
    else:
        dt = dt.astimezone()
    return (dt.strftime(FMTS["DATETIME"]), dt)

args = [
        {'tzinfo': 'US/Pacific',},
        {'tzinfo': 'local',},
        {'tzinfo': 'float',},
        {},
        ]
pr("\nparse examples for '2pm fri':")
for _ in args:
    m, o = parse('2p fri', **_)
    pr(f"with {_}: {m}; {o}")

pr("\nbad arg for parse:")
args = ['fr', '32 2p', '25p', '-3' ]
for _ in args:
    m, o = parse(_)
    pr(f"for {_}: {m}; {o}")

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
    return dt.replace(second=0, microsecond=0)

def truncate_timedelta(td: timedelta) -> timedelta:
    return timedelta(days=td.days, seconds=td.seconds-td.seconds%60)

pr("\ntruncate examples:")
_ = datetime.now()
pr(f"{_}: {truncate_datetime(_)}")
_ = timedelta(days=1, hours=1, minutes=1, seconds=30, microseconds=23456)
pr(f"{_}: {truncate_timedelta(_)}")

