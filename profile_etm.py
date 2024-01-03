#! /usr/bin/env python3
import cProfile
import pstats
import sys
import os
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

from etm.__main__ import main

# from etm.view import main

etmhome = os.environ.get('ETMHOME')

bn = 'profile'
ext = 'txt'

cwd = os.getcwd()
maybe_etmdir = os.path.exists(
    os.path.join(cwd, 'etm.json')
) and os.path.exists(os.path.join(cwd, 'cfg.yaml'))

fn = f'{bn}.{ext}'
if len(sys.argv) > 1 and os.path.isdir(sys.argv[-1]):
    etmdir = sys.argv[-1]
elif maybe_etmdir:
    etmdir = cwd
    sys.argv.append(etmdir)
elif etmhome:
    etmdir = etmhome
else:
    print(
        """Canceled
          An etmhome directory was not provided, 
          the current working directory does not appear to be suitable
          and the environmental variable ETMHOME is not set.
          """
    )
    sys.exit()

fp = os.path.join(etmdir, fn)

if os.path.exists(fp):
    timestamp = (
        datetime.now().astimezone(ZoneInfo('UTC')).strftime('%y%m%dT%H%M')
    )
    backup = os.path.join(os.path.split(fp)[0], f'{bn}-{timestamp}.{ext}')
    shutil.copy2(fp, backup)


if os.path.exists(fn):
    os.remove(fn)

# use contexts for profile and stdout
with cProfile.Profile() as profile:
    print(sys.argv)
    main()

    with open(fn, 'w') as file:
        # Save the original stdout so we can restore it later
        original_stdout = sys.stdout

        # Set stdout to the file object
        sys.stdout = file

        results = pstats.Stats(profile)
        results.sort_stats(pstats.SortKey.TIME)
        results.print_stats('dag', 0.3)

        # results.dump_stats('results.prof')

        # Reset stdout to its original value
        sys.stdout = original_stdout

print(f'\n### pstats saved to {fn} ###')
