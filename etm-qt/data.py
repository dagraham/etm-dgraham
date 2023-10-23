#!/usr/bin/env python3.12
from common import parse, is_aware, add_zone_info, truncate_datetime, truncate_timedelta, print_model 
from datetime import datetime, date, timedelta

from pydantic import BaseModel, ConfigDict, ValidationError, Field,  field_validator
from typing import Optional
from enum import Enum
from icecream import ic

############
# CLASSES
############

class ReminderType(Enum):
    inbox = '!'
    event = '*'
    task = '-'
    journal = '%'


class Reminder(BaseModel):
    model_config = ConfigDict(
            extra='forbid',
            use_enum_values=True,
            validate_assignment = True,
            arbitrary_types_allowed=True
            )

    #####################
    #### attributes #####
    #####################
    itemtype: ReminderType
    summary: str

    # combine start and zone and store aware datetimes as UTC
    zone: Optional[str] = None
    start: datetime | date
    @field_validator('start')
    @classmethod
    def use_zone(cls, value, values):
        # zone will either be None (null) or have the provided zone information
        return add_zone_info(value, values.data['zone'])
    extent: Optional[timedelta] = None

    #####################
    ###### methods ######
    #####################

    def get_end(self):
        if self.extent:
            return (self.start + self.extent).astimezone()
        else:
            return None

    def get_start(self):
        return self.start.astimezone()


print("\nReminder examples:")
w1 = Reminder(
        itemtype = ReminderType.inbox,
        summary = 'now is the time',
        start = datetime.now(),
        extent = truncate_timedelta(
            timedelta(days=2, hours=1, minutes=30, seconds=10, microseconds=737)
            ),
        zone = 'US/Eastern',
        )
print_model(w1)



d = dict(itemtype = ReminderType.event,
    summary = 'for all good men',
    start = parse("fri 3p"),
    extent = truncate_timedelta(
        timedelta(hours=1, minutes=30, seconds=10, microseconds=737)
        ),
    zone = 'US/Mountain',
    )
w2 = Reminder(**d)
print_model(w2)

w_d = w2.model_dump()

w3=Reminder(**w_d)
print_model(w3)

if __name__ == "__main__":
    pass

