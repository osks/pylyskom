# -*- coding: utf-8 -*-

from .mocks import MockSocket

from pylyskom.connection import ReceiveBuffer
from pylyskom.datatypes import Array, String, Int32


def test_Array_can_parse_empty_array_with_star_format():
    s = MockSocket(["0 *"])
    buf = ReceiveBuffer(s)
    res = Array(Int32).parse(buf)
    assert res == []

def test_Array_can_parse_empty_array_with_normal_format():
    # This is generally not sent by the server, because empty arrays
    # are sent as "0 *", but I think we should handle it anyway.
    s = MockSocket("0 { }")
    buf = ReceiveBuffer(s)
    res = Array(Int32).parse(buf)
    assert res == []

def test_Array_can_parse_array_non_zero_length_with_star_special_case():
    s = MockSocket("5 *") # length 5 but no array content
    buf = ReceiveBuffer(s)
    res = Array(Int32).parse(buf)
    assert res == []

def test_String_can_parse_hollerith_string():
    s = MockSocket("7Hfoo bar")
    buf = ReceiveBuffer(s)
    res = String.parse(buf)
    assert res == "foo bar"

