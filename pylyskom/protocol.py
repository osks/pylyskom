# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.


from __future__ import absolute_import
import six

WHITESPACE = bytearray(b" \t\r\n")
DIGITS = bytearray(b"01234567890")
FLOAT_CHARS = DIGITS + bytearray(b"eE.-+")

ORD_0 = ord("0")

MAX_TEXT_SIZE = int(2**31-1)


def read_first_non_ws(buf):
    """Skip whitespace and return first non-ws character"""
    c = buf.receive_char()
    while c in WHITESPACE:
        c = buf.receive_char()
    return c

def read_int_and_next(buf):
    """Get an integer and next character from the receive buffer."""
    c = read_first_non_ws(buf)
    n = 0
    while c in DIGITS:
        n = n * 10 + (ord(c) - ORD_0)
        c = buf.receive_char()
    return (n, c)

def read_int(buf):
    """Get an integer from the receive buffer (discard next character)"""
    (c, n) = read_int_and_next(buf)
    return c

def read_float(buf):
    # Get a float from the receive buffer (discard next character)
    c = read_first_non_ws(buf)
    digs = []
    while c in FLOAT_CHARS:
        digs.append(c)
        c = buf.receive_char()
    return float(b"".join(digs))


def to_hstring(s):
    """To hollerith byte string
    """
    assert isinstance(s, six.binary_type)
    return b"%dH%s" % (len(s), s)
