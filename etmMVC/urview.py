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

palette = [('I say', 'default,bold', 'default', 'bold'),]
ask = urwid.Edit(('I say', u"new item\n"))
reply = urwid.Text(u"")
button = urwid.Button(u'Exit')
div = urwid.Divider()
pile = urwid.Pile([ask, div, reply, div, button])
top = urwid.Filler(pile, valign='top')

types = {
        '*': 'event',
        '-': 'task',
        '?': 'someday',
        '#': 'journal',
        '$': 'inbox'
        }

def on_ask_change(edit, new_edit_text):
    type_char = new_edit_text[0]
    if type_char in types:
        reply.set_text(('I say', u"%s: %s" % (types[type_char], new_edit_text)))
    else:
        reply.set_text(('I say', u"unrecognized type: %s" % type_char))

    # reply.set_text(('I say', u"got: %s" % new_edit_text[-1]))

def on_exit_clicked(button):
    raise urwid.ExitMainLoop()

urwid.connect_signal(ask, 'change', on_ask_change)
urwid.connect_signal(button, 'click', on_exit_clicked)

urwid.MainLoop(top, palette).run()
