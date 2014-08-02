# -*- coding: utf-8 -*-

import pytest
from .mocks import MockSocket

from pylyskom.errors import ReceiveError
from pylyskom.connection import ReceiveBuffer
from pylyskom.datatypes import Array, Bitstring, String, Int32, ConfType, ExtendedConfType


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


def test_Bitstring_constructor():
    bs1 = Bitstring([0], length=1)
    assert len(bs1) == 1
    bs2 = Bitstring([0, 1, 0, 1, 1], length=5)
    assert len(bs2) == 5
    bs4 = Bitstring(length=2)
    assert len(bs4) == 2
    bs5 = Bitstring(None, length=3)
    assert len(bs5) == 3

    with pytest.raises(ValueError):
        Bitstring([1, 0]) # no length
    with pytest.raises(ValueError):
        Bitstring()
    with pytest.raises(ValueError):
        Bitstring(length=0) # invalid length
    with pytest.raises(ValueError):
        Bitstring([], length=0) # invalid length
    with pytest.raises(ValueError):
        Bitstring(None)
    with pytest.raises(ValueError):
        Bitstring([2])
    with pytest.raises(ValueError):
        Bitstring([-1])
    with pytest.raises(ValueError):
        Bitstring([0, 1, 2])


def test_ConfType_length():
    ct = ConfType()
    assert ConfType.LENGTH == 4
    assert len(ct) == ConfType.LENGTH

def test_ConfType_default_constructor():
    ct = ConfType()
    assert ct[0] == 0
    assert ct.rd_prot == 0
    assert ct[1] == 0
    assert ct.original == 0
    assert ct[2] == 0
    assert ct.secret == 0
    assert ct[3] == 0
    assert ct.letterbox == 0

def test_ConfType_to_string():
    ct = ConfType()
    assert ct.to_string() == "0000"

    ct = ConfType([1, 1, 1, 1])
    assert ct.to_string() == "1111"

def test_ExtendedConfType_length():
    ct = ExtendedConfType()
    assert ExtendedConfType.LENGTH == 8
    assert len(ct) == ExtendedConfType.LENGTH

def test_ExtendedConfType_default_constructor():
    ct = ExtendedConfType()
    assert ct.to_string() == "00000000"

def test_ExtendedConfType_rd_prot():
    ct = ExtendedConfType([1, 0, 0, 0, 0, 0, 0, 0])
    assert ct.rd_prot == 1
    assert ct.original == 0
    assert ct.secret == 0
    assert ct.letterbox == 0
    assert ct.allow_anonymous == 0
    assert ct.forbid_secret == 0
    assert ct.reserved2 == 0
    assert ct.reserved3 == 0

def test_ExtendedConfType_original():
    ct = ExtendedConfType([0, 1, 0, 0, 0, 0, 0, 0])
    assert ct.rd_prot == 0
    assert ct.original == 1
    assert ct.secret == 0
    assert ct.letterbox == 0
    assert ct.allow_anonymous == 0
    assert ct.forbid_secret == 0
    assert ct.reserved2 == 0
    assert ct.reserved3 == 0

def test_ExtendedConfType_secret():
    ct = ExtendedConfType([0, 0, 1, 0, 0, 0, 0, 0])
    assert ct.rd_prot == 0
    assert ct.original == 0
    assert ct.secret == 1
    assert ct.letterbox == 0
    assert ct.allow_anonymous == 0
    assert ct.forbid_secret == 0
    assert ct.reserved2 == 0
    assert ct.reserved3 == 0

def test_ExtendedConfType_letterbox():
    ct = ExtendedConfType([0, 0, 0, 1, 0, 0, 0, 0])
    assert ct.rd_prot == 0
    assert ct.original == 0
    assert ct.secret == 0
    assert ct.letterbox == 1
    assert ct.allow_anonymous == 0
    assert ct.forbid_secret == 0
    assert ct.reserved2 == 0
    assert ct.reserved3 == 0

def test_ExtendedConfType_allow_anonymous():
    ct = ExtendedConfType([0, 0, 0, 0, 1, 0, 0, 0])
    assert ct.rd_prot == 0
    assert ct.original == 0
    assert ct.secret == 0
    assert ct.letterbox == 0
    assert ct.allow_anonymous == 1
    assert ct.forbid_secret == 0
    assert ct.reserved2 == 0
    assert ct.reserved3 == 0

def test_ExtendedConfType_forbid_secret():
    ct = ExtendedConfType([0, 0, 0, 0, 0, 1, 0, 0])
    assert ct.rd_prot == 0
    assert ct.original == 0
    assert ct.secret == 0
    assert ct.letterbox == 0
    assert ct.allow_anonymous == 0
    assert ct.forbid_secret == 1
    assert ct.reserved2 == 0
    assert ct.reserved3 == 0

def test_ExtendedConfType_reserved2():
    ct = ExtendedConfType([0, 0, 0, 0, 0, 0, 1, 0])
    assert ct.rd_prot == 0
    assert ct.original == 0
    assert ct.secret == 0
    assert ct.letterbox == 0
    assert ct.allow_anonymous == 0
    assert ct.forbid_secret == 0
    assert ct.reserved2 == 1
    assert ct.reserved3 == 0

def test_ExtendedConfType_reserved3():
    ct = ExtendedConfType([0, 0, 0, 0, 0, 0, 0, 1])
    assert ct.rd_prot == 0
    assert ct.original == 0
    assert ct.secret == 0
    assert ct.letterbox == 0
    assert ct.allow_anonymous == 0
    assert ct.forbid_secret == 0
    assert ct.reserved2 == 0
    assert ct.reserved3 == 1

def test_ExtendedConfType_constructor_can_convert_ConfType():
    ct = ConfType([1, 1, 1, 1])
    ect = ExtendedConfType(ct)
    assert ect.to_string() == "11110000"

def test_ExtendedConfType_to_string():
    ct1 = ExtendedConfType()
    assert ct1.to_string() == "00000000"
    ct2 = ExtendedConfType([1, 0, 1, 0,
                            1, 0, 1, 0])
    assert ct2.to_string() == "10101010"
    ct3 = ExtendedConfType([1, 1, 1, 1,
                            1, 1, 1, 1])
    assert ct3.to_string() == "11111111"

def test_ExtendedConfType_parse():
    with pytest.raises(ReceiveError):
        # Must have an extra character, so this will fail
        ect = ExtendedConfType.parse(ReceiveBuffer(MockSocket("00110011")))
        
    ect = ExtendedConfType.parse(ReceiveBuffer(MockSocket("00110011 ")))
    assert ect.to_string() == "00110011"
