#! /usr/bin/env python3
import calendar
import locale
import pendulum
from options import Settings
settings = Settings()
lcl = settings.locale

def sixmonthcal(advance=0):
    """
    Advance = 0 shows the half year containing the current month. Advance 
    = n shows the half year containing the month that is 6 x n months in the
    future if n > 0 or the past if n < 0.  
    """
    today = pendulum.today()
    c = calendar.LocaleTextCalendar(0)
    cal = []
    # make advance = 0 show the half year containing the current month
    y = today.year
    adv = advance if advance else today.month // 7
    m = 1
    m += 6 * adv
    y += m // 12
    m = m % 12
    for i in range(6): # months in the half year
        cal.append(c.formatmonth(y, m+i, w=2).split('\n'))
    ret = []
    for r in range(0, 6, 2):  # 6 months in columns of 2 months
        l = max(len(cal[r]), len(cal[r + 1]))
        for i in range(2):
            if len(cal[r + i]) < l:
                for j in range(len(cal[r + i]), l + 1):
                    cal[r + i].append('')
        for j in range(l):  # rows from each of the 2 months
            ret.append((u'  %-20s    %-20s  ' % (cal[r][j], cal[r + 1][j])))
    return "\n".join(ret)

if __name__ == "__main__":
    import sys
    if sys.argv and len(sys.argv) > 1:
        adv = int(sys.argv[1])
    else:
        adv = 0
    print(sixmonthcal(adv))