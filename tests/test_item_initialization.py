# tests/test_item.py
from etm.new_model import Item

def test_item_initialization():
    item = Item(input_string="* carpe diem @s 2024/7/10 @r d")
    assert item.itemtype == "*"
    assert item.summary == "carpe diem"
    assert item.start.strftime("%Y/%m/%d") == "2024/07/10"