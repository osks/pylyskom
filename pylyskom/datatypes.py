# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

import time
import calendar
from typing import Optional

from .protocol import (
    to_hstring,
    read_first_non_ws,
    read_int_and_next,
    read_int,
    read_float)

from .errors import (
    ProtocolError)
from six.moves import filter
import six
from six.moves import range


# Constants for Misc-Info (needed in requests below)

MI_RECPT=0
MI_CC_RECPT=1
MI_COMM_TO=2
MI_COMM_IN=3
MI_FOOTN_TO=4
MI_FOOTN_IN=5
MI_LOC_NO=6
MI_REC_TIME=7
MI_SENT_BY=8
MI_SENT_AT=9
MI_BCC_RECPT=15

MIR_TO = MI_RECPT
MIR_CC = MI_CC_RECPT
MIR_BCC = MI_BCC_RECPT

MIC_COMMENT = MI_COMM_TO
MIC_FOOTNOTE = MI_FOOTN_TO


# TODO: Rename the to_string() to something better. Its purpose is to
# return the serialized data.

class EmptyResponse(object):
    @classmethod
    def parse(cls, buf):
        return None

class String(bytes):
    def __new__(cls, s=None):
        """
        @param s Encoded string (not unicode)
        """
        if isinstance(s, six.text_type):
            # For convenience. Latin-1 is the default-encoding in
            # LysKOM
            try:
                s = s.encode('latin-1')
            except UnicodeEncodeError:
                raise ValueError("Failed to encode {!r} to latin-1".format(s))

        if s is None:
            return bytes.__new__(cls)
        else:
            return bytes.__new__(cls, s)

    @classmethod
    def parse(cls, buf):
        # Parse a string (Hollerith notation)
        (length, h) = read_int_and_next(buf)
        if h != b"H":
            raise ProtocolError()
        return cls(buf.receive_string(length))

    def to_string(self):
        if isinstance(self, six.text_type):
            raise ValueError("Un-encoded string: {!r}".format(self))
        return b"%dH%s" % (len(self), self)

class Float(float):
    @classmethod
    def parse(cls, buf):
        return read_float(buf)

    def to_string(self):
        raise NotImplementedError()

class Int(int):
    @classmethod
    def parse(cls, buf):
        return read_int(buf)

    def to_string(self):
        return b"%d" % (self,)

class Bool(Int):
    # todo: inherit from bool instead of int
    pass

class Int8(Int):
    pass

class Int16(Int):
    pass

class Int32(Int):
    pass

class AuxNo(Int32):
    pass

class ConfNo(Int16):
    pass

class PersNo(ConfNo):
    pass

class TextNo(Int32):
    pass

class LocalTextNo(Int32):
    pass

class SessionNo(Int32):
    pass

class GarbNice(Int32):
    pass

class InfoType(Int32):
    # TODO: Should only allow values of MiscInfo.
    # http://www.lysator.liu.se/lyskom/protocol/11.1/protocol-a.html#Info-Type
    pass


class Array(list):
    """Sub-class this to use it.
    """
    ELEMENT_CLASS: Optional[object] = None # Must be set in subclass

    def __init__(self, iterable=None):
        if self.ELEMENT_CLASS is None:
            raise ValueError("No element class specified")
        if iterable is None:
            list.__init__(self)
        else:
            iterable = [ self.ELEMENT_CLASS(v) for v in iterable ]
            list.__init__(self, iterable)

    def __setitem__(self, i, y):
        if not isinstance(y, self.ELEMENT_CLASS):
            y = self.ELEMENT_CLASS(y)
        return list.__setitem__(self, i, y)

    def append(self, x):
        if not isinstance(x, self.ELEMENT_CLASS):
            x = self.ELEMENT_CLASS(x)
        return list.append(self, x)

    def insert(self, i, x):
        if not isinstance(x, self.ELEMENT_CLASS):
            x = self.ELEMENT_CLASS(x)
        return list.insert(self, i, x)

    def extend(self, l):
        return list.extend(self, self.__class__(l))

    def __add__(self, other):
        return self.__class__(list.__add__(self, other))

    #def __repr__(self):
    #    return "{:s}({:s})".format(
    #        self.__class__.__name__,
    #        list.__repr__(self))

    @classmethod
    def parse(cls, buf):
        length = read_int(buf)
        obj = cls()
        left = read_first_non_ws(buf)
        if left == b"*":
            # Empty or special case of unwanted data
            return obj
        elif left != b"{":
            raise ProtocolError()
        for i in range(0, length):
            el = cls.ELEMENT_CLASS.parse(buf)
            obj.append(el)
        right = read_first_non_ws(buf)
        if right != b"}":
            raise ProtocolError()
        return obj

    def to_string(self):
        self._validate_array()
        if len(self) > 0:
            return b"%d { %s }" % (len(self), b" ".join([x.to_string() for x in self]))
        else:
            return b"0 { }"

    def _validate_array(self):
        for v in self:
            if not isinstance(v, self.ELEMENT_CLASS):
                raise ValueError("Array of {!r} contains invalid element ({!r})".format(
                        self.ELEMENT_CLASS, v))


