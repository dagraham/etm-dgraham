import os
import sys

import ruamel.yaml
yaml_nort = ruamel.yaml.YAML(typ='safe') # no round trip
yaml_nort.indent(mapping=2, sequence=4, offset=2)
yaml = ruamel.yaml.YAML() # use round trip
yaml.indent(mapping=2, sequence=4, offset=2)
import logging
import logging.config
logger = logging.getLogger()
import string
import random
import re
import locale
from copy import deepcopy
from prompt_toolkit.styles.named_colors import NAMED_COLORS
import etm.__version__ as version
etm_version = version.version

locale_regex = re.compile(r'[a-z]{2}_[A-Z]{2}')

def randomString(stringLength=10):
    """Generate a random string with the combination of lowercase and uppercase letters and digits """

    letters = string.ascii_letters + 2*'0123456789'
    return ''.join(random.choice(letters) for i in range(stringLength))

grey1 = '#396060', # 1 shade lighter of darkslategrey for status and menubar background
grey2 = '#1d3030', # 2 shades darker of darkslategrey for textarea background

def dict2yaml(d):
    if not d or not type(d) == dict:
        return ""
    rows = [""" """]
    for k, v in d.items():
        if v and type(v) != list:
            v = repr(v)
            v = str2yaml(v)
        rows.append(f"""  {k}: {v}""")
    ret = "\n".join(rows)
    return "\n".join(rows)

def str2yaml(s):
    ret = ""
    logger.debug(f"processing: {s}")
    if type(s) == bool:
        ret = 'true' if s else 'false'
    elif s is None or s == 'None':
        ret = ""
    elif type(s) == str:
        ret = re.sub(r'\\+\\n', r'\\n', s)
    else:
        ret = s
    if ret:
        return ret
    else:
        return

