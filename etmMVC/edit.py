# Last Edited: Mon 05 Feb 2018 10:00 EST
import urwid
from model import check_entry, str2hsh
import os
import sys
import inspect
import difflib

# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(
    inspect.currentframe()))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)



class ButtonLabel(urwid.SelectableIcon):
    def __init__(self, text):
        curs_pos = len(text.strip())
        urwid.SelectableIcon.__init__(self, text, cursor_position=curs_pos)


class BracketButton(urwid.Button):
    '''
    - override __init__ to use our ButtonLabel instead of urwid.SelectableIcon

    - make button_left and button_right plain strings and variable width -
      any string, including an empty string, can be set and displayed

    - otherwise, we leave Button behaviour unchanged
    '''
    button_left = "["
    button_right = "]"

    def __init__(self, label, on_press=None, user_data=None):
        self._label = ButtonLabel("")
        cols = urwid.Columns([
            ('fixed', len(self.button_left), urwid.Text(self.button_left)),
            self._label,
            ('fixed', len(self.button_right), urwid.Text(self.button_right))],
            dividechars=1)
        super(urwid.Button, self).__init__(cols)

        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

        self.set_label(label)

class BareButton(urwid.Button):
    '''
    - override __init__ to use our ButtonLabel instead of urwid.SelectableIcon

    - make button_left and button_right plain strings and variable width -
      any string, including an empty string, can be set and displayed

    - otherwise, we leave Button behaviour unchanged
    '''
    button_left = ""
    button_right = ""

    def __init__(self, label, on_press=None, user_data=None):
        self._label = ButtonLabel("")
        cols = urwid.Columns([
            ('fixed', len(self.button_left), urwid.Text(self.button_left)),
            self._label,
            ('fixed', len(self.button_right), urwid.Text(self.button_right))],
            dividechars=1)
        super(urwid.Button, self).__init__(cols)

        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

        self.set_label(label)

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

type_prompt = u"type character for new item?"
item_types = u"item type characters:\n  *: event\n  -: task\n  #: journal entry\n  ?: someday entry\n  !: nbox entry"

palette = [
        ('say', 'dark blue,bold', 'default', 'bold'),
        ('warn', 'dark red,bold', 'default', 'bold')]

# ask sets the caption for the edit widget which will be followed by the actual entry field.
prompt = urwid.Text(type_prompt)
ask = urwid.Edit(('say', ""), multiline=True)
# reply sets the text for the reply TEXT widget
reply = urwid.Text(item_types)
save_button = BracketButton(u'Save')
exit_button = BracketButton(u'Quit')
date1 = BareButton(u' 9')
date2 = BareButton(u'10')

buttons = urwid.Padding(urwid.GridFlow(
    [save_button, exit_button], 8, 3, 1, 'left'),
     left=4, right=3, min_width=10)
dates = urwid.Padding(urwid.GridFlow(
    [date1, date2], 6, 1, 1, 'left'),
     left=4, right=3, min_width=10)
# walker = urwid.SimpleListWalker([date1, date2])
div = urwid.Divider('-')

# pile = urwid.Pile([ask, div, reply, div, save_button, exit_button])
pile = urwid.Pile([prompt, ask, div, reply, div, buttons, dates])
top = urwid.Filler(pile, valign='top')

# top.append(urwid.AttrMap(date1, None, focus_map='reversed'))
# top.append(urwid.AttrMap(date2, None, focus_map='reversed'))

def report_diff(a, b):
    res = 0, ''
    for i,s in enumerate(difflib.ndiff(a, b)):
        if s[0]==' ': 
            continue
        elif s[0]=='-':
            res = i-1, 'position {}: deleted "{}" '.format(i, s[-1])
            break
        elif s[0]=='+':
            res = i, 'position {}: added "{}" '.format(i, s[-1])
            break
    return res

old_text = ''
def on_ask_change(edit, new_text):
    global old_text
    old_text = ask.get_text()[0]
    pos, res = report_diff(old_text, new_text)
    # pos = ask.edit_pos
    a, r = check_entry(new_text, pos)
    prompt.set_text(a)
    # reply.set_text(('say', "{}\n{}\n{}".format(old_text, new_text, res)))
    reply.set_text(r)


def on_save_clicked(save_button):
    raise urwid.ExitMainLoop()

def on_exit_clicked(exit_button):
    raise urwid.ExitMainLoop()

def on_focus_changed(date1):
    raise urwid.ExitMainLoop()


urwid.connect_signal(ask, 'change', on_ask_change)
urwid.connect_signal(save_button, 'click', on_save_clicked)
urwid.connect_signal(exit_button, 'click', on_exit_clicked)
urwid.connect_signal(date1, 'click', on_exit_clicked)
urwid.connect_signal(date2, 'click', on_exit_clicked)

# urwid.connect_signal(walker, 'modified', on_focus_changed)
urwid.MainLoop(top, palette).run()
