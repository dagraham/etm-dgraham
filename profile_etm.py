#! /usr/bin/env python3
import cProfile
import pstats
import sys
import os
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from etm.__main__ import main

etmhome = os.environ.get('ETMHOME')


bn = 'profile'
ext = 'txt'

fn = f'{bn}.{ext}'
if len(sys.argv) > 1:
    fn = os.path.join(sys.argv[-1], fn)
elif etmhome:
    fn = os.path.join(etmhome, fn)
if os.path.exists(fn):
    timestamp = (
        datetime.now().astimezone(ZoneInfo('UTC')).strftime('%y%m%dT%H%M')
    )
    backup = os.path.join(os.path.split(fn)[0], f'{bn}-{timestamp}.{ext}')
    shutil.copy2(fn, backup)


if os.path.exists(fn):
    os.remove(fn)

# use contexts for profile and stdout
with cProfile.Profile() as profile:
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
