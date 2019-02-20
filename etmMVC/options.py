import json
import os
import pwd
import logging
import logging.config
logger = logging.getLogger()


class Settings():

    user_name = pwd.getpwuid(os.getuid()).pw_name

    # options format: option name -> [description, starting/default value]
    options = {
        "ampm": [
            "True or False. Use AM/PM format for datetimes if True else use 24 hour format.",
            True
            ],
        "locale": [
            "2 character locale abbreviation for pendulum, e.g., 'fr', 'de', 'en'",
            "en"
            ],
        "calendars": [ 
            "A list of (calendar name, display boolian) tuples. The default for items without @c entries is the first calendar name in the list. Items are displayed by default in standard views if the corresponding boolian is True.",
            [
                [f'{user_name}', True],
                ['shared', True]
            ],
            ],
        "alerts": [
            "A dictionary with single-character, 'alert' keys and corresponding 'system command' values. Note that characters 't' (text message) and 'e' (email) are already used.  The 'system command' string should be a comand with any applicable arguments that could be run in a terminal. Properties of the item triggering the alert can be included in the command arguments using the syntax '{property}', e.g., {summary} in the command string would be replaced by the summary of the item. Similarly {start} by the starting time, {when} by the time remaining until the the starting time, {location} by the @l entry and {description} by the @d entry. E.g., If the event '* sales meeting @s 2019-02-12 3p' triggered an alert 30 minutes before the starting time the string '{summary} {when}' would expand to 'sales meeting in 30 minutes'.",
            {
                }
            ],
        "sms": [
            "Settings to send 't' (sms text message) alerts to yourself",
            {
            "sms_from": '',
            "sms_phone": '',
            "sms_pw": '',
            "sms_server": ''
            }
            ],
        "smtp": [
            "Settings to send 'e' (email message) alerts using your account. Messages will be sent to the 'name <email>' entries in the item's @n (attendees) entry using the item's summary as the subject and the @d (disscussion) entry as the message body.",
            {
            "smtp_from": '',
            "smtp_id": '',
            "smtp_pw": '',
            "smtp_server": '',
            "smtp_body": "{location} {when}\n{discussion}"
            }
            ],
        "expansions": [
            "A dictionary with 'expansion name' keys and corresponding 'replacement string' values. E.g. with 'tennis' -> '@e 1h30m @a 30m @l Fitness Center @i personal:tennis', then when an item containing '@x tennis' is saved the '@x tennis' would be replaced by the corresponding value.",
            {
                }
            ]
    }

    def __init__(self, etmdir):
        if os.path.isdir(etmdir):
            self.config_file = os.path.normpath(os.path.join(etmdir, 'cfg.json'))
            self.user_name = Settings.user_name
            if os.path.exists(self.config_file):
                self.__dict__ = json.load(open(self.config_file))
            else:
                for opt in Settings.options:
                    self.__dict__.setdefault(opt, Settings.options[opt][1]) 
        else:
            raise ValueError(f"{etmdir} is not a valid directory")

        json.dump(self.__dict__, open(self.config_file, 'w'), indent=1)
        logger.info(f"using config_file: {self.config_file}")

    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        json.dump(self.__dict__, open(self.config_file, 'w'), indent=1)


    def set_value(self, option, value):
        if option in Settings.options:
            self.__dict__[option] = value


    def settings(self):
        return self.__dict__


    def show_options(self):
        """
        Return options but with values from __dict__.
        """
        tmp = {}
        for key, value in self.options.items():
            tmp[key] = [Settings.options[key][0], self.__dict__[key]]
        return tmp

    def show_names(self):
        """
        Return a list of the option names
        """
        return [x for x in Settings.options.keys()]

    def show_description(self, name):
        """
        Return the description for name
        """
        if name in Settings.options:
            return Settings.options[name][0]
        else:
            return f"{name} is not a recognized option."


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        etmdir = sys.argv.pop(1)
    else:
        sys.exit("The etm path must be provided.")

    with Settings(etmdir) as settings:  # Those settings will be saved (with eventual modifications) when script exits
        settings.set_value('alerts', {
                "d": "/Applications/terminal-notifier.app/Contents/MacOS/terminal-notifier  -title '{summary}' -subtitle '{start}' -message '{when}' -sound 'default'",
                "s": "/usr/bin/afplay -v 1 /Users/dag/.etm/sounds/etm_ding.m4a",
                "v": "/usr/bin/say -v 'Alex' '{summary}, {when}'",
                })

        print(settings.settings())

        print(settings.show_options())

        print(settings.show_names())

        print(settings.show_description('alerts'))

        print(settings.show_description('whatever'))

        print(settings.smtp)


