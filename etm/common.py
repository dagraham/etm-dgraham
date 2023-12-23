# in __main__ placed in model and view
VSEP = '⏐'   # U+23D0  this will be a de-emphasized color
FREE = '─'   # U+2500  this will be a de-emphasized color
HSEP = '┈'   #
BUSY = '■'   # U+25A0 this will be busy (event) color
CONF = '▦'   # U+25A6 this will be conflict color
TASK = '▩'   # U+25A9 this will be busy (task) color
ADAY = '━'   # U+2501 for all day events ━
USED = '◦'   # U+25E6 for used time
REPS = '↻'   # Flag for repeating items


#  model, data and ical
#  with integer prefixes
WKDAYS_DECODE = {
    '{0}{1}'.format(n, d): '{0}({1})'.format(d, n) if n else d
    for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    for n in ['-4', '-3', '-2', '-1', '', '1', '2', '3', '4']
}
WKDAYS_ENCODE = {
    '{0}({1})'.format(d, n): '{0}{1}'.format(n, d) if n else d
    for d in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
    for n in ['-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4']
}
# without integer prefixes
for wkd in ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']:
    WKDAYS_ENCODE[wkd] = wkd
