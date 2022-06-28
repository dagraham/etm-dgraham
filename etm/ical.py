import os

from datetime import timedelta

from icalendar import Calendar, Event, Todo, Journal
from icalendar.caselessdict import CaselessDict
from icalendar.prop import vDate, vDatetime
import pytz
import pendulum
import dateutil

# from dateutil.parser import parse
from pendulum import parse as pendulum_parse

def parse(s, **kwd):
    return pendulum_parse(s, strict=False, **kwd)

local_timezone = None
ONEMINUTE = timedelta(minutes=1)

WKDAYS_DECODE = {"{0}{1}".format(n, d): "{0}({1})".format(d, n) if n else d for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']}

def wkdays_decode(s):
    """
    Return the serialization as a weekday object.
    """
    # print('deseralizing', s, type(s))
    return eval('dateutil.rrule.{}'.format(WKDAYS_DECODE[s]))

def pen_from_fmt(s, z='local'):
    """
    >>> pen_from_fmt("20120622T0000")
    Date(2012, 6, 22)
    """
    if not isinstance(s, str):
        return pendulum.instance(s)
    if len(s) == 8:
        dt = pendulum.from_format(s, "YYYYMMDD", z)
        return dt.date()
    else:
        if s[-1] == 'Z':
            # UTC - ignore z and drop the trailing Z
            dt = pendulum.from_format(s[:-1], "YYYYMMDDTHHmmss")
        else:
            dt = pendulum.from_format(s, "YYYYMMDDTHHmmss", z)
        if z in ['local', 'Factory'] and dt.hour == dt.minute == 0:
            dt = dt.date()
        return dt

def fmt_dt(s):
    dt = parse(s)
    return dt.strftime("%Y-%m-%d %H:%M")


def fmt_period(td, parent=None, short=False):
    if type(td) is not timedelta:
        return td
    if td < ONEMINUTE * 0:
        return '0m'
    if td == ONEMINUTE * 0:
        return '0m'
    until = []
    td_days = td.days
    td_hours = td.seconds // (60 * 60)
    td_minutes = (td.seconds % (60 * 60)) // 60

    if short:
        if td_days > 1:
            if td_minutes > 30:
                td_hours += 1
            td_minutes = 0
        if td_days > 7:
            if td_hours > 12:
                td_days += 1
            td_hours = 0

    if td_days:
        until.append("%dd" % td_days)
    if td_hours:
        until.append("%dh" % td_hours)
    if td_minutes:
        until.append("%dm" % td_minutes)
    if not until:
        until = "0m"
    return "".join(until)


ical_hsh = {
    '-': 'EXDATE',
    '+': 'RDATE',
    'f': 'FREQ',  # unicode
    'i': 'INTERVAL',  # positive integer
    'c': 'COUNT',  # total count positive integer
    's': 'BYSETPOS',  # integer
    'u': 'UNTIL',  # unicode
    'M': 'BYMONTH',  # integer 1...12
    'm': 'BYMONTHDAY',  # positive integer
    'W': 'BYWEEKNO',  # positive integer
    'w': 'BYDAY',  # integer 0 (SU) ... 6 (SA)
    'h': 'BYHOUR',  # positive integer
    'n': 'BYMINUTE',  # positive integer
    'E': 'BYEASTER',  # non-negative integer number of days after easter
}

ical_rrule_hsh = {
    'EXDATE': '-',
    'RDATE': '+',
    'FREQ': 'r',  # unicode
    'INTERVAL': 'i',  # positive integer
    'COUNT': 'c',  # total count positive integer
    'BYSETPOS': 's',  # integer
    'UNTIL': 'u',  # unicode
    'BYMONTH': 'M',  # integer 1...12
    'BYMONTHDAY': 'm',  # positive integer
    'BYWEEKNO': 'W',  # positive integer
    'BYDAY': 'w',  # integer 0 (SU) ... 6 (SA)
    # 'BYWEEKDAY': 'w',  # integer 0 (SU) ... 6 (SA)
    'BYHOUR': 'h',  # positive integer
    'BYMINUTE': 'n',  # positive integer
    'BYEASTER': 'E',  # non negative integer number of days after easter
}

# don't add f and u - they require special processing in get_rrulestr
rrule_keys = ['i', 'm', 'M', 'w', 'W', 'h', 'n', 't', 's', 'E']
ical_rrule_keys = ['f', 'i', 'm', 'M', 'w', 'W', 'h', 'n', 't', 's', 'u']

# ^ Presidential election day @s 2004-11-01 12am
#   @r y &i 4 &m 2, 3, 4, 5, 6, 7, 8 &M 11 &w TU

freq_hsh = {
    'y': 'YEARLY',
    'm': 'MONTHLY',
    'w': 'WEEKLY',
    'd': 'DAILY',
    'h': 'HOURLY',
    'n': 'MINUTELY',
    'E': 'EASTERLY',
}

ical_freq_hsh = {
    'YEARLY': 'y',
    'MONTHLY': 'm',
    'WEEKLY': 'w',
    'DAILY': 'd',
    'HOURLY': 'h',
    'MINUTELY': 'n',
    # 'EASTERLY': 'e'
}

item_types = {
        '*': Event(),
        '-': Todo(),
        '%': Journal()
        }


# BEGIN:VCALENDAR
# VERSION:2.0
# PRODID:-//etm_tk 3.2.38//dgraham.us//
# BEGIN:VEVENT
# SUMMARY:Charleston Volvo Open
# DTSTART;VALUE=DATE:20190402
# UID:f42d3035fd634835a01f6193a925f32eetm
# RRULE:FREQ=DAILY;COUNT=4
# END:VEVENT
# END:VCALENDAR


def ics_to_items(ics_file=None):
    """
    Process an ics (iCalendar) file and return a corresponding hash of item hashes suitable for adding to tinydb.
    """
    logger.debug(f"ics_file: {ics_file}")
    if not os.path.isfile(ics_file):
        return False, f"Could not open {ics_file}"
    with open(ics_file, 'rb') as g:
        cal = Calendar.from_ical(g.read())
    ilst = []
    items = {}
    id = 0
    for comp in cal.walk():
        item = {}
        start = None
        t = ''  # item type
        s = ''  # @s
        e = ''  # @e
        f = ''  # @f
        tzid = comp.get('tzid')
        if comp.name == "VEVENT":
            t = '*'
            start = comp.get('dtstart')
            if start:
                s = start.to_ical().decode('utf-8')[:16]
                end = comp.get('dtend')
                if end:
                    e = end.to_ical().decode('utf-8')[:16]
                    logger.debug('start: {0}, s: {1}, end: {2}, e: {3}'.format(start, s, end, e))
                    extent = parse(e) - parse(s)
                    e = extent

        elif comp.name == "VTODO":
            t = '-'
            tmp = comp.get('completed')
            if tmp:
                f = tmp.to_ical().decode('utf-8')[:16]
            due = comp.get('due')
            start = comp.get('dtstart')
            if due:
                s = due.to_ical().decode('utf-8')
            elif start:
                s = start.to_ical().decode('utf-8')

        elif comp.name == "VJOURNAL":
            t = '%'
            tmp = comp.get('dtstart')
            if tmp:
                s = tmp.to_ical().decode('utf-8')[:16]
        else:
            continue
        id += 1
        item['itemtype'] = t
        tmp = comp.get('summary')
        if tmp:
            item['summary'] = tmp.to_ical().decode('utf-8')
        if start and 'TZID' in start.params:
            logger.debug("TZID: {0}".format(start.params['TZID']))
            item['z'] = start.params['TZID']
        if s:
            item['s'] = pen_from_fmt(s)
        if e:
            item['e'] = e
        if f:
            item['f'] = pen_from_fmt(f)
        tzid = comp.get('tzid')
        if tzid:
            logger.debug("Using tzid: {0}".format(tzid.to_ical().decode('utf-8')))
            item['z'] = tzid
        else:
            logger.debug("Using tzid: {0}".format(local_timezone))
            if local_timezone:
                item['z'] = local_timezone

        tmp = comp.get('description')
        if tmp:
            desc = tmp.to_ical().decode('utf-8').replace('\,', ',').replace('\;', ';').replace('\\n', '\n')
            item['d'] = "".join(desc) if isinstance(desc, list) else desc
        tmp = comp.get('organizer')
        if tmp:
            item['w'] =  tmp.to_ical().decode('utf-8')

        rule = comp.get('rrule')
        if rule:
            rhsh = {}
            keys = rule.sorted_keys()
            for key in keys:
                if key == 'FREQ':
                    rhsh['r'] = ical_freq_hsh[rule.get('FREQ')[0].to_ical().decode('utf-8')]
                elif key == 'UNTIL':
                    tmp = rule.get(key)
                    rhsh['u'] = pen_from_fmt(tmp[0])
                elif key == 'BYDAY':
                    tmp = rule.get(key)
                    rhsh['w'] = wkdays_decode(tmp[0])
                elif key in ical_rrule_hsh:
                    tmp = rule.get(key) #.to_ical().decode('utf-8')
                    if not isinstance(tmp, list):
                        tmp = [x.strip() for x in tmp.split(',')]
                    rhsh[ical_rrule_hsh[key]] = tmp
            item.setdefault('r', []).append(rhsh)

        tags = comp.get('categories')
        if tags:
            if type(tags) is not list:
                tags = [tags]
            tags = [x.to_ical().decode('utf-8') for x in tags]
            item['t'] = tags

        invitees = comp.get('attendee')
        if invitees:
            tmp = []
            if type(invitees) is not list:
                invitees = [invitees]
            invitees = [x.to_ical().decode('utf-8') for x in invitees]
            for x in invitees:
                if x.startswith("MAILTO:"):
                    x = x[7:]
                tmp.append(x)
            item['n'] = tmp

        rdates = comp.get('rdate')
        if rdates:
            if type(rdates) is not list:
                rdates = [rdates]
            rdates = [pen_from_fmt(x.to_ical().decode('utf-8')[:16]) for x in rdates]
            item['+'] = rdates

        exdates = comp.get('exdate')
        if exdates:
            if type(exdates) is not list:
                exdates = [exdates]
            exdates = [pen_from_fmt(x.to_ical().decode('utf-8')[:16]) for x in exdates]
            item['-'] = exdates

        # items[f"{id}"] = item
        items[id] = item
    return items

# def ics_to_text(ics=None):
#     """
#     Convert an ics (iCalendar) file to corresponding list of etm text entries and return a tuple (Success, string list)
#     """
#     if not os.path.isfile(ics):
#         return False, f"Could not open {ics}"
#     logger.debug(f"ics: {0}")
#     with open(ics, 'rb') as g:
#         cal = Calendar.from_ical(g.read())
#     ilst = []
#     for comp in cal.walk():
#         clst = []
#         start = None
#         t = ''  # item type
#         s = ''  # @s
#         e = ''  # @e
#         f = ''  # @f
#         tzid = comp.get('tzid')
#         if comp.name == "VEVENT":
#             t = '*'
#             start = comp.get('dtstart')
#             if start:
#                 s = start.to_ical().decode('utf-8')[:16]
#                 end = comp.get('dtend')
#                 if end:
#                     e = end.to_ical().decode('utf-8')[:16]
#                     logger.debug('start: {0}, s: {1}, end: {2}, e: {3}'.format(start, s, end, e))
#                     extent = parse(e) - parse(s)
#                     e = fmt_period(extent)

#         elif comp.name == "VTODO":
#             t = '-'
#             tmp = comp.get('completed')
#             if tmp:
#                 f = pen_from_fmt(tmp.to_ical().decode('utf-8')[:16])
#             due = comp.get('due')
#             start = comp.get('dtstart')
#             if due:
#                 s = due.to_ical().decode('utf-8')[:16]
#             elif start:
#                 s = start.to_ical().decode('utf-8')[:16]

#         elif comp.name == "VJOURNAL":
#             t = '%'
#             tmp = comp.get('dtstart')
#             if tmp:
#                 s = tmp.to_ical().decode('utf-8')[:16]
#         else:
#             continue
#         summary = comp.get('summary')
#         clst = [t, summary]
#         if start:
#             if 'TZID' in start.params:
#                 logger.debug("TZID: {0}".format(start.params['TZID']))
#                 clst.append('@z %s' % start.params['TZID'])

#         if s:
#             clst.append("@s %s" % pen_from_fmt(s))
#         if e:
#             clst.append("@e %s" % e)
#         if f:
#             clst.append("@f %s" % pen_from_fmt(f))
#         tzid = comp.get('tzid')
#         if tzid:
#             clst.append("@z %s" % tzid.to_ical().decode('utf-8'))
#             logger.debug("Using tzid: {0}".format(tzid.to_ical().decode('utf-8')))
#         else:
#             logger.debug("Using tzid: {0}".format(local_timezone))
#             if local_timezone:
#                 clst.append("@z {0}".format(local_timezone))

#         tmp = comp.get('description')
#         if tmp:
#             clst.append("@d %s" % tmp.to_ical().decode('utf-8').replace('\,', ',').replace('\;', ';'))
#         tmp = comp.get('organizer')
#         if tmp:
#             clst.append("@w %s".tmp.to_ical().decode('utf-8'))

#         rule = comp.get('rrule')
#         if rule:
#             rlst = []
#             keys = rule.sorted_keys()
#             for key in keys:
#                 print(f'processing key: {key}')
#                 if key == 'FREQ':
#                     rlst.append(ical_freq_hsh[rule.get('FREQ')[0].to_ical().decode('utf-8')])
#                 elif key == 'UNTIL':
#                     tmp = rule.get(key)
#                     rlst.append('&u %s' % tmp[0].strftime("%Y-%m-%d %H:%M"))
#                 elif key in ical_rrule_hsh:
#                     rlst.append("&%s %s" % (
#                         ical_rrule_hsh[key],
#                         ", ".join(map(str, rule.get(key)))))
#             clst.append("@r %s" % " ".join(rlst))

#         tags = comp.get('categories')
#         if tags:
#             if type(tags) is list:
#                 tags = [x.to_ical().decode('utf-8') for x in tags]
#                 for tag in tags:
#                     clst.append(f"@t {tag}")
#             else:
#                 clst.append(f"@t {tags}")

#         invitees = comp.get('attendee')
#         if invitees:
#             if type(invitees) is not list:
#                 invitees = [invitees]
#             invitees = [x.to_ical().decode('utf-8') for x in invitees]
#             for x in invitees:
#                 if x.startswith("MAILTO:"):
#                     x = x[7:]
#                 clst.append(f"@n {x}")

#         rdates = comp.get('rdate')
#         if rdates:
#             if type(rdates) is not list:
#                 rdates = [rdates]
#             rdates = [x.to_ical().decode('utf-8')[:16] for x in rdates]
#             clst.append(f"@+ {', '.join(rdates)}")

#         exdates = comp.get('exdate')
#         if exdates:
#             if type(exdates) is not list:
#                 exdates = [exdates]
#             exdates = [x.to_ical().decode('utf-8')[:16] for x in exdates]
#             clst.append(f"@- {', '.join(exdates)}")


#         item = ' '.join(clst)
#         ilst.append(item)
#     return ilst

def item_to_ics(item):
    """
    Convert an etm item to an ical object and return a tuple (Success, object)
    """
    doc_id = item.doc_id
    if not doc_id:
        return False, None
    itemtype = item.get('itemtype')
    if not itemtype:
        return False, None
    element = item_types.get(itemtype)
    if not element:
        return False, None
    summary = item['summary']

    element.add('uid', doc_id)
    if 'z' in item:
        # pytz is required to get the proper tzid into datetimes
        tz = pytz.timezone(item['z'])
    else:
        tz = None
    if 's' in item:
        dt = item['s']
        dz = dt.replace(tzinfo=tz)
        tzinfo = dz.tzinfo
        dt = dz
        dd = dz.date()
    else:
        dt = None
        tzinfo = None
        # tzname = None

    if 'r' in item:
        # repeating
        rlst = item['r']
        for r in rlst:
            ritem = {}
            for k in ical_rrule_keys:
                if k in r:
                    if k == 'f':
                        ritem[ical_item[k]] = freq_item[r[k]]
                    elif k == 'w':
                        if type(r[k]) == list:
                            ritem[ical_item[k]] = [x.upper() for x in r[k]]
                        else:
                            ritem[ical_item[k]] = r[k].upper()
                    elif k == 'u':
                        uz = parse_str(r[k], item['z']).replace(tzinfo=tzinfo)
                        ritem[ical_item[k]] = uz
                    else:
                        ritem[ical_item[k]] = r[k]
            citem = CaselessDict(ritem)
            element.add('rrule', citem)
        if '+' in item:
            for pd in item['+']:
                element.add('rdate', pd)
        if '-' in item:
            for md in item['-']:
                element.add('exdate', md)

    element.add('summary', summary)

    if 'p' in item:
        element.add('priority', item['p'])
    if 'l' in item:
        element.add('location', item['l'])
    if 't' in item:
        element.add('categories', item['t'])
    if 'd' in item:
        element.add('description', item['d'])
    if 'm' in item:
        element.add('comment', item['m'])
    if 'w' in item:
        element.add('organizer', item['w'])
    if 'i' in item:
        for x in item['i']:
            element.add('attendee', "MAILTO:{0}".format(x))


    if item['itemtype'] in ['-', '+', '%']:
        done, due, following = getDoneAndTwo(item)
        if 's' in item:
            element.add('dtstart', dt)
        if done:
            finz = done.replace(tzinfo=tzinfo)
            fint = vDatetime(finz)
            element.add('completed', fint)
        if due:
            duez = due.replace(tzinfo=tzinfo)
            dued = vDate(duez)
            element.add('due', dued)
    elif item['itemtype'] == '^':
        element.add('dtstart', dd)
    elif dt:
        try:
            element.add('dtstart', dt)
        except:
            logger.exception('exception adding dtstart: {0}'.format(dt))

    if item['itemtype'] == '*':
        if 'e' in item and item['e']:
            ez = dz + item['e']
        else:
            ez = dz
        try:
            element.add('dtend', ez)
        except:
            logger.exception('exception adding dtend: {0}, {1}'.format(ez, tz))
    elif item['itemtype'] == '~':
        if 'e' in item and item['e']:
            element.add('comment', timedelta2Str(item['e']))
    return True, element


def export_item_to_ics(hsh, ics_file):
    """
    Export a single item in iCalendar format
    """
    cal = Calendar()
    cal.add('prodid', '-//etm//dgraham.us//')
    cal.add('version', '2.0')

    ok, element = item_to_ics(hsh)
    if not ok:
        return False
    cal.add_component(element)
    (name, ext) = os.path.splitext(ics_file)
    pname = "%s.ics" % name
    try:
        cal_str = cal.to_ical()
    except Exception:
        logger.exception("could not serialize the calendar")
        return False
    try:
        fo = open(pname, 'wb')
    except:
        logger.exception("Could not open {0}".format(pname))
        return False
    try:
        fo.write(cal_str)
    except Exception:
        logger.exception("Could not write to {0}".format(pname))
    finally:
        fo.close()
    return True


def export_active_to_ics(file2uuids, uuid2hash, ics_file, calendars=None):
    """
    Export items from active calendars to an ics file with the same name in vcal_folder.
    """
    logger.debug("ics_file: {0}; calendars: {1}".format(ics_file, calendars))

    calendar = Calendar()
    calendar.add('prodid', '-//etm//dgraham.us//'.format(version))
    calendar.add('version', '2.0')

    cal_tuples = []
    if calendars:
        for cal in calendars:
            logger.debug('processing cal: {0}'.format(cal))
            if not cal[1]:
                continue
            name = cal[0]
            regex = re.compile(r'^{0}'.format(cal[2]))
            cal_tuples.append((name, regex))
    else:
        logger.debug('processing cal: all')
        regex = re.compile(r'^.*')
        cal_tuples.append(('all', regex))

    if not cal_tuples:
        return

    logger.debug('using cal_tuples: {0}'.format(cal_tuples))
    match = False
    for rp in file2uuids:
        for name, regex in cal_tuples:
            if regex.match(rp):
                for uid in file2uuids[rp]:
                    this_hsh = uuid2hash[uid]
                    ok, element = item_to_ics(this_hsh)
                    if ok:
                        calendar.add_component(element)
                break
        if not match:
            logger.debug('skipping {0} - no match in calendars'.format(rp))

    try:
        cal_str = calendar.to_ical()
    except Exception:
        logger.exception("Could not serialize the calendar: {0}".format(calendar))
        return False
    try:
        fo = open(ics_file, 'wb')
    except:
        logger.exception("Could not open {0}".format(ics_file))
        return False
    try:
        fo.write(cal_str)
    except Exception:
        logger.exception("Could not write to {0}" .format(ics_file))
        return False
    finally:
        fo.close()
    return True

if __name__ == '__main__':
    import sys
    import pprint
    pp = pprint.PrettyPrinter(indent=3)
    if len(sys.argv) > 1:
        try:
            ics_file = sys.argv[1]
            # res = ics_to_text(ics_file)
            # print("\n".join(res))
        except Exception as e:
            print(repr(e))
        items = ics_to_items(ics_file)
        pp.pprint(items)
        # print(items)


