# -*- coding: utf-8 -*-

import pytest
from .mocks import MockSocket

from pylyskom.errors import ReceiveError
from pylyskom.connection import ReceiveBuffer
from pylyskom.datatypes import ArrayInt32, Int32, String, ConfType, ExtendedConfType


def test_Array_can_parse_empty_array_with_star_format():
    s = MockSocket(["0 *"])
    buf = ReceiveBuffer(s)
    res = ArrayInt32.parse(buf)
    assert res == []

def test_Array_can_parse_empty_array_with_normal_format():
    # This is generally not sent by the server, because empty arrays
    # are sent as "0 *", but I think we should handle it anyway.
    s = MockSocket("0 { }")
    buf = ReceiveBuffer(s)
    res = ArrayInt32.parse(buf)
    assert res == []

def test_Array_can_parse_array_non_zero_length_with_star_special_case():
    s = MockSocket("5 *") # length 5 but no array content
    buf = ReceiveBuffer(s)
    res = ArrayInt32.parse(buf)
    assert res == []

def test_String_can_parse_hollerith_string():
    s = MockSocket("7Hfoo bar")
    buf = ReceiveBuffer(s)
    res = String.parse(buf)
    assert res == "foo bar"


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


def test_ArrayInt32_parse():
    a = ArrayInt32.parse(ReceiveBuffer(MockSocket("3 { 17 4711 0 }")))
    for v in a:
        assert isinstance(v, Int32)
    assert a.to_string() == "3 { 17 4711 0 }"

def test_ArrayInt32_empty_array():
    a = ArrayInt32([])
    assert a.to_string() == "0 { }"

def test_ArrayInt32_constructor_convert_elements():
    a = ArrayInt32([ 17, 4711, 0 ])
    assert a.to_string() == "3 { 17 4711 0 }"

def test_ArrayInt32_setitem_convert_element():
    a = ArrayInt32([0, 0])
    a[0] = 17
    a[1] = 4711
    assert a.to_string() == "2 { 17 4711 }"

def test_ArrayInt32_append_convert_element():
    a = ArrayInt32()
    a.append(17)
    a.append(4711)
    assert a.to_string() == "2 { 17 4711 }"

def test_ArrayInt32_insert_convert_element():
    a = ArrayInt32()
    a.insert(0, 17)
    a.insert(1, 4711)
    assert a.to_string() == "2 { 17 4711 }"

#def test_ArrayInt32_repr():
#    a = ArrayInt32([1, 2, 3])
#    assert repr(a) == "ArrayInt32([1, 2, 3])"

def test_ArrayInt32_add():
    a = ArrayInt32([1, 2, 3])
    b = ArrayInt32([4, 5, 6])
    a = a + b
    assert a.to_string() == "6 { 1 2 3 4 5 6 }"

def test_ArrayInt32_add_convert_element():
    a = ArrayInt32([1, 2, 3])
    b = [4, 5, 6]
    a = a + b
    assert a.to_string() == "6 { 1 2 3 4 5 6 }"

def test_ArrayInt32_extend_convert_element():
    a = ArrayInt32([1, 2, 3])
    b = [4, 5, 6]
    a.extend(b)
    assert a.to_string() == "6 { 1 2 3 4 5 6 }"
