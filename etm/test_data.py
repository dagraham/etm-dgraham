import sys
import os

sys.path.append(os.path.dirname(__file__)) # for pytest

from data import RRuleSerializer
from dateutil.rrule import rrule, rruleset, rrulestr, DAILY

def rulestr_as_set(rulestr):
    return set([x.strip() for x in rulestr.split('\n')])

def test_rrule_serializer():
    rs = RRuleSerializer()
    rulestr = """\
DTSTART:20241028T133000
RRULE:FREQ=DAILY;COUNT=14
RRULE:FREQ=DAILY;INTERVAL=2;COUNT=7
RDATE:20241104T134500
RDATE:20241105T151500
EXDATE:20241104T133000"""
    print(f"{rulestr = }")
    print(f"{rulestr_as_set(rulestr) = }")
    ruleset = rrulestr(rulestr)
    print(f"{ruleset = }")

    ruleset_encoded = rs.encode(ruleset)
    print(f"{rulestr_as_set(ruleset_encoded) = }")
    assert(rulestr_as_set(rulestr) == rulestr_as_set(ruleset_encoded))
    ruleset_decoded = rs.decode(ruleset_encoded)
    print(f"{ruleset_decoded = }")
    assert(ruleset_encoded == rs.encode(ruleset_decoded))


test_rrule_serializer()