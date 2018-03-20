#!/usr/bin/env python3

import shutil
import urwid
import re

##################
### start tree ###
##################

(_ROOT, _DEPTH, _BREADTH) = range(3)

class Node:
    def __init__(self, identifier):
        self.__identifier = identifier
        self.__children = []
        self.__is_expanded = True

    @property
    def is_expanded(self):
        return self.__is_expanded

    def toggle_expanded(self):
        self.__is_expanded = not self.__is_expanded

    @property
    def identifier(self):
        return self.__identifier

    @property
    def children(self):
        return self.__children

    def add_child(self, identifier):
        self.__children.append(identifier)


class Tree:

    def __init__(self):
        self.__nodes = {}
        self.nodeNum2Id = {}
        self.rowNum2Id = {}
        self.id2expanded = {}  # Note that clear() does not reset this.
        self.rowNum = -1
        self.nodeNum = 0
        self.output = []
        columns, rows = shutil.get_terminal_size()
        self.columns = columns
        self.clear()

    @property
    def nodes(self):
        return self.__nodes

    # def clear(self, columns=80):
    def clear(self):
        self.__nodes = {}
        self.nodeNum2Id = {}
        self.rowNum2Id = {}
        self.rowNum = -1
        self.nodeNum = 0
        self.output = []
        self.add_node("_")

    def add_node(self, identifier, parent=None):
        node = Node(identifier)
        self[identifier] = node

        if parent is not None:
            self[parent].add_child(identifier)
            if not self.id2expanded.get(identifier, True):
                self[identifier].toggle_expanded()

        return node

    def format_output(self, identifier="_", depth=_ROOT):
        children = self[identifier].children
        tab = 2
        black_box = u"\u25A0"
        white_box = u"\u25A1"
        if not self[identifier].is_expanded:
            children = []
        if depth == _ROOT:
            pass
        else:
            self.rowNum += 1
            if type(identifier) is tuple:
                # start nodeNum with 1
                dt = None
                self.nodeNum += 1
                if len(identifier) == 4:
                    tup, dt, type_num, this_id = identifier
                    attr = model.num2Type[type_num]
                elif len(identifier) == 3:
                    tup, type_num, this_id = identifier
                    attr = model.num2Type[type_num]
                else:
                    tup, this_id = identifier
                    attr = None

                self.nodeNum2Id[self.nodeNum] = (this_id, dt)
                self.rowNum2Id[self.rowNum] = (this_id, dt)
                # 11:30am-12:30pm
                # 123456789012345
                # use 15 for column 2, 2 for space and the rest for column 1
                w2 = 15
                w1 = self.columns - tab * (depth - 1) - w2 - 2
                col1 = ""
                if len(tup) >= 1:
                    col1 = "{0:<{width}}".format(tup[0], width=w1)
                if len(tup) >= 2 and tup[1]:
                    if type(tup[1]) is str:
                        col2 = "{0:^{width}}".format(tup[1][:w2], width=w2)
                    else:
                        print('problem with', tup[1])
                        col2 = "{0:^{width}}".format(tup[1].__str__(), width=w2)

                else:
                    col2 = " " * w2

                self.output.append(
                    urwid.AttrMap(
                        urwid.Text("{0}{1}  {2}".format(" " * tab * (depth - 1), col1[:w1], col2)), attr, focus_map='focus'))

            else:
                self.rowNum2Id[self.rowNum] = identifier, '_'
                self.id2expanded[identifier] = self[identifier].is_expanded
                if self[identifier].is_expanded:
                    box = white_box
                else:
                    box = black_box
                self.output.append(
                    urwid.AttrMap(
                        urwid.Text("{0}{1} {2}".format(" " * tab * (depth - 1), box, identifier.split(":")[-1])), "path", focus_map='focus'))

        depth += 1
        for child in children:
            self.format_output(child, depth)  # recursive call

    def traverse(self, identifier, mode=_DEPTH):
        # Python generator. Loosly based on an algorithm from
        # 'Essential LISP' by John R. Anderson, Albert T. Corbett,
        # and Brian J. Reiser, page 239-241
        yield identifier
        queue = self[identifier].children
        while queue:
            yield queue[0]
            expansion = self[queue[0]].children
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _BREADTH:
                queue = queue[1:] + expansion  # width-first

    def add_rows(self, rows):
        root = "_"
        paths = []
        self.add_node(root)
        for row in rows:
            for i in range(len(row)):
                if (*row[:i], row[i]) in paths:
                    continue
                else:
                    paths.append((*row[:i], row[i]))
                if i == 0:
                    parent = root
                else:
                    # parent = row[i-1]
                    parent = ":".join(row[:i])
                if i < len(row) - 1:
                    # this is part of the branch
                    child = ":".join(row[:i + 1])
                else:
                    # this is a leaf
                    child = row[i]
                self.add_node(child, parent)

    def __getitem__(self, key):
        return self.__nodes[key]

    def __setitem__(self, key, item):
        self.__nodes[key] = item

