import logging
import sys
import os
from etmMVC import view
from etmMVC import model

if __name__ == "__main__":
    loglevel = '3'
    log_levels = [str(x) for x in range(1, 6)]

    if len(sys.argv) > 1 and sys.argv[1] in log_levels:
        loglevel = sys.argv.pop(1)

    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        etmdir = sys.argv.pop(1)
    else:
        etmdir = None

    logger = logging.getLogger()
    model.setup_logging(loglevel, etmdir=etmdir)
    logger.debug("logging at level {0} and starting urwid loop in dir {1}".format(loglevel, etmdir))

    view.Menu(etmdir).loop.run()