class Settings():
    """
    'settings' stores the defaults for all settings. 'settings_hsh' stores the settings that
    are user adjustable, e.g., ampm, type_colors and window_colors and is initially populated
    with the default values from settings.
    When cfg.yaml exists and is not empty, yaml (no-round-trip) is used to load its values which
    are then checked for validity and, if valid, update the settings in 'settings_hsh' and settings.
    If any changes have been made to 'settings_hsh', then f-string formatting is used to update
    the content which is then written (writelines, not dump) to cfg.yaml.
    """

    default_type_colors = {
        'dark': {
            'available':    'LightSkyBlue',
            'begin':        'Gold',
            'event':        'LimeGreen',
            'finished':     'DarkGrey',
            'inbox':        'OrangeRed',
            'journal':       'GoldenRod',
            'pastdue':      'LightSalmon',
            'plain':        'Ivory',
            'today':        'Ivory bold',
            'waiting':      'SlateGrey',
            },
        'light': {
            'available':    'DarkBlue',
            'begin':        'DarkViolet',
            'event':        'DarkGreen',
            'finished':     'LightSlateGrey',
            'inbox':        'MediumVioletRed',
            'journal':      'Brown',
            'pastdue':      'Red',
            'plain':        'Black',
            'today':        'Black bold',
            'waiting':      'DarkSlateBlue',
            },
    }

    default_window_colors = {
        'dark': {
            'ask':                     ['grey2', 'Lime', 'bold'],
            'button.focused':          ['DarkGreen', 'White'],
            'details':                 ['', 'Ivory'],
            'dialog shadow':           ['#444444', ''],
            'dialog':                  ['DarkSlateGrey', 'White'],
            'dialog-entry':            ['White', 'Black'],
            'dialog-output':           ['DarkSlateGrey', 'Lime'],
            'dialog.body label':       ['', 'White'],
            'dialog.body':             ['DarkSlateGrey', 'White'],
            'entry':                   ['grey2', 'LightGoldenRodYellow'],
            'frame.label':             ['DarkSlateGrey', 'White'],
            'menu':                    ['DarkSlateGrey', 'White'],
            'menu-bar':                ['grey1', 'White'],
            'menu-bar.selected-item':  ['#ffffff', '#000000'],
            'menu.border':             ['', '#aaaaaa'],
            'not-searching':           ['', '#222222'],
            'query':                   ['', 'Ivory'],
            'reply':                   ['grey2', 'DeepSkyBlue'],
            'shadow':                  ['#222222', ''],
            'status':                  ['grey1', 'White'],
            'status.key':              ['', '#ffaa00'],
            'status.position':         ['', '#aaaa00'],
            'text-area':               ['grey2', 'Ivory'],
            'window.border shadow':    ['', '#444444'],
            'window.border':           ['', '#888888'],
            },
        'light': {
            'ask':                     ['Cornsilk', 'Lime', 'bold'],
            'button.focused':          ['DarkGreen', 'White'],
            'details':                 ['', 'Black'],
            'dialog shadow':           ['#444444', ''],
            'dialog':                  ['DimGrey', 'White'],
            'dialog-entry':            ['White', 'Black'],
            'dialog-output':           ['DimGrey', 'Lime'],
            'dialog.body label':       ['', 'White'],
            'dialog.body':             ['DimGrey', 'White'],
            'entry':                   ['Cornsilk', 'LightGoldenRodYellow'],
            'frame.label':             ['DimGrey', 'White'],
            'menu':                    ['DimGrey', 'White'],
            'menu-bar':                ['grey1', 'White'],
            'menu-bar.selected-item':  ['#ffffff', '#000000'],
            'menu.border':             ['', '#aaaaaa'],
            'not-searching':           ['', '#777777'],
            'query':                   ['', 'Black'],
            'reply':                   ['Cornsilk', 'DeepSkyBlue'],
            'shadow':                  ['#222222', ''],
            'status':                  ['grey1', 'White'],
            'status.key':              ['', '#ffaa00'],
            'status.position':         ['', '#aaaa00'],
            'text-area':               ['Cornsilk', 'Black'],
            'window.border shadow':    ['', '#444444'],
            'window.border':           ['', '#888888'],
            }
        }

    ampm = "true"
    yearfirst = "true"
    dayfirst = "false"
    updates_interval = 0
    locale = "en_US"
    vi_mode = "false"
    secret = randomString(10)
    omit_extent = ""
    keep_current = 0
    keep_next = "false"
    archive_after = 0
    num_finished = 0
    limit_skip_display = "true"
    connecting_dots = "false"
    usedtime_minutes = 1
    alerts = ""
    expansions = ""
    sms = {"body": "{location} {when}", "from": "", "server": "", "pw": ""}
    smtp = {"body": "{location} {when}\n{description}", "from": "", "server": "", "id": "", "pw": ""}
    locations = ""
    queries = ""
    style = "dark"
    type_colors = ""
    window_colors = ""

    # use these to format the template
    settings_hsh = {
        "ampm" : ampm,
        "dayfirst" : dayfirst,
        "yearfirst" : yearfirst,
        "updates_interval" : updates_interval,
        "locale" : locale,
        "vi_mode" : vi_mode,
        "secret" : secret,
        "omit_extent" : omit_extent,
        "keep_current" : keep_current,
        "keep_next" : keep_next,
        "archive_after" : archive_after,
        "num_finished" : num_finished,
        "limit_skip_display" : limit_skip_display,
        "connecting_dots" : connecting_dots,
        "usedtime_minutes" : usedtime_minutes,
        "alerts" : dict2yaml(alerts),
        "expansions" : dict2yaml(expansions),
        "sms": dict2yaml(sms),
        "smtp": dict2yaml(smtp),
        "locations": dict2yaml(locations),
        "queries": dict2yaml(queries),
        "style" : style,
        "type_colors" : dict2yaml(type_colors),        # user modifications only
        "window_colors" : dict2yaml(window_colors),    # user modifications only
}


    template = """\
#### begin cfg.yaml ####

ampm: {ampm}
# true or false. Use AM/PM format for datetimes if true else
# use 24 hour format.

dayfirst:  {dayfirst}
yearfirst: {yearfirst}
# each true or false. Whenever an ambiguous date is parsed, dayfirst
# and yearfirst parameters control how the information is processed
# using this precedence:
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

updates_interval: {updates_interval}
# non-negative integer. If positive,  automatically check for updates
# every 'updates_interval' minutes. If zero, do not automatically
# check for updates. When enabled, a blackboard u symbol, 𝕦, will be
# displayed at the right end of status bar when an update is available
# or a question mark when the check cannot be completed as, for
# example, when there is no internet connection.

locale: {locale}
# locale abbreviation. E.g., "en_AU" for English (Australia), "en_US"
# for English (United States), "fr_FR" for French (France) and so
# forth. Google "python locale abbreviatons" for a complete list."

vi_mode: {vi_mode}
# true or false. Use vi keybindings for editing if true else use emacs
# style keybindings.

secret: {secret}
# string to use as the secret_key for @m masked entries. E.g.
# 'X6i2SGWu6m'. In etm versions after 4.0.21, the default string is
# randomly generated when this file is created or when the secret
# value is removed and etm is restarted. WARNING: if this key is
# changed, any @m entries that were made before the change will be
# unreadable after the change.

omit_extent: {omit_extent}
# A list of calendar names. Events with @c entries belonging to this
# list will only have their starting times displayed in agenda view
# and will neither appear nor cause conflicts in busy view.

keep_current: {keep_current}
# non-negative integer. If positive, the agenda for that integer
# number of weeks starting with the current week will be written to
# "current.txt" in your etm home directory and updated when necessary.
# You could, for example, create a link to this file in a pCloud or
# DropBox folder and have access to your current schedule on your
# mobile device.

keep_next: {keep_next}
# true or false. If true, the 'do next' view will be written to
# "next.txt" in your etm home directory. As with "current.txt", a link
# to this file could be created in a pCloud or DropBox folder for
# access from your mobile device.

archive_after: {archive_after}
# non-negative integer. If zero, do not archive items. If positive,
# finished tasks and events with last datetimes falling more than this
# number of years before the current date will automatically be
# archived on a daily basis.  Archived items are moved from the
# "items" table in the database to the "archive" table and will no
# longer appear in normal views. Note that unfinished tasks and
# records are not archived.

num_finished: {num_finished}
# non-negative integer
# If positive, when saving retain only the most recent
# "num_finished" completions of an infinitely repeating task,
# i.e., repeating without an "&c" count or an "&u" until
# attribute. If zero or not infinitely repeating, save all
# completions.

limit_skip_display: {limit_skip_display}
# true or false. If true, only the first instance of a task with "@o
# s" (overdue skip) will be displayed. For a task with an "@s" entry
# that is a date this will be the first instance that falls on or
# after the current date. Otherwise, when the "@s" entry is a
# datetime, this will be the first instance that falls on or after the
# current time.

connecting_dots: {connecting_dots}
# true or false. If true, display dots connecting the item summary and
# the right-hand details columns in tree views.

usedtime_minutes: {usedtime_minutes}
# 1, 6, 12, 30 or 60. Round used times up to the nearest
# usedtime_minutes in used time views. With 1, no rounding is done and
# times are reported as hours and minutes. Otherwise, the prescribed
# rounding is done and times are reported as floating point hours.
# Note that each "@u" timeperiod is rounded before aggregation.

alerts: {alerts}
# A dictionary with single-character, "alert" keys and corresponding
# "system command" values. Note that characters "t" (text message) and
# "e" (email) are already used.  The "system command" string should be
# a comand with any applicable arguments that could be run in a
# terminal. Properties of the item triggering the alert can be
# included in the command arguments using the syntax {{prop}}, e.g.,
# {{summary}} in the command string would be replaced by the summary of
# the item. Similarly {{start}} by the starting time, {{when}} by the time
# remaining until the starting time, {{location}} by the @l entry and
# {{description}} by the @d entry. E.g., If the event "* sales meeting
# @s 2019-02-12 3p" triggered an alert 30 minutes before the starting
# time the string "{{summary}} {{when}}" would expand to "sales meeting in
# 30 minutes". E.g. on my macbook
#
#    alerts:
#        v:   /usr/bin/say -v "Alex" "{{summary}}, {{when}}"
#        ...
#
# would make the alert 'v' use the builtin text to speech sytem
# to speak the item's summary followed by a slight pause
# (the comma) and then the time remaining until the starting
# time, e.g., "sales meeting, in 20 minutes" would be triggered
# by including "@a 20m: v" in the reminder.

expansions: {expansions}
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

sms: {sms}
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

smtp: {smtp}
# Settings to send "e" (email message) alerts to the list of email
# addresses from the item's @n attendee entries using the item's
# summary as the subject and body as the message. E.g., if you have a
# gmail account with email address "whatever457@gmail.com", then your
# entries should be
#     from: whatever457@gmail.com
#     id: whatever457
#     pw: your gmail password
#     server: smtp.gmail.com

locations: {locations}
# A dictionary with location group names as keys and corresponding
# lists of locations as values. When given, do next view will group
# items first by the location group name and then by the location
# within that group. Note that locations can appear under more than
# one group name. E.g.,
# locations:
#    home: [home, garage, yard, phone, computer]
#    work: [work, phone, computer, copier, fax]
# Items with a location entry that does not belong to one of these
# location groups will be listed under 'OTHER' and items without a
# location entry under 'OTHER' and then tilde.

queries: {queries}
# A dictionary with short query "keys" and corresponding "query"
# values. Each "query" must be one that could be entered as the
# command in query view. Keys can be any short string other than
# 'a', 'u', 'c' or 'l' which are already in use.
# queries:
#    td: m l -q equals itemtype - and ~exists f
#    mi: exists u and ~exists i
#    arch: a exists itemtype

style: {style}
# dark or light. Set the defaults for dark or light terminal
# backgounds. Some output may not be visible unless this is set
# correctly for your display.

type_colors: {type_colors}
# A dictionary with item component keys and corresponding named-color
# or hex-color values. The default colors are determined by the 'dark'
# or 'light' style setting as follows:
#
#     key           dark default        light default
#  -----------    -----------------   -----------------
#  available       'LightSkyBlue',     'DarkBlue',
#  begin           'Gold',             'DarkViolet',
#  event           'LimeGreen',        'DarkGreen',
#  finished        'DarkGrey',         'LightSlateGrey',
#  inbox           'OrangeRed',        'MediumVioletRed',
#  journal         'GoldenRod',        'Brown',
#  pastdue         'LightSalmon',      'Red',
#  plain           'Ivory',            'Black',
#  today           'Ivory bold',       'Black bold',
#  waiting         'SlateGrey',        'DarkSlateBlue',
#
# Explanations for the key names:
#     available:    available task/job reminders
#     begin:        begin by warnings
#     event:        event reminders
#     finished:     finished task/job reminders
#     inbox:        inbox reminders
#     journal:      journal reminders
#     pastdue:      pasdue task warnings
#     plain:        headings such as outline branches
#     today:        the current and following agenda date headings
#     waiting:      waiting job reminders (jobs with unfinished prereqs)
#
# E.g., with style 'dark', the default color for 'available' is
# 'LightSkyBlue'. This entry
#   colors:
#       available: CornFlowerBlue
# would change the 'available' color to 'CornflowerBlue' while leaving
# the other 'dark' colors unchanged.
#
# To preview the namedcolors, download "namedcolors.py" from
#    "https://github.com/dagraham/etm-dgraham",
# open a terminal with your chosen background color and run
#    python3 <path to namedcolors.py>
# at the command prompt.

window_colors: {window_colors}
# A dictionary with style component keys and corresponding lists of
#    [background, foreground, attribute]
# components. background and foreground can either be named colors,
# hex colors, or ''. Attribute is an optional font attribute such
# as 'bold' which must, of course, be supported by the font used in
# your terminal. The default settings are determined by the 'dark'
# or 'light' style setting as follows:
#
#    key                           dark                        light
# -------------------    -----------------------------  -----------------------------
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
# Note that 'grey1' (#396060) and 'grey2' (#1d3030) are colors named
# within etm itself. They are, respectively, one shade lighter and two
# shades darker than DarkSlateGrey.
#
# Any of the style attributes above can be modified. E.g., with style
# 'dark', the default for 'text-area' is [grey2, Ivory]. This entry
#   style_modifications:
#       text-area: [Black, White]
# would change the 'text-area' setting to 'Black' as the background color
# and 'White' as the foreground color while leaving the other style settings
# unchanged.

#### end cfg.yaml ####\
"""

    def __init__(self, etmdir):
        if not os.path.isdir(etmdir):
            raise ValueError(f"{etmdir} is not a valid directory")
        self.settings = {}
        logger.debug(f"settings_hsh: {self.settings_hsh}")
        default_template = Settings.template.format(**Settings.settings_hsh)
        self.settings.update(self.settings_hsh)
        logger.debug(f"default template: {default_template}")
        # self.settings = yaml_nort.load(default_template) # uses RoundTripLoader (comments)
        # yaml = YAML(typ='safe', pure=True)
        # load defaults
        active_style = self.settings_hsh['style']
        default_type_colors = self.default_type_colors[active_style]
        default_window_colors = self.default_window_colors[active_style]
        # override the settings_hsh values for type_colors and window_colors so that
        # settings will have all the possible keys
        self.settings['type_colors'] = default_type_colors
        self.settings['window_colors'] = default_window_colors
        logger.debug(f"default settings: {type(self.settings)};\n{self.settings}")
        self.cfgfile = os.path.normpath(
                os.path.join(etmdir, 'cfg.yaml'))
        if os.path.exists(self.cfgfile):
            with open(self.cfgfile, 'rb') as fn:
                try:
                    self.user = yaml_nort.load(fn) # not RoundTripLoader (no comments)
                    logger.debug(f"settings from cfg.yaml: {type(self.user)};\n{self.user}")
                except Exception as e:
                    error = f"This exception was raised when loading settings:\n---\n{e}---\nPlease correct the error in {self.cfgfile} and restart etm.\n"
                    logger.critical(error)
                    print(error)
                    sys.exit()

            if self.user and isinstance(self.user, dict):
                logger.debug(f"self.user: {self.user}")
            else:
                self.user = {}
        else:
            self.user = {}

        if self.user:
            # we have user settings that need to be checked
            self.changes = self.check_options()
        else:
            # we need to populate cfg.yaml
            self.changes = None
            with open(self.cfgfile, 'w') as fn:
                fn.writelines(default_template)

        if self.changes:
            logger.debug(f"updating template with {self.settings_hsh}")
            updated_template = Settings.template.format(**self.settings_hsh)
            logger.debug(f"template updated: {updated_template}")
            with open(self.cfgfile, 'w') as fn:
                fn.writelines(updated_template)
            logger.info(f"updated {self.cfgfile}: {', '.join(self.changes)}")
        else:
            logger.info(f"using settings from {self.cfgfile}")


    def check_options(self):
        changed = []
        new = deepcopy(self.user)
        logger.debug(f"got here with new: {new}")
        active_style = new.get('style', self.settings_hsh['style'])
        if active_style not in ['dark', 'light']:
            active_style = self.settings_hsh['style']
        default_type_colors = self.default_type_colors[active_style]
        default_window_colors = self.default_window_colors[active_style]

        cfg = deepcopy(self.settings_hsh)
        logger.debug(f"cfg copied from settings_hsh: {cfg}")
        # add missing default keys
        logger.debug(f"self.settings_hsh: {type(self.settings_hsh)}")
        for key, value in self.settings_hsh.items():
            if key in ["colors", "type_colors", "window_colors"]:
                continue
            logger.debug(f"1checking {key} {value}")
            if isinstance(self.settings_hsh[key], dict):
                if key not in new or not isinstance(new[key], dict):
                    new[key] = self.settings_hsh[key]
                    changed.append(f"retaining default {key}: self.settings_hsh[key]")
                else:
                    for k, v in self.settings_hsh[key].items():
                        if k not in new[key]:
                            new[key][k] = self.settings_hsh[key][k]
                            changed.append(f"retaining default {key}.{k}: {self.settings_hsh[key][k]}")
            elif key not in new:
                new[key] = self.settings_hsh[key]
                changed.append(f"retaining default {key}: {self.settings_hsh[key]}")
        # remove invalid user keys/values
        tmp = deepcopy(new) # avoid modifying ordered_dict during iteration
        logger.debug(f"copy of new: {type(tmp)}; {tmp}")
        for key in tmp:
            # if key in ["summary", "prop", "start", "when", "location", "description", "etm_version"]:
            #     continue
            if key not in self.settings_hsh:
                # not a valid option
                del new[key]
                changed.append(f"removed {key}: {self.user[key]}")
            elif key in ['type_colors', 'window_colors']:
                # only allow the specified subfields for these keys
                ks = tmp[key] or []
                logger.debug(f"2checking {key}: {type(tmp[key])}")
                for k in ks:
                    if k not in self.settings[key]:
                        changed.append(f"removed {key}.{k}: {new[key][k]}")
                        del new[key][k]


        if 'colors' in new and new['colors']:
            new['type_colors'] = new['colors']
            del new['colors']

        if 'type_colors' in new and new['type_colors']:
            # avoid modifying ordered_dict during iteration
            tmp = deepcopy(new['type_colors'])
            logger.debug(f"copy of new['type_colors']: {type(tmp)}; {tmp}")
            deleted = False
            for k in tmp:
                if k not in self.settings['type_colors']:
                    deleted = True
                    changed.append(f"removed invalid type_colors entry: {k}")
                    del tmp[k]
            if deleted:
                new['type_colors'] = tmp

            if new['type_colors']:
                self.settings_hsh['type_colors'] = dict2yaml(new['type_colors'])
                self.settings['type_colors'].update(new['type_colors'])

        logger.debug(f"self.settings[type_colors]: {self.settings['type_colors']}")

        if 'style_modifications' in new and new['style_modifications']:
            new['window_colors'] = new['style_modifications']
            del new['style_modifications']

        if 'window_colors' in new and new['window_colors']:
            tmp = deepcopy(new['window_colors'])
            logger.debug(f"tmp window_colors: {tmp}\ndefault_window_colors: {default_window_colors}")
            deleted = False
            for k in tmp:
                if k not in self.settings['window_colors']:
                    deleted = True
                    changed.append(f"removed invalid window_colors entry: {k}")
                    del tmp[k]
            if deleted:
                new['window_colors'] = tmp

            if new['window_colors']:
                logger.debug(f"updating window_colors\nfrom {self.settings_hsh['window_colors']}\nto {new['window_colors']}")
                self.settings_hsh['window_colors'] = dict2yaml(new['window_colors'])
                self.settings['window_colors'].update(new['window_colors'])

        logger.debug(f"self.settings[window_colors]: {self.settings['window_colors']}")

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

        for key in self.settings_hsh:
            if key in ['type_colors', 'window_colors']:
                # already processed these
                continue
            new_value = new.get(key, '')
            logger.debug(f"about to update {key}\nnew_value: {new_value}")
            if new_value is not None and new_value != self.settings_hsh.get(key, ''):
                tmp = self.settings_hsh[key]
                if type(new_value) == dict:
                    self.settings_hsh[key] = dict2yaml(new_value)
                else:
                    self.settings_hsh[key] = str2yaml(new_value)
                logger.debug(f"updating settings: {key}\nfrom {tmp}\nto {new_value}")
                self.settings[key] = new_value

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


