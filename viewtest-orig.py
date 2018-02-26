import urwid


# This function handles input not handled by widgets.
# It's passed into the MainLoop constructor at the bottom.
def unhandled_input(key):
  if key in ('q','Q'):
    raise urwid.ExitMainLoop()
  if key == 'enter':
    try:

      ## This is the part you're probably asking about

      loop.widget = next(views).build()
    except StopIteration:
      raise urwid.ExitMainLoop()

# A class that is used to create new views, which are
# two text widgets, piled, and made into a box widget with
# urwid filler
class MainView(object):
  def __init__(self,title_text,body_text):
    self.title_text = title_text
    self.body_text = body_text

  def build(self):
    title = urwid.Text(self.title_text)
    body = urwid.Text(self.body_text)
    body = urwid.Pile([title,body])
    fill = urwid.Filler(body)
    return fill

# An iterator consisting of 3 instantiated MainView objects.
# When a user presses Enter, since that particular key sequence
# isn't handled by a widget, it gets passed into unhandled_input.
views = iter([ MainView(title_text='Page One',body_text='Lorem ipsum dolor sit amet...'),
          MainView(title_text='Page Two',body_text='consectetur adipiscing elit.'),
          MainView(title_text='Page Three',body_text='Etiam id hendrerit neque.')
        ])

initial_view = next(views).build()
loop = urwid.MainLoop(initial_view,unhandled_input=unhandled_input)
loop.run()
