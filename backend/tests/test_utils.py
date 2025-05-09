# tests/test_utils.py

import pytest
from app.services.picklist_service import _clean_flow, _clean_discrete, _clean_part

@pytest.mark.parametrize("inp,expected", [
    (None, "AWAITING_SHIPPING"),
    ("nan", "AWAITING_SHIPPING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
])
def test_clean_flow(inp, expected):
    assert _clean_flow(inp) == expected

@pytest.mark.parametrize("inp,expected", [
    (None, ""),
    ("",     ""),
    ("nan",  ""),
    ("SQU",  ""),
    ("foo",  "foo"),
])
def test_clean_discrete(inp, expected):
    assert _clean_discrete(inp) == expected

@pytest.mark.parametrize("inp,expected", [
    (None,   ""),
    ("",     ""),
    ("abc.", "abc"),
    ("x.y.z","x.y.z"),
])
def test_clean_part(inp, expected):
    assert _clean_part(inp) == expected
