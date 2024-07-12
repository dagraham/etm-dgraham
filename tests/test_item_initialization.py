# tests/test_item.py
from etm.new_model import Item

json_entry = {
    "created": "{T}:20240712T1052",
    "itemtype": "*",
    "summary": "Thanksgiving",
    "s": "{T}:20101126T0500",
    "r": [
        {
            "r": "y",
            "M": [11],
            "w": ["{W}:4TH"]
        }
    ],
    "modified": "{T}:20240712T1054"
}

def test_item_initialization():
    item = Item(input_string="* carpe diem @s 2024/7/10 @r d")
    assert item.itemtype == "*"
    assert item.summary == "carpe diem"
    assert item.start.strftime("%Y/%m/%d") == "2024/07/10"

    item_from_json = Item(json_dict=json_entry)
    item_from_string = Item(input_string="* Thanksgiving @s 2010/11/26 @r y &M 11 &w 4TH")
    assert item_from_json.summary == item_from_string.summary