# -*- coding: utf-8 -*-
import pytest

from .mocks import MockSocket

from pylyskom.connection import ReceiveBuffer
from pylyskom.errors import ReceiveError
from pylyskom.datatypes import Array, String, Int32
from pylyskom.protocol import to_hstring, parse_float, parse_int

def test_to_hstring():
    to_hstring('foobar') == '7Hfoo bar'

def test_to_hstring__encodes_unicode_to_latin1_by_default():
    hs = to_hstring(u'R\xe4ksm\xf6rg\xe5s')
    assert type(hs) == str
    assert hs == u'10HR\xe4ksm\xf6rg\xe5s'.encode('latin1')

def test_to_hstring__encodes_before_calculating_length():
    hs = to_hstring(u'R\xe4ksm\xf6rg\xe5s', encoding='utf8')
    assert type(hs) == str
    assert hs == '13HR\xc3\xa4ksm\xc3\xb6rg\xc3\xa5s'


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
    res = String().parse(buf)
    assert res == "foo bar"

def test_parse_float():
    s = MockSocket("4711.512 ")
    buf = ReceiveBuffer(s)
    res = parse_float(buf)
    assert res == 4711.512

def test_parse_float_raises_if_no_nonfloat_character_at_end():
    s = MockSocket("4711.512")
    buf = ReceiveBuffer(s)
    with pytest.raises(ReceiveError):
        parse_float(buf)

def test_parse_int():
    s = MockSocket("4711 ")
    buf = ReceiveBuffer(s)
    res = parse_int(buf)
    assert res == 4711

def test_parse_int_raises_if_no_noninteger_character_at_end():
    s = MockSocket("4711")
    buf = ReceiveBuffer(s)
    with pytest.raises(ReceiveError):
        parse_int(buf)
