import urwid

# def main():
#     term = urwid.Terminal(None)

#     mainframe = urwid.LineBox(
#         urwid.Pile([
#             ('weight', 70, term),
#             ('fixed', 1, urwid.Filler(urwid.Edit('focus test edit: '))),
#         ]),
#     )

#     def set_title(widget, title):
#         mainframe.set_title(title)

#     def quit(*args, **kwargs):
#         raise urwid.ExitMainLoop()

#     def handle_key(key):
#         if key in ('q', 'Q'):
#             quit()

#     urwid.connect_signal(term, 'title', set_title)
#     urwid.connect_signal(term, 'closed', quit)

#     loop = urwid.MainLoop(
#         mainframe,
#         handle_mouse=False,
#         unhandled_input=handle_key)

#     term.main_loop = loop
#     loop.run()


def main():
    palette =   [
                ('header', 'dark magenta,bold', 'default'),
                ('footer', 'black', 'light gray'),
                ('textentry', 'white,bold', 'dark red'),
                ('body', 'light gray', 'default'),
                ('focus', 'black', 'dark cyan', 'standout')
                ]

    textentry = urwid.Edit()
    assert textentry.get_text() == ('', []), textentry.get_text() 

    parser = OptionParser()
    parser.add_option("-u", "--username")
    parser.add_option("-p", "--password")
    (options, args) = parser.parse_args()

    if options.username and not options.password:
        print ("If you specify a username, you must also specify a password")
        exit()

    print("Loading...")

    body = MainWindow()
    if options.username:
        print ("[Logging in]")
        if body.login(options.username, options.password):
            print("[Login Successful]")
        else:
            print("[Login Failed]")
            exit()

    body.refresh()

    def edit_handler(keys, raw):
        """respond to keys while user is editing text""" 
        if keys in (['enter'],[]):
            if keys == ['enter']:
                if textentry.get_text()[0] != '':
                    # We set the footer twice because the first time we
                    # want the updated status text (loading...) to show 
                    # immediately, and the second time as a catch-all
                    body.frame.set_footer(body.footer)
                    body.set_subreddit(textentry.edit_text)
                    textentry.set_edit_text('')
            # Restore original status footer
            body.frame.set_footer(body.footer)
            body.frame.set_focus('body')
            global main_loop
            main_loop.input_filter = input_handler
            return
        return keys

    def input_handler(keys, raw):
        """respond to keys not handled by a specific widget"""
        for key in keys:
            if key == 's':
                # Replace status footer wth edit widget
                textentry.set_caption(('textentry', ' [subreddit?] ("fp" for the front page) :>'))
                body.frame.set_footer(urwid.Padding(textentry, left=4))
                body.frame.set_focus('footer')
                global main_loop
                main_loop.input_filter = edit_handler
                return
            elif key in ('j','k'):
                direction = 'down' if key == 'j' else 'up'
                return [direction]
            elif key in ('n','m'):
                direction = 'prev' if key == 'n' else 'next'
                body.switch_page(direction)
            elif key == 'u':
                body.refresh()
            elif key == 'b': # boss mode
                os.system("man python")
            elif key == '?': # help mode
                os.system("less -Ce README.markdown")
            elif key == 'q': # quit
                raise urwid.ExitMainLoop()
            return keys

    # Start ui 
    global main_loop
    main_loop = urwid.MainLoop(body.frame, palette, input_filter=input_handler)
    main_loop.run()

# def exit_on_q(key):
#     if key in ('q', 'Q', 'esc'):
#         raise urwid.ExitMainLoop()

# class QuestionBox(urwid.Filler):
#     def keypress(self, size, key):
#         if key in ('space', '@'):
#             print('got', key)
#         if key != 'enter':
#             return super(QuestionBox, self).keypress(size, key)
#         self.original_widget = urwid.Text(
#             u"Nice to meet you,\n%s.\n\nPress Q to exit." %
#             edit.edit_text)

# edit = urwid.Edit(u"What is your name?\n")
# fill = QuestionBox(edit)
# loop = urwid.MainLoop(fill, unhandled_input=exit_on_q)
# loop.run()

import re
at_regex = re.compile(r'\s@', re.MULTILINE)
amp_regex = re.compile(r'\s&', re.MULTILINE)


type_keys = {
    "*": "event",
    "-": "task",
    "#": "journal entry",
    "?": "someday entry",
    "!": "inbox entry",
}

