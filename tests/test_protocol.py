# -*- coding: utf-8 -*-
import pytest

from .mocks import MockSocket

from pylyskom.connection import ReceiveBuffer
from pylyskom.errors import ReceiveError
from pylyskom.protocol import to_hstring, read_float, read_int

def test_to_hstring():
    to_hstring(b'foobar') == b'7Hfoo bar'

#def test_to_hstring__encodes_unicode_to_latin1_by_default():
#    hs = to_hstring(u'R\xe4ksm\xf6rg\xe5s')
#    assert type(hs) == str
#    assert hs == u'10HR\xe4ksm\xf6rg\xe5s'.encode('latin1')
#
#def test_to_hstring__encodes_before_calculating_length():
#    hs = to_hstring(u'R\xe4ksm\xf6rg\xe5s', encoding='utf8')
#    assert type(hs) == str
#    assert hs == '13HR\xc3\xa4ksm\xc3\xb6rg\xc3\xa5s'


def test_read_float():
    s = MockSocket(b"4711.512 ")
    buf = ReceiveBuffer(s)
    res = read_float(buf)
    assert res == 4711.512

def test_read_float_raises_if_no_nonfloat_character_at_end():
    s = MockSocket(b"4711.512")
    buf = ReceiveBuffer(s)
    with pytest.raises(ReceiveError):
        read_float(buf)

def test_read_int():
    s = MockSocket(b"4711 ")
    buf = ReceiveBuffer(s)
    res = read_int(buf)
    assert res == 4711

def test_read_int_raises_if_no_noninteger_character_at_end():
    s = MockSocket(b"4711")
    buf = ReceiveBuffer(s)
    with pytest.raises(ReceiveError):
        read_int(buf)