################
### end tree ###
################


class Menu:
    """
    Display a menu and respond to choices when run.
    """
    def __init__(self, etmdir=None):
        if etmdir is None:
            etmdir = "/Users/dag/etm-qml/test/data"
        self.active_view = None
        self.tree = Tree()
        self.details = False
        self.edit_active = False
        self.edit_paused = False
        self.edit_modified = False
        self.prompt_text = ""

        today = datetime.today() # FIXME
        self.selecteddate = today
        self.selectedweek = today.isocalendar()[:2]
        self.today = today.date()
        self.cb_status = {"Earlier": False, "Selected": True, "Later": False}

        self.items = None
        self.view_command = {}

        self.filter = ()  # (mtch, regex)

        self.view_names = {
            "a": "Agenda",
            "w": "Week",
            "m": "Month",
            "p": "Path",
            "t": "Tag",
            "k": "Keyword",
        }
        self.expanded = {view: {} for view in self.view_names}

        self.palette = [
            # ('foot', 'yellow', 'dark gray', 'standout', '', 'h8'),
            ('foot', 'yellow', 'dark gray', 'standout', '', 'h8'),
            ('title', 'yellow', 'dark gray', 'standout', '', 'h8'),
            ('key', 'white', 'dark gray','standout'),
            ('body', 'black', 'white', 'default'),
            ('focus', 'default', 'light gray', '', '', '#adf'),
            ('edit', 'black', 'dark green', 'standout', 'bold', '#ad0'),       # foot in edit mode
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

        self.screen = urwid.raw_display.Screen()
        self.screen.set_mouse_tracking()

        self.screen.tty_signal_keys('undefined', 'undefined', 'undefined', 'undefined', 'undefined')

        # set terminal mode and redraw chart
        self.screen.set_terminal_properties(256)
        self.screen.register_palette(self.palette)

        logo = [
            "                          ",
            " █████╗██████╗███╗   ███╗ ",
            " ██╔══╝╚═██╔═╝████╗ ████║ ",
            " ███╗    ██║  ██╔████╔██║ ",
            " ██╔╝    ██║  ██║╚██╔╝██║ ",
            " █████╗  ██║  ██║ ╚═╝ ██║ ",
            " ╚════╝  ╚═╝  ╚═╝     ╚═╝ ",
        ]


        self.menu_content = [urwid.AttrMap(urwid.Text(x, align='center'),
            'logo', None) for x in logo]

        # TODO:  preferences, alerts


        menu1 = [
            "-- VIEWS ------------------------------------------ ",
            "a: agenda        s: someday        t: tags          ",
            "b: busy          i: index          j: jump to date  ",
            "d: done          c: created        f: set filter    ",
            "n: next          m: modified       l: set level     ",
            ]

        menu2 = [
            "-- SELECTED ITEM ---------------------------------- ",
            "E: edit          R: reschedule     K: klone         ",
            "D: delete        S: schedule new   T: start timer   ",
            "F: finish        O: open link      X: export ical   ",
            ]

        menu3 = [
            "-- TOOLS ------------------------------------------ ",
            "N: new item      Q: query          F2: date calc    ",
            "J: jump to date  C: copy view      F3: yearly cal   ",
            "A: alerts        P: preferences    F8: quit         ",
        ]


        menutext = "The key bindings for the various commands are listed above. E.g., press 'a' to open agenda view. In any of the views, 'Enter' toggles the expansion of the selected node or item. In any of the dated views, 'Shift Left' and 'Shift Right' change the period displayed and 'Space' changes the display to the current date."

        menu_text = []
        menu_text.append(urwid.AttrMap(urwid.Text("", align='center'), 'details', None))
        for menu in [menu1, menu2, menu3]:
            menu_text.append(urwid.AttrMap(urwid.Text(menu[0], align='center'), 'details', None))
            menu_text.extend([urwid.AttrMap(urwid.Text(x, align='center'), 'body', None) for x in menu[1:]])
        menu_text.append(urwid.AttrMap(urwid.Text("", align='center'), 'details', None))
        menu_text.append(urwid.Text(menutext, wrap="space"))

        self.menu_content.extend(menu_text)

        self.content = urwid.SimpleListWalker(self.menu_content)

        self.saved_content = None
        self.saved_header = None
        self.saved_idx = 0

        self.listbox = urwid.ListBox(self.content)

        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'), None, None)
        self.header("event and task manager")
        self.footer("initializing ...")
        placeholder = urwid.SolidFill()

        self.loop = urwid.MainLoop(
            placeholder,
            screen=self.screen,
            # handle_mouse=True,
            unhandled_input=self.process_command,
            # pop_ups=True
        )
        self.loop.widget = self.view
        self.loop.set_alarm_in(0.001, self.init_model)

    def init_model(self, _loop=None, _data=None):
        if timeit:
            tt = TimeIt(label="initialization completed")
        self.items = model.Items(etmdir)
        self.view_command = {
            "a": self.items.agendaView,
            "w": self.items.refreshWeeks,
            "m": self.items.refreshWeeks,
            "p": self.items.pathView,
            "t": self.items.tagView,
            "k": self.items.keywordView,
        }
        self.refresh()
        yw_lst = model.getWeeks(self.selecteddate, 1, 3)
        self.items.getWeeks(yw_lst, ret=[])
        if timeit:
            tt.stop()
            logger.info(tt.msg)
        self.header("event and task manager")

    def set_prompt(self, text=None, modified=False):
        if text is not None:
            self.prompt_text = text
        t = urwid.Text(" {}".format(self.prompt_text), align='left')
        m = urwid.Text("+ " if modified else "  ", align='right')
        self.prompt = urwid.AttrMap(urwid.Columns([t, ('fixed', 2, m)]), 'edit')
        self.content[1] = self.prompt

    def footer(self, text, alert=""):
        clock = urwid.Text("{}".format(text), align='left')
        alrt = urwid.Text(" {} ".format(alert), align="right")
        # if alert:
        #     alrt = urwid.Text(" {} ".format(alert), align="center")
        # else:
        #     # alrt = urwid.Text(urwid.Button("{}".format(alert)), align="center")
        #     alrt = urwid.Text(" 5:30pm+2 ", align="right")
        self.view.footer = urwid.AttrMap(urwid.Columns([clock, ('fixed', 11, alrt)]), 'foot')

    def header(self, text=""):
        title = urwid.Text(" {}".format(text), align="left")
        f1 = urwid.Text("F1:help ", align='right')
        self.saved_header = self.view.header
        self.view.header = urwid.AttrMap(urwid.Columns([title, ('fixed', 8, f1)]), 'title')

    def refresh(self, *args):
        now = datetime.now()
        nxt = 60 - now.second
        changed = self.items.processFiles(all=False)
        if self.view.get_focus() == 'body':
            # don't reset footer if it has the focus for editing
            self.footer(arrow.now().format(" h:mma ddd MMM DD "))
            # self.footer(" {0} ".format(model.fmtDateTime(now)))
        if changed or now.date() != self.today:
            self.today = now.date()
            self.items.refreshToday()
            yw_lst = model.getWeeks(self.today, 1, 3)
            if timeit:
                tt = TimeIt(label="file change or new day")
            self.items.getWeeks(yw_lst, refresh=True)
            if timeit:
                tt.stop()
                logger.info(tt.msg)
            if self.active_view:
                self.show_view(self.active_view)
        self.loop.set_alarm_in(nxt, self.refresh)

    def get_date(self, dt):
        dt, msg = model.parse_time(dt)
        if not msg:
            self.selecteddate = dt
            self.show_view(self.active_view)
            now = datetime.now()
            self.footer(arrow.now().format(" h:mma ddd MMM DD "))
            # self.footer(" {0} ".format(model.fmtDateTime(now)))

    def restore_prompt(self, *args):
        self.edit_active = False
        self.edit_paused = False
        self.edit_modified = False
        now = datetime.now()
        self.footer(arrow.now().format(" h:mma ddd MMM DD "))
        # self.footer(" {0} ".format(model.fmtDateTime(now)))
        del self.content[-2:]
        self.content.set_focus(0)
        self.view.set_focus('body')

    def selectable(self):
        return True

    def button_press(self, button):
        status = ', '.join([x for x, v in self.cb_status.items() if v])
        logger.debug("status: {0}".format(status))
        self.view.footer = urwid.AttrWrap(urwid.Text(
            ["Pressed: ", button.get_label(), "; Status: ", status]), 'footer')

    def checkbutton_select(self, choice, state):
        logger.debug("{0}: {1}".format(choice.get_label(), state))
        self.cb_status[choice.get_label()] = state

    def show_details(self):
        focus_widget, idx = self.listbox.get_focus()
        id, dt = self.tree.rowNum2Id.get(idx, None)

        if dt == '_':
            self.tree.id2expanded[id] = not self.tree.id2expanded.get(id, True)
            self.show_view(self.active_view, d=idx)
            return

        if type(id) is not bool:
            self.details = True
            item = self.items.all_items.get(id, None)
            if item is not None:
                self.saved_idx = idx
                f, l = item.item['_fileinfo']
                if dt is not None and '_rrule' in item.item:
                    self.header("repeating: {} selected".format(model.fmtDateTime(dt)))
                else:
                    self.header("not repeating")
                # lst = [urwid.Divider(" ", 0, 0)]
                lst = []
                lst.append(urwid.AttrMap(urwid.Text(item.item["_entry"]), 'details'))
                # lst = [(urwid.AttrMap(urwid.Text(item.item["_entry"]), 'details'))]
                if '_defaults' in item.item and item.item["_defaults"]:
                    lst.append(urwid.Divider())
                    dflts = item.item['_defaults']
                    tmp = ["Defaults:"]
                    for key, value in dflts.items():
                        value = model.value2str(key, value)
                        tmp.append("  @{0} {1}".format(key, value))
                    lst.append(urwid.AttrMap(
                        urwid.Text("\n".join(str(x) for x in tmp)), None))
                if '_messages' in item.item:
                    lst.append(urwid.Divider())
                    tmp = ["Errors:"]
                    for msg in item.item['_messages']:
                        tmp.append("  {0}".format(msg))
                    lst.append(urwid.AttrMap(
                        urwid.Text("\n".join(str(x) for x in tmp)), 'errors'))
                self.content[:] = lst
                self.content.set_focus(0)


    def confirm(self, editor=True):
        """

        """
        if editor:
            msg = "cancel edit and lose changes"
            quit = self.restore_prompt()
        else:
            msg = "exit etm"
            quit = self.quit_etm

        e = FooterEdit(' {}?: [yn] '.format(msg), "", edit_pos=None)
        self.view.footer = urwid.Columns([urwid.AttrMap(e, 'edit')])
        urwid.connect_signal(e, 'change', quit)
        urwid.connect_signal(e, 'quit', self.restore_prompt)
        self.view.footer.set_focus(0)
        self.view.set_focus('footer')


    def save_edit(self, *args):
        self.restore_prompt()
        # TODO: implement save

    def set_edit_modified(self, *args):
        self.edit_modified = True
        self.set_prompt(text=None, modified=True)

    def quit_etm(self, widget, confirm):
        confirm = confirm.lower() == 'y'
        if confirm:
            raise urwid.ExitMainLoop()
        else:
            pass


    def process_command(self, input):
        if urwid.is_mouse_event(input):
            event, button, col, row = input
            size = self.screen.get_cols_rows()
            vis = self.listbox.calculate_visible(size)[1][1]
            if vis:
                start_row = int(vis[-1][-2])
            else:
                start_row = 0
            focus = 'body'
            if event == 'ctrl mouse release':
                self.show_details()
            else:
                try:
                    self.listbox.set_focus(min(max(start_row + row - 1, 0), len(self.listbox.body)-1))
                except TypeError as e:
                    print(start_row, row)
                    pass
            # return self.listbox.mouse_event(size, event, button, col, row, focus)
            return input

        logger.debug('key: "{}"'.format(input))
        if self.details:
            if input == 'f8':
                self.confirm(False)

            if input in ['enter']:
                self.details = False
                if self.saved_header is not None:
                    self.view.header = self.saved_header
                if self.saved_content is not None:
                    self.content[:] = self.saved_content
                    self.listbox.set_focus(self.saved_idx)
                return input
            elif input in ['e']:
                self.details = False
                self.edit_active = True
                self.content.append(urwid.Divider())
                t = urwid.Text(' event summary')
                # p = urwid.AttrMap(t, 'edit')
                self.set_prompt('event summary', modified=False)
                # self.set_prompt = urwid.Columns([urwid.AttrMap(t, 'edit')])

                # self.content.append(self.prompt)
                e = ItemEdit('', '* Test item', edit_pos=None, multiline=True)
                done = urwid.connect_signal(e, 'done', self.save_edit)
                quit = urwid.connect_signal(e, 'quit', self.confirm )
                modified = urwid.connect_signal(e, 'change', self.set_edit_modified)
                self.content.append(e)
                self.content.set_focus(len(self.listbox.body)-1)

        else:
            if input == 'f8':
                if self.edit_modified:
                    self.confirm(True)
                else:
                    self.confirm(False)

            elif input in ['enter']:
                self.show_details()
                return input

            elif input == "home":
                self.listbox.set_focus(0)
                return input

            elif input == "end":
                self.listbox.set_focus(len(self.listbox.body)-1)
                return input


            elif input == "f1":
                self.content[:] = self.menu_content
                self.header("event and task manager")
                return input

            elif input =="j" and self.active_view in ["w", "m"]:
                # self.frame.footer = e = FooterEdit('Date: ', "now", edit_pos=1)
                e = FooterEdit(' date: ', "", edit_pos=None)
                self.view.footer = urwid.Columns([urwid.AttrMap(e, 'edit')])
                done = urwid.connect_signal(e, 'done', self.get_date)
                quit = urwid.connect_signal(e, 'quit', self.restore_prompt)
                self.view.footer.set_focus(0)
                self.view.set_focus('footer')

            elif input == 'f' and self.active_view:
                # self.frame.footer = e = FooterEdit('Date: ', "now", edit_pos=1)
                e = FooterEdit(' filter: ', "", edit_pos=None)
                self.view.footer = urwid.Columns([urwid.AttrMap(e, 'edit')])
                changed = urwid.connect_signal(e, 'change', self.set_filter)
                quit = urwid.connect_signal(e, 'quit', self.clear_filter)
                self.view.footer.set_focus(0)
                self.view.set_focus('footer')

            elif input == 'l' and self.active_view:
                e = FooterEdit(' level: ', "", edit_pos=None)
                self.view.footer = urwid.Columns([urwid.AttrMap(e, 'edit')])
                done = urwid.connect_signal(e, 'done', self.set_depth)
                quit = urwid.connect_signal(e, 'quit', self.restore_prompt)
                self.view.footer.set_focus(0)
                self.view.set_focus('footer')

            elif input == ' ' and self.active_view in ["w", "m"]:
                self.selecteddate = datetime.today()
                self.selectedweek = datetime.today().isocalendar()[:2]
                self.show_view(self.active_view)

            elif input == 'shift left' and self.active_view in ["w", "m"]:
                if self.active_view == "w":
                    self.selecteddate = self.selecteddate - timedelta(days=7)
                elif self.active_view == "m":
                    self.selecteddate = self.selecteddate.replace(day=1) - timedelta(days=1)
                self.show_view(self.active_view, d=0)

            elif input in ['up', 'left']:
                focus_widget, idx = self.listbox.get_focus()
                if idx is not None and idx > 0:
                    idx = idx-1
                    self.listbox.set_focus(idx)
                elif self.active_view in ["w", "m"]:
                    if self.active_view == "w":
                        self.selecteddate = self.selecteddate - timedelta(days=7)
                    elif self.active_view == "m":
                        self.selecteddate = self.selecteddate.replace(day=1) - timedelta(days=1)
                    self.show_view(self.active_view, d=-1)
                # else:
                #     idx = 0
                #     self.listbox.set_focus(idx)

            elif input == 'shift right' and self.active_view in ["w", "m"]:
                focus_widget, idx = self.listbox.get_focus()
                if self.active_view == "w":
                    self.selecteddate = self.selecteddate + timedelta(days=7)
                elif self.active_view == "m":
                    self.selecteddate = self.selecteddate.replace(day=28) + timedelta(days=4)
                self.show_view(self.active_view, d=0)

            elif input in ['down', 'right']:
                focus_widget, idx = self.listbox.get_focus()
                if idx is not None and idx < len(self.listbox.body) - 1:
                    idx = idx+1
                    self.listbox.set_focus(idx)
                elif self.active_view in ["w", "m"]:
                    if self.active_view == "w":
                        self.selecteddate = self.selecteddate + timedelta(days=7)
                    elif self.active_view == "m":
                        self.selecteddate = self.selecteddate.replace(day=28) + timedelta(days=4)
                    self.show_view(self.active_view, d=0)
                # else:
                #     idx = len(self.listbox.body) - 1
                #     self.listbox.set_focus(idx)

            elif input == 'a':
                self.show_view("a")

            elif input == 'w':
                self.show_view("w")

            elif input == 'k':
                self.show_view("k")

            elif input == 't':
                self.show_view("t")

            elif input == 'p':
                self.show_view("p")

            # Ctrl-m = Enter
            elif input == 'm':
                self.show_view("m")

            elif input == "esc":
                self.refresh()
            else:
                self.view.footer = urwid.AttrWrap(urwid.Text(
                ["Pressed: ", input]), 'footer')

                return
        return True

    def set_depth(self, depth):
        try:
            depth = int(depth)
        except:
            return
        logger.debug("expanded[{0}]: {1}".format(self.active_view, self.expanded[self.active_view]))

        if depth < 0:
            return
        elif depth == 0:
            self.expanded[self.active_view] = self.tree.id2expanded = {}
        else:
            for k, v in self.tree.id2expanded.items():
                if len(k.split(":")) >= depth:
                    self.tree.id2expanded[k] = False
                else:
                    self.tree.id2expanded[k] = True

        self.show_view(self.active_view)
        self.restore_prompt()
        # self.footer(" {0} ".format(model.fmtDateTime(now)))


    def set_filter(self, widget, fltr):
        if fltr is None:
            filter_regex = None
        # elif len(fltr) > 0 and fltr[0] in ['=', '*', '^', '!', '~', '+', '-', '%', '$', '?', '#']:
        #     mtch = True
        #     filter_regex = re.compile(r'\s+\{0}{1}'.format(fltr[0], fltr[1:]), re.IGNORECASE)
        else:
            mtch = True
            if len(fltr) > 0 and fltr[0] == '.':
                mtch = False
                fltr = fltr[1:]
            if len(fltr) > 0 and fltr[0] in ['=', '*', '^', '!', '~', '+', '-', '%', '$', '?', '#']:
                fltr = "\s+\{0}{1}".format(fltr[0], fltr[1:])

            filter_regex = re.compile(r'{0}'.format(fltr), re.IGNORECASE)
            # logger.debug('filter: {0} ({1})'.format(fltr, mtch))

        self.filter = (mtch, filter_regex)

        self.show_view(self.active_view)

    def clear_filter(self):
        self.filter = ()
        self.restore_prompt()
        self.show_view(self.active_view)

    def show_view(self, active_view, d=None):
        self.active_view = active_view
        self.tree.id2expanded = self.expanded[active_view]
        # width, height = self.screen.get_cols_rows()
        width=60
        view = "{0} View".format(self.view_names[active_view])
        tmp = []
        if timeit:
            tt = TimeIt(loglevel=2, label=view)
        if active_view == "a":
            view = "Agenda: {0}".format(model.fmtDateRange(datetime.today(), datetime.today()+timedelta(days=1), weeks=False))
        if active_view == "w":
            yw = self.selecteddate.isocalendar()[:2]
            beg_dt = model.iso_to_gregorian((*yw, 1))
            end_dt = model.iso_to_gregorian((*yw, 7))
            view = model.fmtDateRange(beg_dt, end_dt)
            tmp = self.showWeek(yw, d)
        elif active_view == "m":
            view = self.selecteddate.strftime("%B %Y")
            yw_lst = model.getMonthWeeks(self.selecteddate)
            tmp = self.showMonth(yw_lst, d)
        else:
            tmp = self.view_command[active_view]()
        self.rows = tmp
        if self.filter:
            mtch, filter_regex = self.filter
            show = []
            for x in self.rows:
                tmp = (*x[1], *x[2])
                s = " ".join(tmp)
                m = filter_regex.search(s)
                if not ((mtch and m) or (not mtch and not m)):
                    continue
                show.append((*x[1], x[2:]))
        else:
            show = [(*x[1], x[2:]) for x in self.rows]

        if timeit:
            tt.label = view
            tt.stop()
            logger.info(tt.msg)
        self.header(view)
        self.tree.clear()
        self.tree.add_rows(show)
        self.tree.format_output()
        output = self.tree.output

        self.saved_content = self.content[:] = output
        if d is None:
            idx = 0
        elif d == -1:
            idx = len(self.listbox.body) - 1
        elif d >= 0:
            idx = d
        else:
            idx = 0
        logger.debug(('idx: {0}, {1}'.format(idx, type(idx))))
        if self.listbox.body:
            self.listbox.set_focus(idx)


    def showWeek(self, yw, d=None):
        if d is None:
            # initializing or jumpto
            yw_lst = [model.prevWeek(yw), yw, model.nextWeek(yw)]
            rows = self.items.getWeeks(yw_lst, ret=[yw])
        else:
            # next or previous
            rows = self.items.getWeeks([yw], ret=[yw])
            if d == 0:
                # next: focus to row 0
                yw_lst = [model.nextWeek(yw)]
            elif d == -1:
                # prev: focus to the last row
                yw_lst = [model.prevWeek(yw)]
            else:
                # refreshing current week: focus to current row
                yw_lst = [yw]
            self.loop.set_alarm_in(0.001, self.updateCache, user_data=yw_lst)
        return rows


    def showMonth(self, yw_lst, d=None):
        if d is None:
            # initializing or jumpto
            lst = model.prevMonthWeeks(yw_lst) + yw_lst + model.nextMonthWeeks(yw_lst)
            rows = self.items.getWeeks(lst, ret=yw_lst)
        else:
            # next or previous
            rows = self.items.getWeeks(yw_lst, ret=yw_lst)
            if d == 0:
                # next
                yw_lst = model.nextMonthWeeks(yw_lst)
            elif d == -1:
                # prev
                yw_lst = model.prevMonthWeeks(yw_lst)
            else:
                # error
                pass
            self.loop.set_alarm_in(0.001, self.updateCache, user_data=yw_lst)
        return rows


    def updateCache(self, _loop=None, user_data=None):
        if user_data is None:
            return
        # _data will be a yw_lst
        self.items.getWeeks(user_data)


    def select_date(self):
        selected = input("Date: ")
        try:
            dt = parse(selected)
        except:
            print("Could not parse '{0}'".format(selected))
            return False
        self.selecteddate = dt
        return True


