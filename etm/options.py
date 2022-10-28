import os
import sys

import ruamel.yaml
# yaml = ruamel.yaml.YAML(typ='unsafe', pure=True)
yaml = ruamel.yaml.YAML()

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
ampm: true                      # true or false
# Use AM/PM format for datetimes if true else use 24 hour format.

yearfirst: true                 # true or false
dayfirst: false                 # true or false
# Whenever an ambiguous date is parsed, dayfirst and yearfirst
# parameters control how the information is processed using
# this precedence:
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

updates_interval: 0             # non-negative integer
# If positive,  automatically check for updates every
# 'updates_interval' minutes. If zero, do not automatically
# check for updates.
# When enabled, a blackboard u symbol, 𝕦, will be displayed at
# the right end of status bar when an update is available
# or a question mark when the check cannot be completed
# as, for example, when there is no internet connection.

locale: en_US                   # locale abbreviation
# E.g., "en_AU" for English (Australia), "en_US" for English
# (United States), "fr_FR" for French (France) and so forth.
# Google "python locale abbreviatons" for a complete list."

vi_mode: false                  # true or false
# Use vi keybindings for editing if true else use emacs style
# keybindings.

secret: %s                      # string
# A string to use as the secret_key for @m masked entries.
# In etm versions after 4.0.21, the default string is
# randomly generated when this file is created or when
# the secret value is removed and etm is restarted. WARNING:
# if this key is changed, any @m entries that were made before
# the change will be unreadable after the change.

omit_extent: []                 # A list of calendar names
# Events with @c entries belonging to this list will only have
# their starting times displayed in agenda view and will neither
# appear nor cause conflicts in busy view.

keep_current: 0                 # non-negative integer
# If positive, the agenda for that integer number of weeks
# starting with the current week will be written to
# "current.txt" in your etm home directory and updated when
# necessary. You could, for example, create a link to this file
# in a pCloud or DropBox folder and have access to your current
# schedule on your mobile device.

keep_next: false                # true or false
# If true, the 'do next' view will be written to "next.txt" in
# your etm home directory. As with "current.txt", a link to this
# file could be created in a pCloud or DropBox folder for access
# from your mobile device.

archive_after: 0                # non-negative integer
# If zero, do not archive items. If positive, finished tasks and
# events with last datetimes falling more than this number of
# years before the current date will automatically be archived
# on a daily basis.  Archived items are moved from the "items"
# table in the database to the "archive" table and will no
# longer appear in normal views. Note that unfinished tasks and
# records are not archived.

num_finished: 0                 # non-negative integer
# If positive, when saving retain only the most recent
# "num_finished" completions of an infinitely repeating task,
# i.e., repeating without an "&c" count or an "&u" until
# attribute. If zero or not infinitely repeating, save all
# completions.

limit_skip_display: true        # true or false
# If true, only the first instance of a task with "@o s"
# (overdue skip) will be displayed. For a task with an "@s"
# entry that is a date this will be the first instance that
# falls on or after the current date. Otherwise, when the "@s"
# entry is a datetime, this will be the first instance that
# falls on or after the current time.

connecting_dots: false          # true or false
# If true, display dots connecting the item summary and the
# right-hand details columns in tree views.

usedtime_minutes: 1             # 1, 6, 12, 30 or 60
# Round used times up to the nearest usedtime_minutes in used
# time views. With 1, no rounding is done and times are reported
# as hours and minutes. Otherwise, the prescribed rounding is
# done and times are reported as floating point hours. Note that
# each "@u" timeperiod is rounded before aggregation.

alerts:                         # dictionary
# A dictionary with single-character, "alert" keys and
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

expansions:                     # dictionary
# A dictionary with 'expansion name' keys and corresponding
# 'replacement string' values. E.g. with
#
#    expansions:
#        tennis: "@e 1h30m @a 30m: d @i personal:exercise"
#        ...
#
# then when "@x tennis" is entered the popup completions for
# "@x tennis" would offer replacement by the corresponding
# "@e 1h30m @a 30m: d @i personal:exercise".

sms:
    body:   "{location} {when}"
    from:
    pw:
    server:
# Settings to send "t" (sms text message) alerts to the
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

smtp:
    body: "{location} {when}\\n{description}"
    from:
    id:
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

locations:                      # dictionary
# A dictionary with location group names as keys and
# corresponding lists of locations as values. When given,
# do next view will group items first by the location group
# name and then by the location within that group. Note that
# locations can appear under more than one group name. E.g.,
# locations:
#    home: [home, garage, yard, phone, computer]
#    work: [work, phone, computer, copier, fax]
# Items with a location entry that does not belong to one
# of these location groups will be listed under 'OTHER' and
# items without a location entry under 'OTHER' and then tilde.

