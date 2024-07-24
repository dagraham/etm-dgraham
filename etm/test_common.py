import sys
import os
sys.path.append(os.path.dirname(__file__)) # for pytest
from common import wrap, unwrap

def test_wrap():
    test_string = """\
Now is the time for all good men to come to the aid of their country.

   This is indented by 3 spaces. What follows is more of the same. Now is the time for all good men to come to the aid of their country.

This is indented by 0 spaces. What follows is more of the same. Now is the time for all good men to come to the aid of their country.

That's all folks.
"""
    wrapped = wrap(test_string, indent=3, width=60)
    print(f"{wrapped}")

    unwrapped = unwrap(wrapped)
    print(f"{unwrapped}")

    assert(test_string == unwrapped)

test_wrap()