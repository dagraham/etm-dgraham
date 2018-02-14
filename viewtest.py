import urwid
import pendulum

logo = [
    "                                ",
    " ███████╗ ████████╗ ███╗   ███╗ ",
    " ██╔════╝ ╚══██╔══╝ ████╗ ████║ ",
    " █████╗      ██║    ██╔████╔██║ ",
    " ██╔══╝      ██║    ██║╚██╔╝██║ ",
    " ███████╗    ██║    ██║ ╚═╝ ██║ ",
    " ╚══════╝    ╚═╝    ╚═╝     ╚═╝ ",
    "                                ",
]

menu = [
    "--- VIEWS ----------------------------------------- ",
    "a: agenda        n: next           t: tags          ",
    "b: busy          s: someday        f: set filter    ",
    "d: done          i: index          l: set level     ",
    "m: month         h: history        c: set calendars ",
    "--- SELECTED ITEM --------------------------------- ",
    "E: edit          R: reschedule     K: klone item    ",
    "D: delete        S: schedule new   T: start timer   ",
    "F: finish        O: open link      X: export ical   ",
    "--- TOOLS ----------------------------------------- ",
    "N: new item      Q: query          F2: date calc    ",
    "J: jump to date  C: copy view      F3: yearly       ",
    "A: alerts        P: preferences    F8: quit         ",
    "                                                    ",
]

menu_text = [
    "The key bindings for the various commands are listed above. E.g., press 'a' to open agenda view. In any of the views, 'Enter' toggles the expansion of the selected node or item. In any of the dated views, 'Shift Left' and 'Shift Right' change the period displayed and 'Space' changes the display to the current date."
    ]


def unhandled_input(key):
    """
    This function handles input not handled by widgets. It's passed into the MainLoop constructor at the bottom.
    """
    if key == 'f8':
        raise urwid.ExitMainLoop()


