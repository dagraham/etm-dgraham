import json
import os
import pwd
user_name = pwd.getpwuid(os.getuid()).pw_name

class Settings:
    _config_location = 'etm_cfg.json'

    # options format: option name -> [description, starting/default value]
    options = {
        "ampm": [
            "True or False. Use AM/PM format for datetimes if True else use 24 hour format.",
            True
            ],
        "locale": [
            "Locale abbreviation or ''. Use the locale, e.g., 'fr', else use system default.",
            ''
            ],
        "calendars": [ 
            "A list of (calendar name, display boolian) tuples. The default for items without @c entries is the first calendar name in the list. Items are displayed by default in standard views if the corresponding boolian is True.",
            [
                [f'{user_name}', True],
                ['shared', True]
            ],
            ],
        "alerts": [
            "A dictionary with 'alert name' keys and corresponding 'system command' values. If 'wakeup' is among the keys, the corresponding system command will be run before any other alerts are triggered. The 'system command' string should be a comand with any applicable arguments that could be run in a terminal. Properties of the item triggering the alert can be included in the command arguments using the syntax '{property}', e.g., {summary} in the command string would be replaced byt the summary of the item. Similarly {start} by the starting time, {when} by the time remaining until the the starting time and {location} by the @l entry. E.g., If the event '* sales meeting @s 2019-02-12 3p' triggered an alert 30 minutes before the starting time the string '{summary} {when}' would expand to 'sales meeting in 30 minutes'.",
            {
                }
            ],
        "expansions": [
            "A dictionary with 'expansion name' keys and corresponding 'replacement string' values. E.g. with 'tennis' -> '@e 1h30m @a 30m @l Fitness Center @i personal:tennis', then when an item containing '@x tennis' is saved the '@x tennis' would be replaced by the corresponding value.",
            {
                }
            ]
    }

    def __init__(self):
        if os.path.exists(Settings._config_location):
            self.__dict__ = json.load(open(Settings._config_location))
        else:
            for opt in self.options:
                self.__dict__.setdefault(opt, self.options[opt][1]) 

    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        json.dump(self.__dict__, open(Settings._config_location, 'w'), indent=1)


    def set_value(self, option, value):
        self.__dict__[option] = value


    def settings(self):
        return self.__dict__


    def current_options(self):
        """
        Return options but with values from __dict__.
        """
        tmp = {}
        for key, value in self.options.items():
            tmp[key] = [self.options[key][0], self.__dict__[key]]
        return tmp


if __name__ == "__main__":
    with Settings() as settings:  # Those settings will be saved (with eventual modifications) when script exits
        settings.alerts = {
                "d": "/Applications/terminal-notifier.app/Contents/MacOS/terminal-notifier  -title '{summary}' -subtitle '{start}' -message '{when}' -sound 'default'",
                "s": "/usr/bin/afplay -v 1 /Users/dag/.etm/sounds/etm_ding.m4a",
                "v": "/usr/bin/say -v 'Alex' '{summary}, {when}'",
                }
        print(settings.settings())



