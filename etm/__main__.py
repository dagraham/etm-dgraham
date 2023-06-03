#! ./env/bin/python
import pendulum
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError


class ConfirmationValidator(Validator):
    def validate(self, document):
        if document.text.lower() not in ('y', 'n'):
            raise ValidationError(message='Please enter either "y" or "n"', cursor_position=len(document.text))


def ask_for_confirmation(prompt_message):
    while True:
        response = prompt(f'{prompt_message} [y/n]: ', validator=ConfirmationValidator())
        if response.lower() == 'y':
            return True
        elif response.lower() == 'n':
            return False


def print_usage():

    print("""\
    Usage: etm [options]
    Options:
      -h, --help   Show this help message and exit
      [n] [path]   Set logging level 'n' where n = 1, 2, 3
                       or, if omitted, use logging level 2
                   Use 'path' as the etm home directory
                       or, if omitted, use the environmental
                       variable ETMHOME if set and the current
                       working directory otherwise."""
                )

def main():
    import sys
    import logging
    import logging.config
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logger = logging.getLogger()

    if "-h" in sys.argv or "--help" in sys.argv:
        print_usage()
        sys.exit()

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--h', '-help', '--help']:
        print("""
Usage:
    etm <

              """)
        sys.exit()

    MIN_PYTHON = (3, 7, 3)
    if sys.version_info < MIN_PYTHON:
        mv = ".".join([str(x) for x in MIN_PYTHON])
        sys.exit(f"Python {mv} or later is required.\n")
    import os
    IS_VENV = os.getenv('VIRTUAL_ENV') is not None

    import etm.__version__ as version
    etm_version = version.version
    etmhome = os.environ.get("ETMHOME")
    etmdir = etmhome if etmhome else os.getcwd()

    import etm.data as data
    import etm.view as view
    from etm.view import ETMQuery
    import etm.model as model
    import etm.report as report
    report.ETMQuery = ETMQuery

    loglevel = 2 # info
    log_levels = [str(x) for x in range(1, 6)]
    if len(sys.argv) > 1 and sys.argv[1] in log_levels:
        loglevel = int(sys.argv.pop(1))
    if len(sys.argv) > 1 and sys.argv[1] in ['model', 'view', 'data', 'rep']:
        if sys.argv[1] == 'model':
            logger.info(f"calling model doctest with etmdir: {etmdir}, argv: {sys.argv}")
            import doctest
            doctest.testmod(model)
        elif sys.argv[1] == 'view':
            logger.info(f"calling view doctest with etmdir: {etmdir}, argv: {sys.argv}")
            import doctest
            doctest.testmod(view)
        elif sys.argv[1] == 'data':
            logger.info(f"calling data doctest with etmdir: {etmdir}, argv: {sys.argv}")
            import doctest
            doctest.testmod(data)
        elif sys.argv[1] == 'rep':
            logger.info(f"calling report.main with etmdir: {etmdir}, argv: {sys.argv}")
            report.main(etmdir, sys.argv)
        sys.exit()
        # else:
        #     logger.info(f"calling model.main with etmdir: {etmdir}, argv: {sys.argv}")
        #     model.main(etmdir, sys.argv)
    if len(sys.argv) > 1:
        # use the directory being provided
        etmdir = sys.argv.pop(1)
        etmdir = os.getcwd() if etmdir == '.' else os.path.normpath(etmdir)



    print(f"using etmdir {etmdir}")
    created_etmdir = False
    # if not (os.path.exists(etmdir) and os.path.isdir(etmdir)):
    if not os.path.isdir(etmdir):
        print(f"""
The provided directory to use for etm
    {etmdir}
does not exist and will need to be created.
              """)
        if ask_for_confirmation("Do you want to continue?"):
            print("Continuing...")
            os.makedirs(etmdir)
            created_etmdir = True
            print(f'created {etmdir}')
        else:
            print("Exiting...")
            sys.exit()


    logdir = os.path.normpath(os.path.join(etmdir, 'logs'))
    backdir = os.path.normpath(os.path.join(etmdir, 'backups'))
    cfgfile = os.path.normpath(os.path.join(etmdir, 'cfg.yaml'))
    dbfile = os.path.normpath(os.path.join(etmdir, 'etm.json'))
    missing = []
    for p in [logdir, backdir, cfgfile, dbfile]:
        if not os.path.exists(p):
            missing.append(p)
    missing = "\n    ".join(missing) if missing else ""

    # condition = created_etmdir or (os.path.exists(logdir) and os.path.exists(backdir) and os.path.exists(db))
    condition = not created_etmdir and missing

    if condition:
        print(f"""\
The etm directory
     {etmdir}
is missing
    {missing}
which will need to be created.
""")
        if ask_for_confirmation("Do you want to continue?"):
            print("Continuing...")
        else:
            print("Exiting...")
            sys.exit()

    olddb = os.path.normpath(os.path.join(etmdir, 'db.json'))
    needs_update = False
    if os.path.exists(olddb) and not os.path.exists(dbfile):
        import shutil
        shutil.copy(olddb, dbfile)
        needs_update = True

    if not os.path.isdir(logdir):
        os.makedirs(logdir)

    if not os.path.isdir(backdir):
        os.makedirs(backdir)

    import etm.options as options
    setup_logging = options.setup_logging
    setup_logging(loglevel, logdir)
    options.logger = logger
    Settings = options.Settings(etmdir)

    settings = Settings.settings
    beginbusy = settings['beginbusy']
    type_colors = settings['type_colors']
    # logger.debug(f"__main__ type_colors: {type_colors}")
    window_colors = settings['window_colors']
    # logger.debug(f"__main__ window_colors: {window_colors}")

    logger.info(f"running in a virtual environment: {IS_VENV}")

    secret = settings.get('secret')
    queries = settings.get('queries')
    UT_MIN = settings.get('usedtime_minutes', 1)
    usedtime_hours = settings.get('usedtime_hours', 6)
    refresh_interval = settings.get('refresh_interval', 60)
    today = pendulum.today()
    now = pendulum.now('local')
    # We want 2 char 'en' weekday abbreviations regardless of the actual locale
    day = today.end_of('week')  # Sunday
    WA = {i: day.add(days=i).format('ddd')[:2] for i in range(1, 8)}
    midnight = pendulum.now().replace(hour=0, minute=0, second=0, microsecond=0)
    beginbusy = settings.get('beginbusy', 7)
    ampm = settings.get('ampm', True)
    show_minutes = settings.get('show_minutes', False)
    hour = pendulum.duration(hours=1)
    fmt = "hA" if ampm else "H"
    # busyhours = [(midnight + i*hour).format(fmt).lower for i in range(beginbusy, beginbusy + 14, 2)]
    busyhours = [(midnight + i*hour).format('hA').lower() for i in range(beginbusy, beginbusy + 15, 2)]
    HB = "".join([f"{h : <8}" for h in busyhours]).rstrip()
    # "".join([f"{h : <10}" for h in busyhours]).rstrip()

    # HSEP  =    '─' # U+2500  this will be a de-emphasized color
    VSEP   =    '⏐' # U+23D0  this will be a de-emphasized color
    HSEP   =    '·' # U+2500  this will be a de-emphasized color
    BUSY   =    '■' # U+25A0 this will be busy (event) color
    CONF   =    '▦' # U+25A6 this will be conflict color
    TASK   =    '▩' # U+25A9 this will be busy (task) color
    ADAY   =    '━' # U+2501 for all day events ━
    USED   =    '◦' # U+25E6 for used time


    import etm.ical as ical
    ical.logger = logger
    data.secret = secret
    data.logger = logger
    from etm.data import Mask

    # dbfile = os.path.normpath(os.path.join(etmdir, 'etm.json'))
    # cfgfile = os.path.normpath(os.path.join(etmdir, 'cfg.yaml'))
    ETMDB = data.initialize_tinydb(dbfile)
    logger.info(f"initialized TinyDB using {dbfile}")
    DBITEM = ETMDB.table('items', cache_size=None)
    DBARCH = ETMDB.table('archive', cache_size=None)
    logger.debug(f"ETMDB: {ETMDB}, number of items: {len(ETMDB)}")

    from etm.make_examples import make_examples
    from etm.model import about
    from etm.model import wrap
    from etm.model import import_file
    from etm.model import import_examples
    from etm.model import write_back
    # from etm.model import RDict
    from etm.model import item_details
    from etm.model import FINISHED_CHAR
    from etm.model import UPDATE_CHAR
    from etm.model import PIN_CHAR
    from etm.model import INBASKET_CHAR
    from etm.model import TimeIt
    model.loglevel = loglevel
    model.etm_version = etm_version
    model.secret = secret
    model.data = data
    model.ical = ical
    model.Mask = Mask
    model.WA = WA
    model.HB = HB
    model.VSEP = VSEP
    model.HSEP = HSEP
    model.BUSY = BUSY
    model.CONF = CONF
    model.ADAY = ADAY
    model.USED = USED
    model.ETMDB = ETMDB
    model.DBITEM = DBITEM
    model.DBARCH = DBARCH
    model.UT_MIN = UT_MIN
    model.usedtime_hours = usedtime_hours
    model.refresh_interval = refresh_interval
    model.beginbusy = beginbusy
    model.settings = settings
    model.logger = logger
    model.make_examples = make_examples
    model.needs_update = needs_update
    model.timers_file = os.path.join(etmdir, 'timers.pkl')
    userhome = os.path.expanduser('~')
    etmhome = os.path.join('~', os.path.relpath(etmdir, userhome)) if etmdir.startswith(userhome) else etmdir
    model.etmhome = etmhome
    # we put settings into the model namespace so model.Dataview will have it
    dataview = model.DataView(etmdir)
    datetime_calculator = model.datetime_calculator
    item = model.Item()
    format_time = model.format_time
    format_datetime = model.format_datetime
    format_duration = model.format_duration
    format_hours_and_tenths = model.format_hours_and_tenths
    # since dataview calls schedule it will also have settings
    completions = dataview.completions
    expansions = settings["expansions"]
    if expansions:
        for x in expansions:
            completions.append(f"@x {x}")
    style = dataview.settings["style"]
    parse_datetime = model.parse_datetime
    parse_duration = model.parse_duration

    # if needs_update:
    #     timer_update = TimeIt('***UPDATE***')
    #     dataview.update_datetimes_to_periods()
    #     timer_update.stop()


    view.loglevel = loglevel
    view.TimeIt = TimeIt
    view.wrap = wrap
    view.WA = WA
    view.beginbusy = beginbusy
    view.FINISHED_CHAR = FINISHED_CHAR
    view.UPDATE_CHAR = UPDATE_CHAR
    view.PIN_CHAR = PIN_CHAR
    view.INBASKET_CHAR = INBASKET_CHAR
    view.VSEP = VSEP
    view.HSEP = HSEP
    view.BUSY = BUSY
    view.CONF = CONF
    view.TASK = TASK
    view.ADAY = ADAY
    view.USED = USED
    view.settings = settings
    view.type_colors = type_colors
    view.cfgfile = cfgfile
    view.model = model
    view.write_back = write_back
    # view.RDict = RDict
    # view.TDBLexer = model.TBDLexer
    view.item = item
    view.item_details = item_details
    view.logger = logger
    view.import_file = import_file
    view.import_examples = import_examples
    view.etmdir = etmdir
    view.inbasket_file = os.path.join(etmdir, 'inbasket.text')
    view.etmhome = etmhome
    view.datetime_calculator = datetime_calculator
    view.about = about
    view.format_time = format_time
    view.format_datetime = format_datetime
    view.format_duration = format_duration
    view.parse_datetime = parse_datetime
    view.ETMDB = ETMDB
    view.DBITEM = DBITEM
    view.DBARCH = DBARCH
    view.etm_version = etm_version

    view.dataview = dataview
    view.completions = completions
    view.expansions = expansions
    view.terminal_style = style
    view.make_examples = make_examples

    view.report = report
    show_query_results = report.show_query_results
    view.show_query_results = show_query_results
    model.show_query_results = show_query_results
    report.ETMDB = ETMDB
    report.DBITEM = DBITEM
    report.DBARCH = DBARCH
    report.ETMQuery = ETMQuery
    report.settings = settings
    report.format_time = format_time
    report.parse_duration = parse_duration
    report.parse_datetime = parse_datetime
    report.format_datetime = format_datetime
    report.format_duration = format_duration
    report.format_hours_and_tenths = format_hours_and_tenths
    report.logger = logger
    report.UT_MIN = UT_MIN

    logger.info(f"setting terminal_style: {style}")


    if len(sys.argv) > 1:
        if sys.argv[1] == 'model':
            logger.info(f"calling model doctest with etmdir: {etmdir}, argv: {sys.argv}")
            import doctest
            doctest.testmod(model)
        elif sys.argv[1] == 'view':
            logger.info(f"calling view doctest with etmdir: {etmdir}, argv: {sys.argv}")
            import doctest
            doctest.testmod(view)
        elif sys.argv[1] == 'data':
            logger.info(f"calling data doctest with etmdir: {etmdir}, argv: {sys.argv}")
            import doctest
            doctest.testmod(data)
        elif sys.argv[1] == 'rep':
            logger.info(f"calling report.main with etmdir: {etmdir}, argv: {sys.argv}")
            report.main(etmdir, sys.argv)
        else:
            logger.info(f"calling model.main with etmdir: {etmdir}, argv: {sys.argv}")
            model.main(etmdir, sys.argv)

    else:
        logger.info(f"system info {model.about()[1]}")
        logger.info(f"calling view.main with etmdir: {etmdir}")
        from etm.view import main
        import asyncio
        asyncio.run(main(etmdir))

