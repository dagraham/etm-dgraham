#! env/bin/python3
import datetime


class View(object):

    def __init__(self):
        pass


class WeekView(View):

    selected_week = "today"

    def __init__(self):
        self.set_week(datetime.date.today())
        pass

    @classmethod
    def set_week(cls, dt=datetime.date.today()):
        cls.selected_week = dt.isocalendar()[:2]
        print(cls.selected_week)


my_view = WeekView()
another_view = WeekView()

my_view.set_week()

print(my_view.selected_week)

another_view.set_week(datetime.date(2018,2,28))

print(another_view.selected_week)

print(my_view.selected_week)
