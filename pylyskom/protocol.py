# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.


WHITESPACE = " \t\r\n"
DIGITS = "01234567890"
FLOAT_CHARS = DIGITS + "eE.-+"

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
    return float("".join(digs))


def array_of_int_to_string(array):
    return "%d { %s }" % (len(array),
                         " ".join(list(map(str, array))))

def array_to_string(array):
    return "%d { %s }" % (len(array), 
                          " ".join([x.to_string() for x in array]))


def to_hstring(s, encoding='latin1'):
    """To hollerith string
    """
    assert isinstance(s, basestring)
    if isinstance(s, unicode):
        s = s.encode(encoding)
    return "%dH%s" % (len(s), s)
