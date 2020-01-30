#! ./env/bin/python
def main():
    import sys
    import logging
    import logging.config
    logger = logging.getLogger()
    MIN_PYTHON = (3, 6)
    if sys.version_info < MIN_PYTHON:
        sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)
    import os
    IS_VENV = os.getenv('VIRTUAL_ENV') is not None

    import etm.__version__ as version
    etm_version = version.version
    etmdir = os.getcwd()

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
    import pendulum
    locale = settings.get('locale', None)
    if locale:
        pendulum.set_locale(locale)
    today = pendulum.today()
    day = today.end_of('week')  # Sunday
    WA = {i: day.add(days=i).format('ddd')[:2] for i in range(1, 8)}


    import etm.ical as ical
    import etm.data as data
    data.secret = secret
    from etm.data import Mask
    dbfile = os.path.normpath(os.path.join(etmdir, 'db.json'))
    cfgfile = os.path.normpath(os.path.join(etmdir, 'cfg.yaml'))
    ETMDB = data.initialize_tinydb(dbfile)
    DBITEM = ETMDB.table('items', cache_size=None)
    DBARCH = ETMDB.table('archive', cache_size=None)

    from etm.model import about
    from etm.model import import_file
    from etm.model import RDict
    from etm.model import item_details
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
    userhome = os.path.expanduser('~')
    model.etmhome = os.path.join('~', os.path.relpath(etmdir, userhome)) if etmdir.startswith(userhome) else etmdir 
    # we put settings into the model namespace so model.Dataview will have it
    dataview = model.DataView(etmdir)
    datetime_calculator = model.datetime_calculator
    item = model.Item()
    format_time = model.format_time
    format_datetime = model.format_datetime
    format_duration = model.format_duration
    # since dataview calls schedule it will also have settings
    completions = dataview.completions
    expansions = settings["expansions"]
    if expansions:
        for x in expansions:
            completions.append(f"@x {x}")
    style = dataview.settings["style"]
    parse_datetime = model.parse_datetime

    logger.info(f"initialized TinyDB using {dbfile}")


    import etm.view as view
    view.cfgfile = cfgfile
    view.model = model
    view.RDict = RDict
    # view.TDBLexer = model.TBDLexer
    view.item = item
    view.item_details = item_details
    view.logger = logger
    view.import_file = import_file
    view.etmdir = etmdir
    view.datetime_calculator = datetime_calculator
    view.about = about
    view.wrap = model.wrap
    view.settings = settings
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
        else:
            logger.info(f"calling data.main with etmdir: {etmdir}, argv: {sys.argv}")
            model.main(etmdir, sys.argv)

    else:
        logger.info(f"system info {model.about()[1]}")
        logger.info(f"calling view.main with etmdir: {etmdir}")
        from etm.view import main
        # sys.stderr.write = logger.error
        # sys.stdout.write = logger.debug
        import asyncio
        asyncio.run(main(etmdir))

if __name__ == "__main__":
    main()


