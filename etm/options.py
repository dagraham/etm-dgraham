import os
import sys
from ruamel.yaml import YAML
yaml = YAML()
import logging
import logging.config
logger = logging.getLogger()
import string
import random
import re
import locale
from copy import deepcopy
from prompt_toolkit.styles.named_colors import NAMED_COLORS

locale_regex = re.compile(r'[a-z]{2}_[A-Z]{2}')

def randomString(stringLength=10):
    """Generate a random string with the combination of lowercase and uppercase letters and digits """

    letters = string.ascii_letters + 2*'0123456789'
    return ''.join(random.choice(letters) for i in range(stringLength))


class Settings():
    colors = {
        'dark': {
            'plain':        'Ivory',
            'today':        'Ivory bold',
            'inbox':        'OrangeRed',
            'pastdue':      'LightSalmon',
            'begin':        'Gold',
            'journal':       'GoldenRod',
            'event':        'LimeGreen',
            'available':    'LightSkyBlue',
            'waiting':      'SlateGrey',
            'finished':     'DarkGrey',
            },
        'light': {
            'plain':        'Black',
            'today':        'Black bold',
            'inbox':        'MediumVioletRed',
            'pastdue':      'Red',
            'begin':        'DarkViolet',
            'journal':      'Brown',
            'event':        'DarkGreen',
            'available':    'DarkBlue',
            'waiting':      'DarkSlateBlue',
            'finished':     'LightSlateGrey',
            },
    }
    secret = randomString(10)
    inp = """\
###################### IMPORTANT ########################
#
# Changes to this file only take effect when etm is next
# restarted.
#
#########################################################

# ampm: true or false. Use AM/PM format for datetimes if true
# else use 24 hour format.
ampm: true

# yearfirst and dayfirst. Each true or false. Whenever an
# ambiguous date is parsed, the dayfirst and yearfirst
# parameters control how the information is processed.
# Here is the precedence in each case:
#
#   If dayfirst is False and yearfirst is False:
#       MM-DD-YY
#       DD-MM-YY
#       YY-MM-DD
#
#   If dayfirst is True and yearfirst is False:
#       DD-MM-YY
#       MM-DD-YY
#       YY-MM-DD
#
#   If dayfirst is False and yearfirst is True:
#       YY-MM-DD
#       MM-DD-YY
#       DD-MM-YY
#
#   If dayfirst is True and yearfirst is True:
#       YY-MM-DD
#       DD-MM-YY
#       MM-DD-YY
#
yearfirst: false
dayfirst: false

# updates_interval: a non-negative integer. If positive,
# automatically check for updates every 'updates_interval'
# minutes. If zero, do not automatically check for updates.
# When enabled, a blackboard u symbol, 𝕦, will be displayed at
# the right end of status bar when an update is available
# or a question mark when the check cannot be completed
# as, for example, when there is no internet connection.
updates_interval: 0

# locale: A locale abbreviation. E.g., "en_AU" for English
# (Australia), "en_US" for English (United States), "fr_FR"
# for French (France) and so forth. Google "python locale
# abbreviatons" for a complete list."
locale: en_US

# vi_mode: true or false. Use vi keybindings for editing if
# true else use emacs style keybindings.
vi_mode: false

# secret: A string to use as the secret_key for @m masked
# entries. In etm versions after 4.0.21, the default string
# is randomly generated when this file is created or when
# the secret value is removed and etm is restarted. WARNING:
# if this key is changed, any @m entries that were made before
# the change will be unreadable after the change.
secret: %s

# omit_extent: A list of calendar names with each name
# indented on a separate line. Events with @c entries
# belonging to this list will only have their starting times
# displayed in agenda view and will neither appear nor cause
# conflicts in busy view.
omit_extent:

# keep_current: non-negative integer. If positive, the agenda
# for that integer number of weeks starting with the current
# week will be written to "current.txt" in your etm home
# directory and updated when necessary. You could, for
# example, create a link to this file in a pCloud or DropBox
# folder and have access to your current schedule on your
# mobile device.
keep_current: 0

# keep_next: true or false. If true, the 'do next' view will
# be written to "next.txt" in your etm home directory. As with
# "current.txt", a link to this file could be created in a
# pCloud or DropBox folder for access from your mobile device.
keep_next: false

# archive_after: A non-negative integer. If zero, do not
# archive items. If positive, finished tasks and events with
# last datetimes falling more than this number of years
# before the current date will automatically be archived on a
# daily basis.  Archived items are moved from the "items"
# table in the database to the "archive" table and will no
# longer appear in normal views. Note that unfinished tasks
# and records are not archived.
archive_after: 0

# num_finished: A non-negative integer. If positive, when
# saving retain only the most recent 'num_finished'
# completions of an infinitely repeating task, i.e., repeating
# without an "&c" count or an "&u" until attribute. If zero or
# not infinitely repeating, save all completions.
num_finished: 0

# usedtime_minutes: Round used times up to the nearest
# usedtime_minutes in used time views. Possible choices are 1,
# 6, 12, 30 and 60. With 1, no rounding is done and times are
# reported as hours and minutes. Otherwise, the prescribed
# rounding is done and times are reported as floating point
# hours. Note that each "@u" timeperiod is rounded before
# aggregation.
usedtime_minutes: 1

# alerts: A dictionary with single-character, "alert" keys and
# corresponding "system command" values. Note that characters
# "t" (text message) and "e" (email) are already used.  The
# "system command" string should be a comand with any
# applicable arguments that could be run in a terminal.
# Properties of the item triggering the alert can be included
# in the command arguments using the syntax '{property}', e.g.,
# {summary} in the command string would be replaced by the
# summary of the item. Similarly {start} by the starting time,
# {when} by the time remaining until the starting time,
# {location} by the @l entry and {description} by the @d entry.
# E.g., If the event "* sales meeting @s 2019-02-12 3p"
# triggered an alert 30 minutes before the starting time the
# string "{summary} {when}" would expand to "sales meeting in
# 30 minutes". E.g. on my macbook
#
#    alerts:
#        v:   /usr/bin/say -v "Alex" "{summary}, {when}"
#        ...
#
# would make the alert 'v' use the builtin text to speech sytem
# to speak the item's summary followed by a slight pause
# (the comma) and then the time remaining until the starting
# time, e.g., "sales meeting, in 20 minutes" would be triggered
# by including "@a 20m: v" in the reminder.
alerts:

# expansions: A dictionary with 'expansion name' keys and
# corresponding 'replacement string' values. E.g. with
#
#    expansions:
#        tennis: "@e 1h30m @a 30m: d @i personal:exercise"
#        ...
#
# then when "@x tennis" is entered the popup completions for
# "@x tennis" would offer replacement by the corresponding
# "@e 1h30m @a 30m: d @i personal:exercise".
expansions:

# sms: Settings to send "t" (sms text message) alerts to the
# list of phone numbers from the item's @n attendee
# entries using the item's summary and the body as specified
# in the template below as the message. E.g., suppose you
# have a gmail account with email address "who457@gmail.com"
# and want to text alerts to Verizon moble phone (123)
# 456-7890. Then your sms entries should be
#     from:   who457@gmail.com
#     pw:     your gmail password
#     server: smtp.gmail.com:587
# and your item should include the following attendee entry
#     @n 1234567890@vzwpix.com
# In the illustrative phone number, @vzwpix.com is the mms
# gateway for Verizon. Other common mms gateways are
#     AT&T:     @mms.att.net
#     Sprint:   @pm.sprint.com
#     T-Mobile: @tmomail.net
# Note. Google "mms gateway listing" for other alternatives.
sms:
    body:   "{location} {when}"
    from:
    pw:
    server:

# smtp: Settings to send "e" (email message) alerts to the
# list of email addresses from the item's @n attendee
# entries using the item's summary as the subject and body as
# the message. E.g., if you have a gmail account with email
# address "whatever457@gmail.com", then your entries should
# be
#     from: whatever457@gmail.com
#     id: whatever457
#     pw: your gmail password
#     server: smtp.gmail.com
smtp:
    body: "{location} {when}\\n{description}"
    from:
    id:
    pw:
    server:

# queries: A dictionary with short query "keys" and
# corresponding "query" values. Each "query" must be one
# that could be entered as the command in query view. Keys
# can be any short string other than 'a', 'u', 'c' or 'l'
# which are already in use.
queries:
  # unfinished tasks ordered by location
    td: m l -q equals itemtype - and ~exists f
  # usedtimes by i[:1], month and i[1:2] with d
    ui: u i[:1]; MMM YYYY; i[1:2] -a d
  # usedtimes by week and day for the past and current week
    uw: u WWW; ddd D -b weekbeg - 1w -e weekend
  # finished|start by i[:1], month and i[1:2] with u and d
    si: s i[:1]; MMM YYYY; i[1:2] -a u, d
  # items with u but missing the needed i
    mi: exists u and ~exists i
  # all archived items
    arch: a exists itemtype
  # items in which either the summary or the @d description
  # contains a match for a RGX (to be appended when executing
  # the query)
    find: includes summary d

# style: dark or light. Designed for, respectively, dark or
# light terminal backgounds. Some output may not be visible
# unless this is set correctly for your display.
style: dark

# colors: a 'namedcolor' entry for each of the following items:
#     plain:        headings such as outline branches
#     today:        the current date heading in agenda view
#     inbox:        inbox reminders
#     pastdue:      pasdue task warnings
#     begin:        begin by warnings
#     journal:      journal reminders
#     event:        event reminders
#     waiting:      waiting job reminders (unfinished prereqs)
#     finished:     finished task/job reminders
#     available:    available task/job reminders
# The default entries are suitable for the style "dark" given
# above. Note that the color names are case sensitive.
# To restore the default colors for whichever "style" you have
# set above, remove the color name for each of the items you
# want to restore and restart etm.
# To preview the namedcolors, download "namedcolors.py" from
#    "https://github.com/dagraham/etm-dgraham",
# open a terminal with your chosen background color and run
#    python3 <path to namedcolors.py>
# at the command prompt.
colors:
    plain:        'Ivory'
    today:        'Ivory bold'
    inbox:        'Yellow'
    pastdue:      'LightSalmon'
    begin:        'Gold'
    journal:      'GoldenRod'
    event:        'LimeGreen'
    waiting:      'SlateGrey'
    finished:     'DarkGrey'
    available:    'LightSkyBlue'

""" % secret

    def __init__(self, etmdir):
        if not os.path.isdir(etmdir):
            raise ValueError(f"{etmdir} is not a valid directory")
        self.colorst = Settings.colors
        self.settings = yaml.load(Settings.inp)
        # logger.debug(f"settings: {type(self.settings)}; {self.settings}")
        self.cfgfile = os.path.normpath(
                os.path.join(etmdir, 'cfg.yaml'))
        if os.path.exists(self.cfgfile):
            with open(self.cfgfile, 'r') as fn:
                try:
                    self.user = yaml.load(fn)
                except Exception as e:
                    error = f"This exception was raised when loading settings:\n---\n{e}---\nPlease correct the error in {self.cfgfile} and restart etm.\n"
                    logger.critical(error)
                    print(error)
                    sys.exit()

            if self.user and isinstance(self.user, dict):
                self.changes = self.check_options()
            else:
                self.changes = [f'invalid settings from {self.cfgfile} - using defaults']
        else:
            self.changes = [f'missing {self.cfgfile} - using defaults']

        if self.changes:
            with open(self.cfgfile, 'w', encoding='utf-8') as fn:
                yaml.dump(self.settings, fn)
            logger.info(f"updated {self.cfgfile}: {', '.join(self.changes)}")
        else:
            logger.info(f"using settings from {self.cfgfile}")


    def check_options(self):
        changed = []
        new = deepcopy(self.user)
        active_style = new.get('style', self.settings['style'])
        if active_style not in ['dark', 'light']:
            active_style = self.settings['style']
        default_colors = self.colors[active_style]
        self.settings['colors'] = default_colors
        # add missing default keys
        for key, value in self.settings.items():
            # logger.debug(f"checking {key} {value}")
            if isinstance(self.settings[key], dict):
                if key not in new or not isinstance(new[key], dict):
                    new[key] = self.settings[key]
                    changed.append(f"retaining default {key}: self.settings[key]")
                else:
                    for k, v in self.settings[key].items():
                        if k not in new[key]:
                            new[key][k] = self.settings[key][k]
                            changed.append(f"retaining default {key}.{k}: {self.settings[key][k]}")
            elif key not in new:
                new[key] = self.settings[key]
                changed.append(f"retaining default {key}: {self.settings[key]}")
        # remove invalid user keys/values
        tmp = deepcopy(new) # avoid modifying ordered_dict during iteration
        for key in tmp:
            if key not in self.settings:
                # not a valid option
                del new[key]
                changed.append(f"removed {key}: {self.user[key]}")
            elif key in ['sms', 'smtp', 'colors']:
                # only allow the specified subfields for these keys
                ks = tmp[key] or []
                for k in ks:
                    if k not in self.settings[key]:
                        changed.append(f"removed {key}.{k}: {new[key][k]}")
                        del new[key][k]
        if new['colors']:
            tmp = deepcopy(new['colors']) # avoid modifying ordered_dict during iteration
            deleted = False
            for k in tmp:
                if k not in default_colors:
                    deleted = True
                    changed.append(f"removed invalid color entry: {k}")
                    del tmp[k]
            if deleted:
                new['colors'] = tmp

            for k, v in default_colors.items():
                if k not in new['colors']:
                    changed.append(f"appending missing color entry for {k}. Using default.")
                    new['colors'][k] = default_colors[k]
                elif not new['colors'][k] or new['colors'][k].split(" ")[0] not in NAMED_COLORS:
                    changed.append(f"{new['colors'][k]} is invalid. Using default.")
                    new['colors'][k] = default_colors[k]
        else:
            new['colors'] = default_colors

        if not locale_regex.match(new['locale']):
            tmp = new['locale']
            new['locale'] = self.settings['locale']
            changed.append(f"retaining default for 'locale': {self.settings['locale']}. The provided setting, {tmp}, does have the required format.")


        if not isinstance(new['updates_interval'], int) or new['updates_interval'] < 0:
            new['updates_interval'] = self.settings['updates_interval']
            changed.append(f"retaining default for 'updates_interval': {self.settings['updates_interval']}")

        if new['usedtime_minutes'] not in [1, 6, 12, 30, 60]:
            changed.append(f"{new['usedtime_minutes']} is invalid for usedtime_minute. Using default value: 1.")
            new['usedtime_minutes'] = 1
        if  new['style'] not in ['dark', 'light']:
            new['style'] = self.settings['style']
            changed.append(f"retaining default for 'style': {self.settings['style']}")
        if  not isinstance(new['vi_mode'], bool):
            new['vi_mode'] = self.settings['vi_mode']
            changed.append(f"retaining default for 'vi_mode': {self.settings['vi_mode']}")

        if isinstance(new['keep_current'], bool):
            new['keep_current'] = 3 if new['keep_current'] else 0
            changed.append(f"Converting 'keep_current' from boolian to integer {new['keep_current']}")

        for key in self.settings:
            self.settings[key] = new.get(key, None)

        return changed


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
    logger.critical("\n######## Initializing logging #########")
    if file:
        logger.critical(f'logging for file: {file}\n    logging at level: {loglevel}\n    logging to file: {logfile}')
    else:
        logger.critical(f'logging at level: {loglevel}\n    logging to file: {logfile}')

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        etmdir = sys.argv.pop(1)
    else:
        sys.exit("The etm path must be provided.")

    settings = Settings(etmdir)
    print(settings.settings, "\n")
    print(settings.changes, "\n")
    yaml.dump(settings.settings, sys.stdout)

