# import pendulum
# from pendulum import parse
# from model import timestamp_from_id, fmt_week, setup_logging, serialization, item_details, item_instances, beg_ends, fmt_extent, format_interval, getMonthWeeks, set_summary, TimeIt
from controller import Views

import logging
logger = logging.getLogger()
from model import  setup_logging
from model import TimeIt


if __name__ == '__main__':
    print('\n\n')
    setup_logging(1)
    import doctest
    tt = TimeIt(loglevel=1, label=f"views")
    my_views = Views()
    tt.stop()
    weeks = [(2018, 2), (2018, 11), (2018, 12)]
    for week in weeks:
        head, weekfmt = my_views.get_busy_week(week)
        print(f"  {head}")
        print(weekfmt)
        print(my_views.get_done_week(week))
        print()
        print(my_views.get_agenda_week(week))
        print()
    print('completions:', my_views.completions)

    types = [
            'ev',  # event
            'ib',  # inbox
            'td',  # pastdue (for a task group, only jobs can be past due)
            'by',  # beginby
            'ta',  # available task or job 
            'tw',  # job scheduled and waiting 
            'ac',  # action
            'nt',  # note 
            'so',  # someday
            ]

    type2Num = {key: val for val, key in enumerate(types)}
    num2Type = {key: val for key, val in enumerate(types)}
    print('type2Num:', type2Num)
    print('num2Type:', num2Type)

    doctest.testmod()