class ArrayInt32(Array):
    ELEMENT_CLASS = Int32

class ArrayLocalTextNo(Array):
    ELEMENT_CLASS = LocalTextNo

class ArrayTextNo(Array):
    ELEMENT_CLASS = TextNo

class ArrayString(Array):
    ELEMENT_CLASS = String

class Bitstring(list):
    """Some type of base class. Not meant to be used directly as datatype.
    """
    LENGTH: Optional[int] = None # Must be set in subclass

    def __init__(self, iterable=None):
        length = self.LENGTH
        if length is None:
            raise ValueError("No length specified")
        if length < 1:
            raise ValueError("Cannot be empty")
        if iterable is None:
            iterable = [0]*length
        if len(iterable) != length:
            raise ValueError("Wrong length, expected {:d}".format(length))
        list.__init__(self, iterable)
        self._validate_bitstring()

    @classmethod
    def parse(cls, buf):
        obj = cls()
        length = cls.LENGTH
        char = read_first_non_ws(buf)
        for i in range(0, length):
            if char == b"0":
                obj[i] = 0
            elif char == b"1":
                obj[i] = 1
            else:
                raise ProtocolError()
            char = buf.receive_char()
        return obj

    def to_string(self):
        self._validate_bitstring()
        return (b"%d"*self.LENGTH) % tuple(self)

    def _validate_bitstring(self):
        assert len(self) == self.LENGTH
        for v in self:
            if v not in (0, 1):
                raise ValueError("Bitstring values can only be 0 or 1 (got {!r})".format(v))
        

class Bitstring4(Bitstring):
    LENGTH = 4

class Bitstring8(Bitstring):
    LENGTH = 8

class Bitstring16(Bitstring):
    LENGTH = 16

def _create_bitstring_accessors(index):
    """For creating named properties for certain list indicies.

    Usage: original = property(*_create_bitstring_accessors(0))
    
    """
    assert index >= 0
    def _create_get(index):
        def get_wrapper(self):
            return self.__getitem__(index)
        return get_wrapper
    def _create_set(index):
        def set_wrapper(self, value):
            return self.__setitem__(index, value)
        return set_wrapper

    return (_create_get(index), _create_set(index))



# TIME

class Time(object):
    """Assumes all dates are in UTC timezone.
    """
    def __init__(self, seconds=0, minutes=0, hours=0, day=0, month=0, year=0,
                 day_of_week=0, day_of_year=0, is_dst=0, ptime=None):
        if ptime is None:
            self.seconds = seconds
            self.minutes = minutes
            self.hours = hours
            self.day = day
            self.month = month # 0 .. 11 
            self.year = year # no of years since 1900
            self.day_of_week = day_of_week # 0 = Sunday ... 6 = Saturday
            self.day_of_year = day_of_year # 0 ... 365
            self.is_dst = is_dst
        else:
            (dy,dm,dd,th,tm,ts, wd, yd, dt) = time.gmtime(ptime)
            self.seconds = ts
            self.minutes = tm
            self.hours = th
            self.day = dd
            self.month = dm -1 
            self.year = dy - 1900 
            self.day_of_week = (wd + 1) % 7
            self.day_of_year = yd - 1
            self.is_dst = dt

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.seconds = Int32.parse(buf)
        obj.minutes = Int32.parse(buf)
        obj.hours = Int32.parse(buf)
        obj.day = Int32.parse(buf)
        obj.month = Int32.parse(buf)
        obj.year = Int32.parse(buf)
        obj.day_of_week = Int32.parse(buf)
        obj.day_of_year = Int32.parse(buf)
        obj.is_dst = Bool.parse(buf)
        return obj

    def __repr__(self):
        return ("Time(seconds={sec!r}, minutes={min!r}, hours={hours!r}, day={day!r}, "
                "month={month!r}, year={year!r}, day_of_week={dow!r}, day_of_year={doy!r}, "
                "is_dst={dst!r})".format(
                sec=self.seconds,
                min=self.minutes,
                hours=self.hours,
                day=self.day,
                month=self.month,
                year=self.year,
                dow=self.day_of_week,
                doy=self.day_of_year,
                dst=self.is_dst))

    def to_string(self):
        return b"%d %d %d %d %d %d %d %d %d" % (
            self.seconds,
            self.minutes,
            self.hours,
            self.day,
            self.month,
            self.year,
            self.day_of_week, # ignored by server
            self.day_of_year, # ignored by server
            self.is_dst)

    def to_python_time(self):
        return calendar.timegm((self.year + 1900,
                                self.month + 1,
                                self.day,
                                self.hours,
                                self.minutes,
                                self.seconds,
                                (self.day_of_week - 1) % 7,
                                self.day_of_year + 1,
                                self.is_dst))

    def to_date_and_time(self):
        return "%04d-%02d-%02d %02d:%02d:%02d" % \
            (self.year + 1900, self.month + 1, self.day,
             self.hours, self.minutes, self.seconds)

    def to_iso_8601(self):
        """Example: 1994-11-05T13:15:30Z"""
        return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (
            self.year + 1900, self.month + 1, self.day,
            self.hours, self.minutes, self.seconds)

    def __str__(self):
        return "<Time %s, dst=%d>" % (self.to_date_and_time(), self.is_dst)

    def __eq__(self, other):
        return (self.seconds == other.seconds and
                self.minutes == other.minutes and
                self.hours == other.hours and
                self.day == other.day and
                self.month == other.month and
                self.year == other.year and
                self.day_of_week == other.day_of_week and
                self.day_of_year == other.day_of_year and
                self.is_dst == other.is_dst)

    def __ne__(self, other):
        return not self == other