at_keys = {
    '+': "include (list of date-times)",
    '-': "exclude (list of date-times)",
    'a': "alert (timeperiod: cmd, optional args*)",
    'b': "beginby (integer number of days)",
    'c': "calendar (string)",
    'd': "description (string)",
    'e': "extent (timeperiod)",
    'f': "finish (datetime)",
    'g': "goto (url or filepath)",
    'i': "index (colon delimited string)",
    'j': "job summary (string)",
    'l': "location (string)",
    'm': "memo (string)",
    'o': "overdue (r)estart, s)kip or k)eep)",
    'p': "priority (integer)",
    'r': "repetition frequency (y)ear, m)onth, w)eek, d)ay, h)our, M)inute",
    's': "start (date or date-time)",
    't': "tags (list of strings)",
    'v': "value (defaults key)",
    'z': "timezone (string)",
}

amp_keys = {
    'r': {
        'E': "easter: number of days before (-), on (0)  or after (+) Easter",
        'h': "hour: list of integers in 0 ... 23",
        'i': "interval: positive integer",
        'M': "month: list of integers in 1 ... 12",
        'm': "monthday: list of integers 1 ... 31",
        'n': "minute: list of integers in 0 ... 59",
        's': "set position: integer",
        'u': "until: datetime",
        'w': "weekday: list from SU, MO, ..., SA",
    },

    'j': {
        'a': "alert: timeperiod: command, args*",
        'b': "beginby: integer number of days",
        'd': "description: string",
        'e': "extent: timeperiod",
        'f': "finish: datetime",
        'l': "location: string",
        'p': "prerequisites: comma separated list of uids of immediate prereqs",
        's': "start/due: timeperiod before task start",
        'u': "uid: unique identifier: integer or string",
    },
}

methods = {}
requirements = {}
rruleset_methods = '+-r'
item_methods = 'degclmitv'
task_methods = 'fjp'
date_methods = 'sb'
datetime_methods = 'eaz' + date_methods

methods['*'] = item_methods + datetime_methods + rruleset_methods 
requirements['*'] = 's'

methods['-'] = item_methods + task_methods + datetime_methods


palette = [('I say', 'default,bold', 'default', 'bold'),]
ask = urwid.Edit(('I say', u"New * (event), - (task), # (journal entry), ? (someday entry) or ! (nbox entry):\n\n"))
reply = urwid.Text(u"")
button = urwid.Button(u'Exit')
div = urwid.Divider('-')
pile = urwid.Pile([ask, div, reply, div, button])
top = urwid.Filler(pile, valign='top')


def on_ask_change(edit, new_edit_text):
    pos_hsh = {}
    at_hsh = {}
    pos = ask.edit_pos
    active = ''
    at_parts = at_regex.split(new_edit_text)
    at_tups = []
    if at_parts:
        tmp = -1
        for part in at_parts:
            if not part:
                break
            if len(part) > 1:
                at_hsh[part[0]] = part[1:].strip()
            else:
                at_hsh[part[0]] = ''
            at_tups.append( (part[0], at_hsh[part[0]], tmp) )
            tmp += 2 + len(part)

    # print('\n', at_tups)
    if at_tups:
        itemtype, summary, end = at_tups.pop(0)
        act_key = itemtype
        act_val = summary
        for tup in at_tups:
            if tup[-1] < pos:
                act_key = tup[0]
                act_val = tup[1]
            else:
                break
        if itemtype in type_keys:
            # ask.set_caption(('I say', "{0} pos {1} act {2}\n".format(type_keys[itemtype], pos, act_key)))
            ask.set_caption(('I say', "{0} summary\n".format(type_keys[itemtype])))
            if act_key == itemtype:
                if act_val:
                    # reply.set_text(('I say', "summary (string):\n  {0}".format(act_val)))
                    reply.set_text(('I say', "{}\n  required @-keys:\n  optional @-keys:\n  default @-keys:\n".format(type_keys[itemtype])))
                else:
                    # reply.set_text(('I say', "summary (string):\n  ?"))
                    reply.set_text(('I say', "{}\n  required @-keys:\n  optional @-keys:\n  default @-keys:\n".format(type_keys[itemtype])))

            elif act_key in at_keys:
                if act_val:
                    ask.set_caption(('I say', "{0}: {1}\n".format(at_keys[act_key], act_val)))
                else:
                    ask.set_caption(('I say', "{0}:\n".format(at_keys[act_key])))
            else:
                reply.set_text(('I say', "@{0} is invalid".format(act_key)))

        else:
            ask.set_caption(('I say', u"Invalid item type '{0}'.\nUse * (event), - (task), # (journal entry), ? (someday entry) or ! (nbox entry)\n".format(itemtype)))
            summary = "{0}{1}".format(itemtype, summary)
    else:
        reply.set_text(('I say', "no tups"))


def on_exit_clicked(button):
    raise urwid.ExitMainLoop()

urwid.connect_signal(ask, 'change', on_ask_change)
urwid.connect_signal(button, 'click', on_exit_clicked)

urwid.MainLoop(top, palette).run()
