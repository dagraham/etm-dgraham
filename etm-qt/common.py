#!/usr/bin/env python3.12
from dateutil.parser import parse as dateutil_parse
from dateutil.parser import ParserError
from datetime import datetime, date, timedelta
from pytz import timezone
from icecream import ic
import re

atamp_regex = re.compile(r'\s[@&][a-zA-Z+-]')

type_keys = {
    "*": "event",
    "-": "task",
    "✓": "finished",
    "%": "journal",
    "!": "inbox",
    "~": "wrap",
}



AWARE_FMT = '%Y%m%dT%H%MA'
NAIVE_FMT = '%Y%m%dT%H%MN'
DATE_FMT = '%Y%m%d'
DATETIME_FMT = '%y-%m-%d %H:%M %Z'

def pr(s: str) -> None:
    if __name__ == '__main__':
        ic(s)

def parse(s: str, **kwd: any) -> (datetime, str):
    try:
        dt = dateutil_parse(s)
    except ParserError as e:
        return (None, f"'{s}' is not yet a valid date or datetime")
    if 'tzinfo' in kwd:
        tzinfo = kwd['tzinfo']
        if tzinfo == 'float':
            pass
        elif tzinfo == 'local':
            dt = dt.astimezone()
        else:
            dt = timezone(tzinfo).localize(dt)
    else:
        dt = dt.astimezone()
    return (dt, dt.strftime(DATETIME_FMT))

args = [
        {'tzinfo': 'US/Pacific',},
        {'tzinfo': 'local',},
        {'tzinfo': 'float',},
        {},
        ]
pr("\nparse examples for '2pm fri':")
for _ in args:
    pr(f"with {_}: {parse('2pm fri', **_)}")

pr("\nbad arg for parse:")
args = ['fr', '32 2p', '25p', '-3' ]
for _ in args:
    pr(f"for {_}: {parse(_)}")

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