# RESULT FROM LOOKUP-Z-NAME

class ConfZInfo(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.name = String.parse(buf)
        obj.type = ConfType.parse(buf)
        obj.conf_no = ConfNo.parse(buf)
        return obj

    def __str__(self):
        return "<ConfZInfo %d: %s>" % \
            (self.conf_no, self.name)

    def __eq__(self, other):
        return (self.name == other.name and
                self.type == other.type and
                self.conf_no == other.conf_no)

    def __ne__(self, other):
        return not self == other

# RAW MISC-INFO (AS IT IS IN PROTOCOL A)

class RawMiscInfo(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.type = Int32.parse(buf)
        if obj.type in [MI_REC_TIME, MI_SENT_AT]:
            obj.data = Time.parse(buf)
        else:
            obj.data = Int32.parse(buf)
        return obj

    def __str__(self):
        return "<MiscInfo %d: %s>" % (self.type, self.data)

    def __eq__(self, other):
        return (self.type == other.type and
                self.data == other.data)

    def __ne__(self, other):
        return not self == other

class ArrayRawMiscInfo(Array):
    ELEMENT_CLASS = RawMiscInfo


class MIRecipient(object):
    def __init__(self, type=MIR_TO, recpt=0):
        self.type = type # MIR_TO, MIR_CC or MIR_BCC
        self.recpt = recpt   # Always present
        self.loc_no = None   # Always present
        self.rec_time = None # Will be None if not sent by server
        self.sent_by = None  # Will be None if not sent by server
        self.sent_at = None  # Will be None if not sent by server

    def decode_additional(self, raw, i):
        while i < len(raw):
            if raw[i].type == MI_LOC_NO:
                self.loc_no = raw[i].data
            elif raw[i].type == MI_REC_TIME:
                self.rec_time = raw[i].data
            elif raw[i].type == MI_SENT_BY:
                self.sent_by = raw[i].data
            elif raw[i].type == MI_SENT_AT:
                self.sent_at = raw[i].data
            else:
                return i 
            i = i + 1
        return i

    def get_tuples(self):
        return [(self.type, self.recpt)]

    def __eq__(self, other):
        return (self.type == other.type and
                self.recpt == other.recpt and
                self.loc_no == other.loc_no and
                self.rec_time == other.rec_time and
                self.sent_by == other.send_by and
                self.sent_at == other.send_at)

    def __ne__(self, other):
        return not self == other

class MICommentTo(object):
    def __init__(self, type = MIC_COMMENT, text_no = 0):
        self.type = type
        self.text_no = text_no
        self.sent_by = None
        self.sent_at = None
        
    def decode_additional(self, raw, i):
        while i < len(raw):
            if raw[i].type == MI_SENT_BY:
                self.sent_by = raw[i].data
            elif raw[i].type == MI_SENT_AT:
                self.sent_at = raw[i].data
            else:
                return i 
            i = i + 1
        return i

    def get_tuples(self):
        return [(self.type, self.text_no)]

    def __eq__(self, other):
        return (self.type == other.type and
                self.text_no == other.text_no and
                self.sent_by == other.send_by and
                self.sent_at == other.send_at)

    def __ne__(self, other):
        return not self == other

class MICommentIn(object):
    def __init__(self, type = MIC_COMMENT, text_no = 0):
        self.type = type
        self.text_no = text_no

    def get_tuples(self):
        # Cannot send these to sever
        return []

    def __eq__(self, other):
        return (self.type == other.type and
                self.text_no == other.text_no)

    def __ne__(self, other):
        return not self == other

# COOKED MISC-INFO (MORE TASTY)
# N.B: This class represents the whole array, not just one item
class CookedMiscInfo(object):
    def __init__(self, other=None):
        if other is None:
            self.recipient_list = []
            self.comment_to_list = []
            self.comment_in_list = []
        else:
            self.recipient_list = other.recipient_list
            self.comment_to_list = other.comment_to_list
            self.comment_in_list = other.comment_in_list

    @classmethod
    def parse(cls, buf):
        obj = cls()
        raw = ArrayRawMiscInfo.parse(buf)
        i = 0
        while i < len(raw):
            if raw[i].type in [MI_RECPT, MI_CC_RECPT, MI_BCC_RECPT]:
                r = MIRecipient(raw[i].type, raw[i].data)
                i = r.decode_additional(raw, i+1)
                obj.recipient_list.append(r)
            elif raw[i].type in [MI_COMM_TO, MI_FOOTN_TO]:
                ct = MICommentTo(raw[i].type, raw[i].data)
                i = ct.decode_additional(raw, i+1)
                obj.comment_to_list.append(ct)
            elif raw[i].type in [MI_COMM_IN, MI_FOOTN_IN]:
                ci = MICommentIn(raw[i].type - 1 , raw[i].data  ) # KLUDGE :-)
                i = i + 1
                obj.comment_in_list.append(ci)
            else:
                raise ProtocolError
        return obj

    def to_string(self):
        l = []
        for r in self.comment_to_list + \
            self.recipient_list + \
            self.comment_in_list:
            l = l + r.get_tuples()
        return b"%d { %s}" % (len(l),
                              b"".join([b"%d %d " % \
                                            (x[0], x[1]) for x in l]))


    def __eq__(self, other):
        return (self.recipient_list == other.recipient_list and
                self.comment_to_list == other.comment_to_list and
                self.comment_in_list == other.comment_in_list)

    def __ne__(self, other):
        return not self == other

# AUX INFO

class AuxItemFlags(Bitstring8):
    deleted = property(*_create_bitstring_accessors(0))
    inherit = property(*_create_bitstring_accessors(1))
    secret = property(*_create_bitstring_accessors(2))
    hide_creator = property(*_create_bitstring_accessors(3))
    dont_garb = property(*_create_bitstring_accessors(4))
    reserved2 = property(*_create_bitstring_accessors(5))
    reserved3 = property(*_create_bitstring_accessors(6))
    reserved4 = property(*_create_bitstring_accessors(7))
        

class AuxItem(object): 
    def __init__(self, aux_item=None):
        if aux_item is not None:
            self.aux_no = aux_item.aux_no
            self.tag = aux_item.tag
            self.creator = aux_item.creator
            self.created_at = aux_item.created_at
            self.flags = aux_item.flags
            self.inherit_limit = aux_item.inherit_limit
            self.data = aux_item.data
        else:
            self.aux_no = 0
            self.tag = 0
            self.creator = 0
            self.created_at = Time()
            self.flags = AuxItemFlags()
            self.inherit_limit = 0
            self.data = ""

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.aux_no = AuxNo.parse(buf)
        obj.tag = Int32.parse(buf)
        obj.creator = PersNo.parse(buf)
        obj.created_at = Time.parse(buf)
        obj.flags = AuxItemFlags.parse(buf)
        obj.inherit_limit = Int32.parse(buf)
        obj.data = String.parse(buf)
        return obj

    def __str__(self):
        return "<AuxItem %d>" % self.tag

    def __eq__(self, other):
        return (self.aux_no == other.aux_no and
                self.tag == other.tag and
                self.creator == other.creator and
                self.created_at == other.created_at and
                self.flags == other.flags and
                self.inherit_limit == other.inherit_limit and
                self.data == other.data)

    def __ne__(self, other):
        return not self == other


class AuxItemInput(object): 
    def __init__(self, aux_item=None, tag=0, flags=None, inherit_limit=0, data=None):
        if aux_item is not None:
            self.tag = aux_item.tag
            self.flags = aux_item.flags
            self.inherit_limit = aux_item.inherit_limit
            self.data = aux_item.data
        else:
            if flags is None:
                flags = AuxItemFlags()
            if data is None:
                data = ""
            self.tag = tag
            self.flags = flags
            self.inherit_limit = inherit_limit
            self.data = data

    def __str__(self):
        return "<AuxItemInput %d>" % self.tag

    def to_string(self):
        return b"%d %s %d %s" % \
            (self.tag,
             self.flags.to_string(),
             self.inherit_limit,
             to_hstring(self.data))

    def __eq__(self, other):
        return (self.tag == other.tag and
                self.flags == other.flags and
                self.inherit_limit == other.inherit_limit and
                self.data == other.data)

    def __ne__(self, other):
        return not self == other

class ArrayAuxItem(Array):
    ELEMENT_CLASS = AuxItem

class ArrayAuxItemInput(Array):
    ELEMENT_CLASS = AuxItemInput


# Functions operating on lists of AuxItems

def all_aux_items_with_tag(ail, tag):
    return list(filter(lambda x, tag=tag: x.tag == tag, ail))
     
def first_aux_items_with_tag(ail, tag):
    all = all_aux_items_with_tag(ail, tag)
    if len(all) == 0:
        return None
    else:
        return all[0]
     
# TEXT

class TextStat(object):
    def __init__(self, creation_time=None, author=0, no_of_lines=0, no_of_chars=0,
                 no_of_marks=0, misc_info=None, aux_items=None):
        self.creation_time = creation_time
        self.author = author
        self.no_of_lines = no_of_lines
        self.no_of_chars = no_of_chars
        self.no_of_marks = no_of_marks
        if misc_info is None:
            misc_info = CookedMiscInfo()
        self.misc_info = misc_info
        if aux_items is None:
            aux_items = []
        self.aux_items = aux_items

    @classmethod
    def parse(cls, buf, old_format=0):
        obj = cls()
        obj.creation_time = Time.parse(buf)
        obj.author = PersNo.parse(buf)
        obj.no_of_lines = Int32.parse(buf)
        obj.no_of_chars = Int32.parse(buf)
        obj.no_of_marks = Int16.parse(buf)
        obj.misc_info = CookedMiscInfo.parse(buf)
        if old_format:
            obj.aux_items = []
        else:
            obj.aux_items = ArrayAuxItem.parse(buf)
        return obj

    def __eq__(self, other):
        return (self.creation_time == other.creation_time and
                self.author == other.author and
                self.no_of_lines == other.no_of_lines and
                self.no_of_chars == other.no_of_chars and
                self.no_of_marks == other.no_of_marks and
                self.misc_info == other.misc_info and
                self.aux_items == other.aux_items)

    def __ne__(self, other):
        return not self == other


# CONFERENCE

class ConfType(Bitstring4):
    rd_prot = property(*_create_bitstring_accessors(0))
    original = property(*_create_bitstring_accessors(1))
    secret = property(*_create_bitstring_accessors(2))
    letterbox = property(*_create_bitstring_accessors(3))

class ExtendedConfType(Bitstring8):
    def __init__(self, conf_type=None):
        if isinstance(conf_type, ConfType):
            conf_type = conf_type + [0]*(ExtendedConfType.LENGTH - ConfType.LENGTH)
        Bitstring8.__init__(self, conf_type)
    rd_prot = property(*_create_bitstring_accessors(0))
    original = property(*_create_bitstring_accessors(1))
    secret = property(*_create_bitstring_accessors(2))
    letterbox = property(*_create_bitstring_accessors(3))
    allow_anonymous = property(*_create_bitstring_accessors(4))
    forbid_secret = property(*_create_bitstring_accessors(5))
    reserved2 = property(*_create_bitstring_accessors(6))
    reserved3 = property(*_create_bitstring_accessors(7))

class AnyConfType(ExtendedConfType):
    """Alias for ExtendedConfType.
    """
    pass



class Conference(object):
    def __init__(self, name=None, conf_type=None, creation_time=None,
                 last_written=None, creator=0, presentation=0, supervisor=0,
                 permitted_submitters=0, super_conf=0, msg_of_day=0, nice=0,
                 keep_commented=0, no_of_members=0, first_local_no=0,
                 no_of_texts=0, expire=0, aux_items=None):
        if name is None:
            name = ""
        if conf_type is None:
            conf_type = ExtendedConfType()
        if creation_time is None:
            creation_time = Time()
        if last_written is None:
            last_written = Time()
        if aux_items is None:
            aux_items = []

        self.name = name
        self.type = conf_type
        self.creation_time = creation_time
        self.last_written = last_written
        self.creator = creator
        self.presentation = presentation
        self.supervisor = supervisor
        self.permitted_submitters = permitted_submitters
        self.super_conf = super_conf
        self.msg_of_day = msg_of_day
        self.keep_commented = keep_commented
        self.nice = nice
        self.no_of_members = no_of_members
        self.first_local_no = first_local_no
        self.no_of_texts = no_of_texts
        self.expire = expire
        self.aux_items = aux_items

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.name = String.parse(buf)
        obj.type = ExtendedConfType.parse(buf)
        obj.creation_time = Time.parse(buf)
        obj.last_written = Time.parse(buf)
        obj.creator = PersNo.parse(buf)
        obj.presentation = TextNo.parse(buf)
        obj.supervisor = ConfNo.parse(buf)
        obj.permitted_submitters = ConfNo.parse(buf)
        obj.super_conf = ConfNo.parse(buf)
        obj.msg_of_day = TextNo.parse(buf)
        obj.nice = GarbNice.parse(buf)
        obj.keep_commented = GarbNice.parse(buf)
        obj.no_of_members = Int16.parse(buf)
        obj.first_local_no = LocalTextNo.parse(buf)
        obj.no_of_texts = Int32.parse(buf)
        obj.expire = GarbNice.parse(buf)
        obj.aux_items = ArrayAuxItem.parse(buf)
        return obj

    def __str__(self):
        return "<Conference %s>" % self.name

class UConference(object):
    def __init__(self, name=None, conf_type=None, highest_local_no=0, nice=0):
        if name is None:
            name = ""
        if conf_type is None:
            conf_type = ExtendedConfType()

        self.name = name
        self.type = conf_type
        self.highest_local_no = highest_local_no
        self.nice = nice

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.name = String.parse(buf)
        obj.type = ExtendedConfType.parse(buf)
        obj.highest_local_no = LocalTextNo.parse(buf)
        obj.nice = GarbNice.parse(buf)
        return obj

    def __eq__(self, other):
        return (self.name == other.name and
                self.type == other.type and
                self.highest_local_no == other.highest_local_no and
                self.nice == other.nice)

    def __repr__(self):
        return ("UConference(name={name!r}, conf_type={type!r}, "
                "highest_local_no={hln!r}, nice={nice!r})".format(
                name=self.name,
                type=self.type,
                hln=self.highest_local_no,
                nice=self.nice))

    def __str__(self):
        return "<UConference %s>" % self.name
    
# PERSON

class PrivBits(Bitstring16):
    wheel = property(*_create_bitstring_accessors(0))
    admin = property(*_create_bitstring_accessors(1))
    statistic = property(*_create_bitstring_accessors(2))
    create_pers = property(*_create_bitstring_accessors(3))
    create_conf = property(*_create_bitstring_accessors(4))
    change_name = property(*_create_bitstring_accessors(5))
    flg7 = property(*_create_bitstring_accessors(6))
    flg8 = property(*_create_bitstring_accessors(7))
    flg9 = property(*_create_bitstring_accessors(8))
    flg10 = property(*_create_bitstring_accessors(9))
    flg11 = property(*_create_bitstring_accessors(10))
    flg12 = property(*_create_bitstring_accessors(11))
    flg13 = property(*_create_bitstring_accessors(12))
    flg14 = property(*_create_bitstring_accessors(13))
    flg15 = property(*_create_bitstring_accessors(14))
    flg16 = property(*_create_bitstring_accessors(15))
    
class PersonalFlags(Bitstring8):
    unread_is_secret = property(*_create_bitstring_accessors(0))
    flg2 = property(*_create_bitstring_accessors(1))
    flg3 = property(*_create_bitstring_accessors(2))
    flg4 = property(*_create_bitstring_accessors(3))
    flg5 = property(*_create_bitstring_accessors(4))
    flg6 = property(*_create_bitstring_accessors(5))
    flg7 = property(*_create_bitstring_accessors(6))
    flg8 = property(*_create_bitstring_accessors(7))

class Person(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.username = String.parse(buf)
        obj.privileges = PrivBits.parse(buf)
        obj.flags = PersonalFlags.parse(buf)
        obj.last_login = Time.parse(buf)
        obj.user_area = TextNo.parse(buf)
        obj.total_time_present = Int32.parse(buf)
        obj.sessions = Int32.parse(buf)
        obj.created_lines = Int32.parse(buf)
        obj.created_bytes = Int32.parse(buf)
        obj.read_texts = Int32.parse(buf)
        obj.no_of_text_fetches = Int32.parse(buf)
        obj.created_persons = Int16.parse(buf)
        obj.created_confs = Int16.parse(buf)
        obj.first_created_local_no = Int32.parse(buf)
        obj.no_of_created_texts = Int32.parse(buf)
        obj.no_of_marks = Int16.parse(buf)
        obj.no_of_confs = Int16.parse(buf)
        return obj

# MEMBERSHIP

class MembershipType(Bitstring):
    LENGTH = 8
    invitation = property(*_create_bitstring_accessors(0))
    passive = property(*_create_bitstring_accessors(1))
    secret = property(*_create_bitstring_accessors(2))
    passive_message_invert = property(*_create_bitstring_accessors(3))
    reserved2 = property(*_create_bitstring_accessors(4))
    reserved3 = property(*_create_bitstring_accessors(5))
    reserved4 = property(*_create_bitstring_accessors(6))
    reserved5 = property(*_create_bitstring_accessors(7))

class Membership10(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.position = Int32.parse(buf)
        obj.last_time_read  = Time.parse(buf)
        obj.conference = ConfNo.parse(buf)
        obj.priority = Int8.parse(buf)
        obj.last_text_read = LocalTextNo.parse(buf)
        obj.read_texts = ArrayLocalTextNo.parse(buf)
        obj.added_by = PersNo.parse(buf)
        obj.added_at = Time.parse(buf)
        obj.type = MembershipType.parse(buf)
        return obj

class ReadRange(object):
    def __init__(self, first_read = 0, last_read = 0):
        self.first_read = first_read
        self.last_read = last_read
        
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.first_read = LocalTextNo.parse(buf)
        obj.last_read = LocalTextNo.parse(buf)
        return obj

    def __str__(self):
        return "<ReadRange %d-%d>" % (self.first_read, self.last_read)

    def to_string(self):
        return b"%d %d" % \
            (self.first_read,
             self.last_read)

class ArrayReadRange(Array):
    ELEMENT_CLASS = ReadRange

class Membership11(object):
    def __init__(self, position=0, last_time_read=None, conference=0, priority=0,
                 read_ranges=None, added_by=0, added_at=None, membership_type=None):
        if last_time_read is None:
            last_time_read = Time()
        if read_ranges is None:
            read_ranges = ArrayReadRange()
        if added_at is None:
            added_at = Time()
        if membership_type is None:
            membership_type = MembershipType()

        self.position = position
        self.last_time_read = last_time_read
        self.conference = conference
        self.priority = priority
        self.read_ranges = read_ranges
        self.added_by = added_by
        self.added_at = added_at
        self.type = membership_type

    def __repr__(self):
        return ("Membership11(position={pos!r}, last_time_read={ltr!r}, conference={conf!r}, "
             "priority={prio!r}, read_ranges={rr!r}, added_by={by!r}, added_at={at!r}, "
             "membership_type={type!r})".format(
                pos=self.position,
                ltr=self.last_time_read,
                conf=self.conference,
                prio=self.priority,
                rr=self.read_ranges,
                by=self.added_by,
                at=self.added_at,
                type=self.type))

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.position = Int32.parse(buf)
        obj.last_time_read  = Time.parse(buf)
        obj.conference = ConfNo.parse(buf)
        obj.priority = Int8.parse(buf)
        obj.read_ranges = ArrayReadRange.parse(buf)
        obj.added_by = PersNo.parse(buf)
        obj.added_at = Time.parse(buf)
        obj.type = MembershipType.parse(buf)
        return obj

    def __eq__(self, other):
        return (self.position == other.position and
                self.last_time_read == other.last_time_read and
                self.conference == other.conference and
                self.priority == other.priority and
                self.read_ranges == other.read_ranges and
                self.added_by == other.added_by and
                self.added_at == other.added_at and
                self.type == other.type)

Membership = Membership11

class Member(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.member  = PersNo.parse(buf)
        obj.added_by = PersNo.parse(buf)
        obj.added_at = Time.parse(buf)
        obj.type = MembershipType.parse(buf)
        return obj

# TEXT LIST

class TextList(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.first_local_no = LocalTextNo.parse(buf)
        obj.texts = ArrayTextNo.parse(buf)
        return obj

# TEXT MAPPING

class TextNumberPair(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.local_number = LocalTextNo.parse(buf)
        obj.global_number = TextNo.parse(buf)
        return obj

class ArrayTextNumberPair(Array):
    ELEMENT_CLASS = TextNumberPair

class TextMapping(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.range_begin = LocalTextNo.parse(buf) # Included in the range
        obj.range_end = LocalTextNo.parse(buf) # Not included in range (first after)
        obj.later_texts_exists = Bool.parse(buf)
        obj.block_type = Int32.parse(buf)

        obj.dict = {}
        obj.list = []

        if obj.block_type == 0:
            # Sparse
            obj.type_text = "sparse"
            obj.sparse_list = ArrayTextNumberPair.parse(buf)
            for tnp in obj.sparse_list:
                obj.dict[tnp.local_number] = tnp.global_number
                obj.list.append((tnp.local_number, tnp.global_number))
        elif obj.block_type == 1:
            # Dense
            obj.type_text = "dense"
            obj.dense_first = LocalTextNo.parse(buf)
            obj.dense_texts = ArrayInt32.parse(buf)
            local_number = obj.dense_first
            for global_number in obj.dense_texts:
                obj.dict[local_number] = global_number
                obj.list.append((local_number, global_number))
                local_number = local_number + 1
        else:
            raise ProtocolError
        return obj

    def __str__(self):
        if self.later_texts_exists:
            more = " (more exists)"
        else:
            more = ""
        return "<TextMapping (%s) %d...%d%s>" % (
            self.type_text,
            self.range_begin, self.range_end - 1 ,
            more)
# MARK

class Mark(object):
    def __init__(self, text_no=0, type=0):
        self.text_no = text_no
        self.type = type

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.text_no = TextNo.parse(buf)
        obj.type = Int8.parse(buf)
        return obj

    def __str__(self):
        return "<Mark %d (%d)>" % (self.text_no, self.type)

    def __eq__(self, other):
        return (self.text_no == other.text_no and
                self.type == other.type)
    
    def __ne__(self, other):
        return not self == other


# SERVER INFORMATION

class Info(object):
    def __init__(self):
        self.version = None
        self.conf_pres_conf = None
        self.pers_pres_conf = None
        self.motd_conf = None
        self.kom_news_conf = None
        self.motd_of_lyskom = None
        self.aux_item_list = []

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.version = Int32.parse(buf)
        obj.conf_pres_conf = ConfNo.parse(buf)
        obj.pers_pres_conf = ConfNo.parse(buf)
        obj.motd_conf = ConfNo.parse(buf)
        obj.kom_news_conf = ConfNo.parse(buf)
        obj.motd_of_lyskom = TextNo.parse(buf)
        obj.aux_item_list = ArrayAuxItem.parse(buf)
        return obj


class InfoOld(object):
    def __init__(self, info_old=None, version=0, conf_pres_conf=0, pers_pres_conf=0,
                 motd_conf=0, kom_news_conf=0, motd_of_lyskom=0):
        if info_old is None:
            self.version = version
            self.conf_pres_conf = conf_pres_conf
            self.pers_pres_conf = pers_pres_conf
            self.motd_conf = motd_conf
            self.kom_news_conf = kom_news_conf
            self.motd_of_lyskom = motd_of_lyskom
        else:
            self.version = info_old.version
            self.conf_pres_conf = info_old.conf_pres_conf
            self.pers_pres_conf = info_old.pers_pres_conf
            self.motd_conf = info_old.motd_conf
            self.kom_news_conf = info_old.kom_news_conf
            self.motd_of_lyskom = info_old.motd_of_lyskom

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.version = Int32.parse(buf)
        obj.conf_pres_conf = ConfNo.parse(buf)
        obj.pers_pres_conf = ConfNo.parse(buf)
        obj.motd_conf = ConfNo.parse(buf)
        obj.kom_news_conf = ConfNo.parse(buf)
        obj.motd_of_lyskom = TextNo.parse(buf)
        return obj

    def to_string(self):
        return b"%d %d %d %d %d %d" % (
            self.version,
            self.conf_pres_conf,
            self.pers_pres_conf,
            self.motd_conf,
            self.kom_news_conf,
            self.motd_of_lyskom)


class VersionInfo(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.protocol_version = Int32.parse(buf)
        obj.server_software = String.parse(buf)
        obj.software_version = String.parse(buf)
        return obj

    def __str__(self):
        return "<VersionInfo protocol %d by %s %s>" % \
               (self.protocol_version,
                self.server_software, self.software_version)

# New in protocol version 11
class StaticServerInfo(object): 
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.boot_time = Time.parse(buf)
        obj.save_time = Time.parse(buf)
        obj.db_status = String.parse(buf)
        obj.existing_texts = Int32.parse(buf)
        obj.highest_text_no = TextNo.parse(buf)
        obj.existing_confs = Int32.parse(buf)
        obj.existing_persons = Int32.parse(buf)
        obj.highest_conf_no = ConfNo.parse(buf)
        return obj

    def __str__(self):
        return "<StaticServerInfo>"

# SESSION INFORMATION

class SessionFlags(Bitstring):
    LENGTH = 8
    invisible = property(*_create_bitstring_accessors(0))
    user_active_used = property(*_create_bitstring_accessors(1))
    user_absent = property(*_create_bitstring_accessors(2))
    reserved3 = property(*_create_bitstring_accessors(3))
    reserved4 = property(*_create_bitstring_accessors(4))
    reserved5 = property(*_create_bitstring_accessors(5))
    reserved6 = property(*_create_bitstring_accessors(6))
    reserved7 = property(*_create_bitstring_accessors(7))

class DynamicSessionInfo(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.session = SessionNo.parse(buf)
        obj.person = PersNo.parse(buf)
        obj.working_conference = ConfNo.parse(buf)
        obj.idle_time = Int32.parse(buf)
        obj.flags = SessionFlags.parse(buf)
        obj.what_am_i_doing  = String.parse(buf)
        return obj

class StaticSessionInfo(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.username = String.parse(buf)
        obj.hostname = String.parse(buf)
        obj.ident_user = String.parse(buf)
        obj.bufection_time = Time.parse(buf)
        return obj

class SchedulingInfo(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.priority = Int16.parse(buf)
        obj.weight = Int16.parse(buf)
        return obj

class WhoInfo(object):
    def __init__(self, person=0, working_conference=0, session=0,
                 what_am_i_doing=None, username=None):
        if what_am_i_doing is None:
            what_am_i_doing = ""
        if username is None:
            username = ""
        self.person = person
        self.working_conference = working_conference
        self.session = session
        self.what_am_i_doing = what_am_i_doing
        self.username = username

    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.person = PersNo.parse(buf)
        obj.working_conference = ConfNo.parse(buf)
        obj.session = SessionNo.parse(buf)
        obj.what_am_i_doing  = String.parse(buf)
        obj.username = String.parse(buf)
        return obj

    def __eq__(self, other):
        return (self.person == other.person and
                self.working_conference == other.working_conference and
                self.session == other.session and 
                self.what_am_i_doing == other.what_am_i_doing and
                self.username == other.username)

    def __ne__(self, other):
        return not self == other
     
# STATISTICS

class StatsDescription(object):
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.what = ArrayString.parse(buf)
        obj.when = ArrayInt32.parse(buf)
        return obj
     
    def __str__(self):
        return "<StatsDescription>"

    def __eq__(self, other):
        return (self.what == other.what and
                self.when == other.when)

    def __ne__(self, other):
        return not self == other

class Stats(object):
    def __init__(self, average=0.0, ascent_rate=0.0, descent_rate=0.0):
        self.average = average
        self.ascent_rate = ascent_rate
        self.descent_rate = descent_rate
        
    @classmethod
    def parse(cls, buf):
        obj = cls()
        obj.average = Float.parse(buf)
        obj.ascent_rate = Float.parse(buf)
        obj.descent_rate = Float.parse(buf)
        return obj

    def __str__(self):
        return "<Stats %f + %f - %f>" % (self.average,
                                         self.ascent_rate,
                                         self.descent_rate)

    def __eq__(self, other):
        return (self.average == other.average and
                self.ascent_rate == other.ascent_rate and
                self.descent_rate == other.descent_rate)

    def __ne__(self, other):
        return not self == other


class ArrayMark(Array):
    ELEMENT_CLASS = Mark

class ArrayMember(Array):
    ELEMENT_CLASS = Member

class ArrayMembership11(Array):
    ELEMENT_CLASS = Membership11

class ArrayMembership10(Array):
    ELEMENT_CLASS = Membership10

class ArrayStats(Array):
    ELEMENT_CLASS = Stats

class ArrayConfNo(Array):
    ELEMENT_CLASS = ConfNo

class ArrayConfZInfo(Array):
    ELEMENT_CLASS = ConfZInfo

class ArrayDynamicSessionInfo(Array):
    ELEMENT_CLASS = DynamicSessionInfo