def inbasket():
    import sys
    import os
    typechar = '!' # inbasket
    option = '@t etm+'

    help = f"""\
usage: etm+ 'text'          use text
   or: etm+                 get text from stdin
   or: etm+ [?|help]    print this usage information

With the environmental variable ETMHOME set to your etm
root directory, text either piped to this script or
provided as arguments will be appended to 'inbasket.text'
in the ETMHOME directory. When this file exists, etm will
display an ⓘ character at the right end of status bar
alerting you that this file is available for import by
pressing F5.

If the text provided to this script does not begin with an
etm typechar in  -, *, % or !, then the default typechar
'{typechar}' will be used. If the provided string does not
contain any @-key options, then '{option}' will be
appended.

If the inbox typechar '!' is used then after importing,
the reminder will appear as an 'inbox' item requiring your
attention in the list for the current day in agenda view.
This may be especially useful in composing quick notes with
the assurance that you will be reminded to sort them out
later.

If '{T}' is used anywhere in the input, it will be replaced
with a timestamp corresponding to the moment this script was
invoked.
"""

    etmhome = os.environ.get("ETMHOME")
    if not etmhome:
        print("The environmental variable 'ETMHOME' is missing but required.")
        sys.exit()
    elif not os.path.isdir(etmhome):
        print(f"The environmental variable 'ETMHOME={etmhome}' is not a valid directory.")
        sys.exit()

    inbasket = os.path.join(etmhome, 'inbasket.text')


    # use stdin if it's full
    if not sys.stdin.isatty():
        input = sys.stdin.read()

    # otherwise, get the input from
    elif len(sys.argv) > 1:
        if len(sys.argv) == 2:
            input = " ".join(sys.argv[1:])
        else:
            print("The provided input should be wrapped in single quotes")
            sys.exit()
    else:
        print(help)
        sys.exit()

    input = input.strip()
    if input in ["help", "?"]:
        print(help)
        sys.exit()

    # if input does not begins with an itemtype character, prepend typechar .
    input = input if input[0] in "!*-%" else f"{typechar} {input}"
    input = input if '@' in input else f"{input} {option}"
    if '{T}' in input:
        # expand the timestamp
        hsh = {'T': pendulum.now().in_tz('local').format('YYYY-MM-DD HH:mm:ss zz')}
        input = input.format(**hsh)

    with open(inbasket, 'a') as fo:
        fo.write(f"{input}\n")
    print(f"appended:\n   '{input}'\nto {inbasket}")

if __name__ == "__main__":
    main()