queries:                        # dictionary
# A dictionary with short query "keys" and corresponding "query"
# values. Each "query" must be one that could be entered as the
# command in query view. Keys can be any short string other than
# 'a', 'u', 'c' or 'l' which are already in use.
# queries:
#    td: m l -q equals itemtype - and ~exists f
#    mi: exists u and ~exists i
#    arch: a exists itemtype

colors:
    available:    'LightSkyBlue'
    begin:        'Gold'
    event:        'LimeGreen'
    finished:     'DarkGrey'
    inbox:        'Yellow'
    journal:      'GoldenRod'
    pastdue:      'LightSalmon'
    plain:        'Ivory'
    today:        'Ivory bold'
    waiting:      'SlateGrey'
# A dictionary with a 'named' foreground color as the value
# for each of the following keys:
#     available:    available task/job reminders
#     begin:        begin by warnings
#     event:        event reminders
#     finished:     finished task/job reminders
#     inbox:        inbox reminders
#     journal:      journal reminders
#     pastdue:      pasdue task warnings
#     plain:        headings such as outline branches
#     today:        the current date heading in agenda view
#     waiting:      waiting job reminders (unfinished prereqs)
# The default entries are suitable for the style "dark" given
# below. Note that the color names are case sensitive.
# To restore the default colors for whichever "style" you set
# below, remove the color name for each of the items you want to
# restore and restart etm.
#
# To preview the namedcolors, download "namedcolors.py" from
#    "https://github.com/dagraham/etm-dgraham",
# open a terminal with your chosen background color and run
#    python3 <path to namedcolors.py>
# at the command prompt.

style: dark                     # 'dark' or 'light'
# Set the defaults for dark or light terminal backgounds. Some
# output may not be visible unless this is set correctly for your
# display. # The 'dark' and 'light' defaults are given below:
#
#                                     dark                           light
#                        -----------------------------  -----------------------------
# ask:                    [grey2, Lime, bold]           [Cornsilk, Lime, bold]
# button.focused:         [DarkGreen, White]            [DarkGreen, White]
# details:                [, Ivory]                     [, Black]
# dialog shadow:          [#444444, ]                   [#444444, ]
# dialog:                 [DarkSlateGrey, White]        [DimGrey, White]
# dialog-entry:           [White, Black]                [White, Black]
# dialog-output:          [DarkSlateGrey, Lime]         [DimGrey, Lime]
# dialog.body label:      [, White]                     [, White]
# dialog.body:            [DarkSlateGrey, White]        [DimGrey, White]
# entry:                  [grey2, LightGoldenRodYellow] [Cornsilk, LightGoldenRodYellow]
# frame.label:            [DarkSlateGrey, White]        [DimGrey, White]
# menu:                   [DarkSlateGrey, White]        [DimGrey, White]
# menu-bar:               [grey1, White]                [grey1, White]
# menu-bar.selected-item: [#ffffff, #000000]            [#ffffff, #000000]
# menu.border:            [, #aaaaaa]                   [, #aaaaaa]
# not-searching:          [, #222222]                   [, #777777]
# query:                  [, Ivory]                     [, Black]
# reply:                  [grey2, DeepSkyBlue]          [Cornsilk, DeepSkyBlue]
# shadow:                 [#222222, ]                   [#222222, ]
# status:                 [grey1, White]                [grey1, White]
# status.key:             [, #ffaa00]                   [, #ffaa00]
# status.position:        [, #aaaa00]                   [, #aaaa00]
# text-area:              [grey2, Ivory]                [Cornsilk, Black]
# window.border shadow:   [, #444444]                   [, #444444]
# window.border:          [, #888888]                   [, #888888]
#
# Note that 'grey1' (#396060) and 'grey2' (#1d3030) are colors named within etm itself.
# They are, respectively, one shade lighter and two shades darker than DarkSlateGrey.

style_modifications:            # dictionary
# A dictionary with style component keys and corresponding lists of
#    [background, foreground, attribute]
# components. background and foreground can either be named colors,
# hex colors, or ''. Attribute is an optional font attribute such
# as 'bold' which must, of course, be supported by the font used in
# your terminal. Any of the style attributes above can be modified,
# e.g.,
# style_modifications:
#     text-area: [Black, White]
# would change the 'text-area' setting to 'Black' as the background
# color and 'White' as the foreground color.
""" % secret

    def __init__(self, etmdir):
        if not os.path.isdir(etmdir):
            raise ValueError(f"{etmdir} is not a valid directory")
        self.colorst = Settings.colors
        nort_settings = yaml.load(Settings.inp)
        logger.debug(f"nort_settings: {type(nort_settings)}; {nort_settings}")
        self.settings = ruamel.yaml.load(Settings.inp, ruamel.yaml.RoundTripLoader)
        logger.debug(f"settings: {type(self.settings)}; {self.settings}")
        self.cfgfile = os.path.normpath(
                os.path.join(etmdir, 'cfg.yaml'))
        if os.path.exists(self.cfgfile):
            with open(self.cfgfile, 'rb') as fn:
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
            with open(self.cfgfile, 'wb') as fn:
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

