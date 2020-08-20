#! ./env/bin/python
def main():
    import sys
    import logging
    import logging.config
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logger = logging.getLogger()
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

    loglevel = 2 # info
    log_levels = [str(x) for x in range(1, 6)]
    if len(sys.argv) > 1 and sys.argv[1] in log_levels:
        loglevel = int(sys.argv.pop(1))
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        etmdir = sys.argv.pop(1)

    logdir = os.path.normpath(os.path.join(etmdir, 'logs'))
    if not os.path.isdir(logdir):
        os.makedirs(logdir)

    backdir = os.path.normpath(os.path.join(etmdir, 'backups'))
    if not os.path.isdir(backdir):
        os.makedirs(backdir)

    import etm.options as options
    setup_logging = options.setup_logging
    setup_logging(loglevel, logdir)
    options.logger = logger
    settings = options.Settings(etmdir).settings

    logger.info(f"running in a virtual environment: {IS_VENV}")

    secret = settings.get('secret')
    queries = settings.get('queries')
    import pendulum
    today = pendulum.today()
    # We want 2 char 'en' weekday abbreviations regardless of the actual locale
    day = today.end_of('week')  # Sunday
    WA = {i: day.add(days=i).format('ddd')[:2] for i in range(1, 8)}


    import etm.ical as ical
    ical.logger = logger
    import etm.data as data
    data.secret = secret
    from etm.data import Mask
    dbfile = os.path.normpath(os.path.join(etmdir, 'db.json'))
    logger.debug(f"using dbfile: {dbfile}")
    cfgfile = os.path.normpath(os.path.join(etmdir, 'cfg.yaml'))
    ETMDB = data.initialize_tinydb(dbfile)
    DBITEM = ETMDB.table('items', cache_size=None)
    DBARCH = ETMDB.table('archive', cache_size=None)
    logger.debug(f"ETMDB: {ETMDB}")

    from etm.model import about
    from etm.model import import_file
    from etm.model import write_back
    # from etm.model import RDict
    from etm.model import item_details
    from etm.model import FINISHED_CHAR
    from etm.model import UPDATE_CHAR
    from etm.model import PIN_CHAR
    from etm.model import INBASKET_CHAR
    import etm.model as model
    model.etm_version = etm_version
    model.secret = secret
    model.data = data
    model.ical = ical
    model.Mask = Mask
    model.WA = WA
    model.ETMDB = ETMDB
    model.DBITEM = DBITEM
    model.DBARCH = DBARCH
    model.settings = settings
    model.logger = logger
    # model.edit_file = os.path.join(etmdir, 'edit.text')
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

    logger.info(f"initialized TinyDB using {dbfile}")


    import etm.view as view
    view.FINISHED_CHAR = FINISHED_CHAR
    view.UPDATE_CHAR = UPDATE_CHAR
    view.PIN_CHAR = PIN_CHAR
    view.INBASKET_CHAR = INBASKET_CHAR
    view.settings = settings
    view.cfgfile = cfgfile
    view.model = model
    view.write_back = write_back
    # view.RDict = RDict
    # view.TDBLexer = model.TBDLexer
    view.item = item
    view.item_details = item_details
    view.logger = logger
    view.import_file = import_file
    view.etmdir = etmdir
    view.inbasket_file = os.path.join(etmdir, 'inbasket.text')
    view.etmhome = etmhome
    view.datetime_calculator = datetime_calculator
    view.about = about
    view.wrap = model.wrap
    view.format_time = format_time
    view.format_datetime = format_datetime
    view.format_duration = format_duration
    view.parse_datetime = parse_datetime
    view.ETMDB = ETMDB
    view.DBITEM = DBITEM
    view.DBARCH = DBARCH

    view.dataview = dataview
    view.completions = completions
    view.expansions = expansions
    view.terminal_style = style
    from etm.view import ETMQuery

    import etm.report as report
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
    report.UT_MIN = settings.get('usedtime_minutes', 1)

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
later. """

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

    with open(inbasket, 'a') as fo:
        fo.write(f"{input}\n")
    print(f"appended:\n   '{input}'\nto {inbasket}")

if __name__ == "__main__":
    main()