class View:
    """
    Base view class to be inherited by others. Provides methods set_header, set_footer and set_body.
    """

    palette = [
        # ('foot', 'yellow', 'dark gray', 'standout', '', 'h8'),
        ('foot', 'yellow', 'dark gray', 'standout', '', 'h8'),
        ('title', 'yellow', 'dark gray', 'standout', '', 'h8'),
        ('key', 'white', 'dark gray','standout'),
        ('body', 'black', 'white', 'default'),
        ('focus', 'default', 'light gray', '', '', '#adf'),
        ('edit', 'black', 'dark green', 'standout', 'bold', '#ad0'), # foot in edit mode
        ('details', 'dark blue', 'white', 'bold'),    # item details
        ('errors', 'dark red', 'white', 'bold'),      # job pastdue
        (None, 'black', 'white',''),
        ('logo', 'dark blue', 'white', ''),     # logo
        ('path', 'black', 'default', ''),     # path branch
        ('buttn','black','light gray', '', '', 'g89'),
        ('buttnf','white','dark blue','bold', '', '#adf'),
        ('timer', 'black', 'yellow', 'default'),       # path branch
        ('ib', 'light red', 'default', 'default'),     # inbox
        ('oc', 'light magenta', 'default', 'default'), # occasion
        ('ev', 'dark green', 'default', 'standout', '#080', ''),    # event
        ('rm', 'dark green', 'default', 'default', '#080', ''),   # reminder
        ('td', 'dark red', 'default', 'default'),      # task pastdue
        ('jd', 'dark red', 'default', 'default'),      # job pastdue
        ('dd', 'dark red', 'default', 'default'),      # delegated pastdue
        ('jw', 'light red', 'default', 'default'),     # job scheduled and waiting
        ('ts', 'dark blue', 'default', 'default', '#00f', ''),     # task or task group scheduled
        ('js', 'dark blue', 'default', 'default', '#00f', ''),     # job scheduled and available
        ('ds', 'dark blue', 'default', 'default', '#00f', ''),     # delegated scheduled
        ('jp', 'light blue', 'default', 'default'),    # job scheduled with unfinished prereqs
        ('tu', 'light blue', 'default', 'default'),    # task or task group unscheduled
        ('ja', 'light blue', 'default', 'default'),    # job unscheduled
        ('du', 'light blue', 'default', 'default'),    # delegated unscheduled
        ('jb', 'light cyan', 'default', 'default'),    # job unscheduled with unfinished prereqs
        ('by', 'dark magenta', 'default', 'default'),  # beginby"
        ('ac', 'dark cyan', 'default', 'default'),     # action
        ('ns', 'brown', 'default', 'default'),         # note scheduled
        ('nu', 'brown', 'default', 'default'),         # note unscheduled
        ('so', 'light blue', 'default', 'default'),    # someday
        ('fn', 'dark gray', 'default', 'default'),     # finished task or job
        ('df', 'brown', 'default', 'default'),     # default
        ('dl', 'light gray', 'default', 'default'),    # deleted
        ('co', 'light gray', 'default', 'default'),    # commented out
        ]

    screen = urwid.raw_display.Screen()
    # placeholder = urwid.SolidFill()
    # Frame provices body, header and footer for each view.
    view = urwid.Frame(None, None, None)
    loop = urwid.MainLoop(
        urwid.SolidFill(),
        screen=screen,
        unhandled_input=unhandled_input,
    )


    today = None
    this_week = None

    def __init__(self, etmdir=None):
        if etmdir is None:
            etmdir = "/Users/dag/etm-qml/test/data"
        # self.view = view
        # self.loop = loop
        View.screen.set_mouse_tracking()
        View.screen.tty_signal_keys('undefined', 'undefined', 'undefined', 'undefined', 'undefined')
        View.screen.set_terminal_properties(256)
        View.screen.register_palette(View.palette)
        View.loop.widget = View.view

        self.content = []
        self.refresh()

    def process_command(self, key):
        # if key in ('q', 'Q'):
        if key == 'f8':
            raise urwid.ExitMainLoop()

    def set_footer(self, text1="", text2=""):
        t1 = urwid.Text(" {}".format(text1), align='left')
        t2 = urwid.Text("{} ".format(text2), align="right")
        # if alert:
        #     alrt = urwid.Text(" {} ".format(alert), align="center")
        # else:
        #     # alrt = urwid.Text(urwid.Button("{}".format(alert)), align="center")
        #     alrt = urwid.Text(" 5:30pm+2 ", align="right")
        View.view.footer = urwid.AttrMap(urwid.Columns([t1, ('fixed', len(text2)+1, t2)]), 'foot')

    def set_header(self, text1="event and task manager", text2="F1:help"):
        t1 = urwid.Text(" {}".format(text1), align="left")
        t2 = urwid.Text("{} ".format(text2), align='right')
        View.view.header = urwid.AttrMap(urwid.Columns([t1, ('fixed', len(text2)+1, t2)]), "title")

    def set_body(self):
        """

        """
        # listbox will provide the body or main panel of the view (Frame)
        View.view.body = urwid.AttrMap(urwid.ListBox(self.content),
            'body', None)

    def add_centered(self, list_of_strings=[], style=None):
        """

        """
        self.content.extend([urwid.AttrMap(urwid.Text(x, align='center'), style, None)  for x in list_of_strings])

    def add_wrapped(self, list_of_strings=[], style=None):
        """

        """
        self.content.extend([urwid.AttrMap(urwid.Text(x, wrap="space"), style, None) for x in list_of_strings])

    @classmethod
    def refresh(cls, *args):
        now = pendulum.Pendulum.now()
        nxt = 60 - now.second
        cls.loop.set_alarm_in(nxt, cls.refresh)
        td = now.date()
        if td != cls.today:
            View.today = td
            cls.new_day()
            yw = now.isocalendar()[:2]
            if yw != cls.this_week:
                cls.this_week = yw
                cls.new_week()
        cls.set_footer(cls, text1=now.format("h:mmA ddd MMM D", formatter='alternative'))

    @classmethod
    def new_day(cls):
        cls.set_footer("new day")

    @classmethod
    def new_week(cls):
        cls.set_footer("new week")


class ViewDecorator(View):

    def __init__(self, view): 
        super().__init__() 
        self.view = view

help_view = View()
help_view.set_header()
help_view.add_centered(logo, 'logo')
help_view.add_centered(menu, 'details')
help_view.add_wrapped(menu_text, 'body')
help_view.set_body()
help_view.loop.run()

# loop = urwid.MainLoop(help_view,unhandled_input=unhandled_input)
# loop.run()


"""
TODO
Trees

views return rows that tree add_rows and format_output prepares for display
    self.tree.clear()
    self.tree.add_rows(show)
    self.tree.format_output()
    output = self.tree.output

"""
