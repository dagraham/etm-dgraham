import os
import sys
from ruamel.yaml import YAML
import logging
import logging.config
logger = logging.getLogger()
from copy import deepcopy

yaml = YAML()  


class Settings():


    inp = """\
# ampm: true or false. Use AM/PM format for datetimes if 
# true else use 24 hour format. 
ampm: true

# locale: A two character locale abbreviation. E.g., "fr" 
# for French.
locale: en

# alerts: A dictionary with single-character, "alert" keys and 
# corresponding "system command" values. Note that characters 
# "t" (text message) and "e" (email) are already used.  The 
# "system command" string should be a comand with any 
# applicable arguments that could be run in a terminal. 
# Properties of the item triggering the alert can be included 
# in the command arguments using the syntax '{property}', 
# e.g., {summary} in the command string would be replaced by 
# the summary of the item. Similarly {start} by the starting 
# time, {when} by the time remaining until the starting 
# time, {location} by the @l entry and {description} by the @d 
# entry. E.g., If the event "* sales meeting @s 2019-02-12 3p" 
# triggered an alert 30 minutes before the starting time the 
# string "{summary} {when}" would expand to "sales meeting in 
# 30 minutes". E.g. on my macbook, the command
#    v: /usr/bin/say -v "Alex" "{summary}, {when}"
# would use the builtin text to speech sytem to speak the 
# item's summary followed by a slight pause (the comma) and 
# then the time remaining until the starting time, e.g., 
# "sales meeting in 20 minutes".
alerts:
    v: /usr/bin/say -v "Alex" "{summary}, {when}"

# expansions: A dictionary with 'expansion name' keys and 
# corresponding 'replacement string' values. E.g. with 
#    tennis: @e 1h30m @a 30m: d @i personal:exercise 
# then when an item containing '@x tennis' is saved the 
# '@x tennis' would be replaced by the corresponding 
# value.
expansions:
    tennis: "@e 1h30m @a 30m: d @i personal:exercise"  

# sms: Settings to send "t" (sms text message) alerts to the 
# phone numbers listed in sms_phone. E.g., if you have a 
# gmail account with email address "whatever457@gmail.com" 
# and want to text alerts to Verizon moble phone (123) 
# 456-7890 then your entries would look like
#     from: whatever457@gmail.com
#     phone: 1234567890vzwpix.com
#     pw: your gmail password
#     server: smtp.gmail.com:587
# In the phone entry above, vzwpix.com is the mms gateway
# for Verizon. Other common mms gateways are
#     AT&T:     @mms.att.net
#     Sprint:   @pm.sprint.com
#     T-Mobile: @tmomail.net
# Google "mms gateway listing" for other alternatives.
# 
# The subject of the message will be {summary} and the body 
# as specified in the template below.
sms:
    body: "{location} {when}"
    from: 
    phone: 
    pw: 
    server: 

# smtp: Settings to send "e" (email message) alerts to the 
# list of "name <email>" entries in the item's @n (attendee)
# entry using the item's summary as the subject and 
# smtp_body as the message. E.g., if you have a gmail 
# account with email address "whatever457@gmail.com", then 
# your entries would look like
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
"""


    def __init__(self, etmdir, refresh=False):
        if os.path.isdir(etmdir):
            defaults = yaml.load(Settings.inp)
            self.cfgfile = os.path.normpath(
                    os.path.join(etmdir, 'cfg.yaml'))
            if os.path.exists(self.cfgfile):
                with open(self.cfgfile, 'r') as fn:
                    user = yaml.load(fn)
                self.changes, self.settings = self.check_options(defaults, user)
                if self.changes:
                    logger.info(f"using corrected settings from {self.cfgfile}; ")
                    logger.debug(f"user: {user}; corrected: {self.settings}")
                else:
                    logger.info(f"using settings from {self.cfgfile}")
            else:
                self.changes = [f'missing {self.cfgfile} - creating from defaults']
                self.settings = defaults

            if self.changes:
                with open(self.cfgfile, 'w') as fn:
                    yaml.dump(self.settings, fn)
                logger.info(f"saved settings to {self.cfgfile}")
                logger.debug(f"changes: {self.changes}")
        else:
            raise ValueError(f"{etmdir} is not a valid directory")

    def check_options(self, defaults, user):
        # remove bad user keys
        changed = []
        new = deepcopy(user)
        for key, value in user.items():
            if key not in defaults:
                # bad user key
                del new[key]
                changed.append(f"removed {key}: {user[key]}")
            elif isinstance(defaults[key], dict):
                if not isinstance(user[key], dict):
                    new[key] = {}
                    changed.append(f"replaced {key}: {user[key]} with an empty dictionary")
                else:
                    for k, v in user[key].items():
                        if k not in defaults[key]:
                            changed.append(f"removed {key}.{k}: {new[key][k]}")
                            del new[key][k]
        # add missing defaults
        for key, value in defaults.items():
            if key not in new:
                new[key] = defaults[key]
                changed.append(f"added missing default {key}: {defaults[key]}")
            elif isinstance(defaults[key], dict):
                if not isinstance(new[key], dict):
                    new[key] = {}
                    changed.append(f"replaced {key}: {user[key]} with an empty dictionary")
                for k, v in defaults[key].items():
                    if k not in new[key]:
                        new[key][k] = defaults[key][k]
                        changed.append(f"added missing default {key}.{k}: {defaults[key][k]}")
        return changed, new




if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        etmdir = sys.argv.pop(1)
    else:
        sys.exit("The etm path must be provided.")

    settings = Settings(etmdir)
    print(settings.settings)
    print(settings.changes)
    yaml.dump(settings.settings, sys.stdout)

