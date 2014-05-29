# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

import time
import calendar

from .protocol import (
    read_first_non_ws,
    read_int_and_next,
    read_int,
    read_float)

from .errors import (
    ProtocolError,
    )


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


class EmptyResponse(object):
    @classmethod
    def parse(cls, conn):
        return None

class String(str):
    @classmethod
    def parse(cls, buf):
        # Parse a string (Hollerith notation)
        (length, h) = read_int_and_next(buf)
        if h != "H":
            raise ProtocolError()
        return cls(buf.receive_string(length))

class Float(float):
    @classmethod
    def parse(cls, buf):
        return read_float(buf)

class Int(int):
    @classmethod
    def parse(cls, buf):
        return read_int(buf)

        
class Int16(Int):
    pass

class Int32(Int):
    pass

class ConfNo(Int16):
    pass

class PersonNo(ConfNo):
    pass

class TextNo(Int32):
    pass

class LocalTextNo(Int32):
    pass

class SessionNo(Int32):
    pass

class Array(object):
    def __init__(self, element_cls):
        self._element_cls = element_cls

    def parse(self, conn):
        length = read_int(conn)
        res = []
        left = read_first_non_ws(conn)
        if left == "*":
            # Empty or special case of unwanted data
            return res
        elif left != "{":
            raise ProtocolError()
        for i in range(0, length):
            obj = self._element_cls.parse(conn)
            res.append(obj)
        right = read_first_non_ws(conn)
        if right != "}":
            raise ProtocolError()
        return res

class Bitstring(list):
    @classmethod
    def parse(cls, conn, length):
        obj = cls()
        char = read_first_non_ws(conn)
        for i in range(0, length):
            if char == "0":
                obj.append(0)
            elif char == "1":
                obj.append(1)
            else:
                raise ProtocolError()
            char = conn.receive_char()
        return obj


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
    def parse(cls, conn):
        obj = cls()
        obj.seconds = read_int(conn)
        obj.minutes = read_int(conn)
        obj.hours = read_int(conn)
        obj.day = read_int(conn)
        obj.month = read_int(conn)
        obj.year = read_int(conn)
        obj.day_of_week = read_int(conn)
        obj.day_of_year = read_int(conn)
        obj.is_dst = read_int(conn)
        return obj

    def to_string(self):
        return "%d %d %d %d %d %d %d %d %d" % (
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

    def __repr__(self):
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
    def parse(cls, conn):
        obj = cls()
        obj.name = String.parse(conn)
        obj.type = ConfType.parse(conn, old_format=1)
        obj.conf_no = read_int(conn)
        return obj

    def __repr__(self):
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
    def parse(cls, conn):
        obj = cls()
        obj.type = read_int(conn)
        if obj.type in [MI_REC_TIME, MI_SENT_AT]:
            obj.data = Time.parse(conn)
        else:
            obj.data = read_int(conn)
        return obj

    def __repr__(self):
        return "<MiscInfo %d: %s>" % (self.type, self.data)

    def __eq__(self, other):
        return (self.type == other.type and
                self.data == other.data)

    def __ne__(self, other):
        return not self == other


# COOKED MISC-INFO (MORE TASTY)
# N.B: This class represents the whole array, not just one item

class MIRecipient(object):
    def __init__(self, type = MIR_TO, recpt = 0):
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

class CookedMiscInfo(object):
    def __init__(self):
        self.recipient_list = []
        self.comment_to_list = []
        self.comment_in_list = []

    @classmethod
    def parse(cls, conn):
        obj = cls()
        raw = Array(RawMiscInfo).parse(conn)
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
        list = []
        for r in self.comment_to_list + \
            self.recipient_list + \
            self.comment_in_list:
            list = list + r.get_tuples()
        return "%d { %s}" % (len(list),
                             "".join(["%d %d " % \
                                          (x[0], x[1]) for x in list]))


    def __eq__(self, other):
        return (self.recipient_list == other.recipient_list and
                self.comment_to_list == other.comment_to_list and
                self.comment_in_list == other.comment_in_list)

    def __ne__(self, other):
        return not self == other


# AUX INFO

class AuxItemFlags(object):
    def __init__(self):
        self.deleted = 0
        self.inherit = 0
        self.secret = 0
        self.hide_creator = 0
        self.dont_garb = 0
        self.reserved2 = 0
        self.reserved3 = 0
        self.reserved4 = 0

    @classmethod
    def parse(cls, conn):
        obj = cls()
        (obj.deleted,
         obj.inherit,
         obj.secret,
         obj.hide_creator,
         obj.dont_garb,
         obj.reserved2,
         obj.reserved3,
         obj.reserved4) = Bitstring.parse(conn, 8)
        return obj

    def to_string(self):
        return "%d%d%d%d%d%d%d%d" % \
               (self.deleted,
                self.inherit,
                self.secret,
                self.hide_creator,
                self.dont_garb,
                self.reserved2,
                self.reserved3,
                self.reserved4)

    def __eq__(self, other):
        return (self.deleted == other.deleted and
                self.inherit == other.inherit and
                self.secret == other.secret and
                self.hide_creator == other.hide_creator and
                self.dont_garb == other.dont_garb and
                self.reserved2 == other.reserved2 and
                self.reserved3 == other.reserved3 and
                self.reserved4 == other.reserved4)

    def __ne__(self, other):
        return not self == other
        

# This class works as Aux-Item on reception, and
# Aux-Item-Input when being sent.
class AuxItem(object): 
    def __init__(self, tag = None, data = ""):
        self.aux_no = None # not part of Aux-Item-Input
        self.tag = tag
        self.creator = None # not part of Aux-Item-Input
        self.created_at = None # not part of Aux-Item-Input
        self.flags = AuxItemFlags()
        self.inherit_limit = 0
        self.data = data

    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.aux_no = read_int(conn)
        obj.tag = read_int(conn)
        obj.creator = read_int(conn)
        obj.created_at = Time.parse(conn)
        obj.flags = AuxItemFlags.parse(conn)
        obj.inherit_limit = read_int(conn)
        obj.data = String.parse(conn)
        return obj

    def __repr__(self):
        return "<AuxItem %d>" % self.tag

    def to_string(self):
        return "%d %s %d %dH%s" % \
               (self.tag,
                self.flags.to_string(),
                self.inherit_limit,
                len(self.data), self.data)

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
    def parse(cls, conn, old_format=0):
        obj = cls()
        obj.creation_time = Time.parse(conn)
        obj.author = read_int(conn)
        obj.no_of_lines = read_int(conn)
        obj.no_of_chars = read_int(conn)
        obj.no_of_marks = read_int(conn)
        obj.misc_info = CookedMiscInfo.parse(conn)
        if old_format:
            obj.aux_items = []
        else:
            obj.aux_items = Array(AuxItem).parse(conn)
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

class ConfType(object):
    def __init__(self):
        self.rd_prot = 0
        self.original = 0
        self.secret = 0
        self.letterbox = 0
        self.allow_anonymous = 0
        self.forbid_secret = 0
        self.reserved2 = 0
        self.reserved3 = 0

    @classmethod
    def parse(cls, conn, old_format=0):
        obj = cls()
        if old_format:
            (obj.rd_prot,
             obj.original,
             obj.secret,
             obj.letterbox) = Bitstring.parse(conn, 4)
            (obj.allow_anonymous,
             obj.forbid_secret,
             obj.reserved2,
             obj.reserved3) = (0,0,0,0)
        else:
            (obj.rd_prot,
             obj.original,
             obj.secret,
             obj.letterbox,
             obj.allow_anonymous,
             obj.forbid_secret,
             obj.reserved2,
             obj.reserved3) = Bitstring.parse(conn, 8)
        return obj

    def to_string(self):
        return "%d%d%d%d%d%d%d%d" % \
               (self.rd_prot,
                self.original,
                self.secret,
                self.letterbox,
                self.allow_anonymous,
                self.forbid_secret,
                self.reserved2,
                self.reserved3)

class Conference(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.name = String.parse(conn)
        obj.type = ConfType.parse(conn)
        obj.creation_time = Time.parse(conn)
        obj.last_written = Time.parse(conn)
        obj.creator = read_int(conn)
        obj.presentation = read_int(conn)
        obj.supervisor = read_int(conn)
        obj.permitted_submitters = read_int(conn)
        obj.super_conf = read_int(conn)
        obj.msg_of_day = read_int(conn)
        obj.nice = read_int(conn)
        obj.keep_commented = read_int(conn)
        obj.no_of_members = read_int(conn)
        obj.first_local_no = read_int(conn)
        obj.no_of_texts = read_int(conn)
        obj.expire = read_int(conn)
        obj.aux_items = Array(AuxItem).parse(conn)
        return obj

    def __repr__(self):
        return "<Conference %s>" % self.name
    
class UConference(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.name = String.parse(conn)
        obj.type = ConfType.parse(conn)
        obj.highest_local_no = read_int(conn)
        obj.nice = read_int(conn)
        return obj

    def __repr__(self):
        return "<UConference %s>" % self.name
    
# PERSON

class PrivBits(object):
    def __init__(self):
        self.wheel = 0
        self.admin = 0
        self.statistic = 0
        self.create_pers = 0
        self.create_conf = 0
        self.change_name = 0
        self.flg7 = 0
        self.flg8 = 0
        self.flg9 = 0
        self.flg10 = 0
        self.flg11 = 0
        self.flg12 = 0
        self.flg13 = 0
        self.flg14 = 0
        self.flg15 = 0
        self.flg16 = 0

    @classmethod
    def parse(cls, conn):
        obj = cls()
        (obj.wheel,
         obj.admin,
         obj.statistic,
         obj.create_pers,
         obj.create_conf,
         obj.change_name,
         obj.flg7,
         obj.flg8,
         obj.flg9,
         obj.flg10,
         obj.flg11,
         obj.flg12,
         obj.flg13,
         obj.flg14,
         obj.flg15,
         obj.flg16) = Bitstring.parse(conn, 16)
        return obj

    def to_string(self):
        return "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d" % \
               (self.wheel,
                self.admin,
                self.statistic,
                self.create_pers,
                self.create_conf,
                self.change_name,
                self.flg7,
                self.flg8,
                self.flg9,
                self.flg10,
                self.flg11,
                self.flg12,
                self.flg13,
                self.flg14,
                self.flg15,
                self.flg16)
    
class PersonalFlags(object):
    def __init__(self):
        self.unread_is_secret = 0
        self.flg2 = 0
        self.flg3 = 0
        self.flg4 = 0
        self.flg5 = 0
        self.flg6 = 0
        self.flg7 = 0
        self.flg8 = 0

    @classmethod
    def parse(cls, conn):
        obj = cls()
        (obj.unread_is_secret,
         obj.flg2,
         obj.flg3,
         obj.flg4,
         obj.flg5,
         obj.flg6,
         obj.flg7,
         obj.flg8) = Bitstring.parse(conn, 8)
        return obj

    def to_string(self):
        return "%d%d%d%d%d%d%d%d" % \
               (self.unread_is_secret,
                self.flg2,
                self.flg3,
                self.flg4,
                self.flg5,
                self.flg6,
                self.flg7,
                self.flg8)

class Person(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.username = String.parse(conn)
        obj.privileges = PrivBits.parse(conn)
        obj.flags = PersonalFlags.parse(conn)
        obj.last_login = Time.parse(conn)
        obj.user_area = read_int(conn)
        obj.total_time_present = read_int(conn)
        obj.sessions = read_int(conn)
        obj.created_lines = read_int(conn)
        obj.created_bytes = read_int(conn)
        obj.read_texts = read_int(conn)
        obj.no_of_text_fetches = read_int(conn)
        obj.created_persons = read_int(conn)
        obj.created_confs = read_int(conn)
        obj.first_created_local_no = read_int(conn)
        obj.no_of_created_texts = read_int(conn)
        obj.no_of_marks = read_int(conn)
        obj.no_of_confs = read_int(conn)
        return obj

# MEMBERSHIP

class MembershipType(object):
    def __init__(self, invitation=0, passive=0, secret=0, passive_message_invert=0,
                 reserved2=0, reserved3=0, reserved4=0, reserved5=0):
        self.invitation = invitation
        self.passive = passive
        self.secret = secret
        self.passive_message_invert = passive_message_invert
        self.reserved2 = reserved2
        self.reserved3 = reserved3
        self.reserved4 = reserved4
        self.reserved5 = reserved5

    @classmethod
    def parse(cls, conn):
        obj = cls()
        (obj.invitation,
         obj.passive,
         obj.secret,
         obj.passive_message_invert,
         obj.reserved2,
         obj.reserved3,
         obj.reserved4,
         obj.reserved5) = Bitstring.parse(conn, 8)
        return obj

    def to_string(self):
        return "%d%d%d%d%d%d%d%d" % \
               (self.invitation,
                self.passive,
                self.secret,
                self.passive_message_invert,
                self.reserved2,
                self.reserved3,
                self.reserved4,
                self.reserved5)

    def __eq__(self, other):
        return (self.invitation == other.invitation and
                self.passive == other.passive and
                self.secret == other.secret and
                self.passive_message_invert == other.passive_message_invert and
                self.reserved2 == other.reserved2 and
                self.reserved3 == other.reserved3 and
                self.reserved4 == other.reserved4 and
                self.reserved5 == other.reserved5)

    def __ne__(self, other):
        return not self == other
        

class Membership10(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.position = read_int(conn)
        obj.last_time_read  = Time.parse(conn)
        obj.conference = read_int(conn)
        obj.priority = read_int(conn)
        obj.last_text_read = read_int(conn)
        obj.read_texts = Array(LocalTextNo).parse(conn)
        obj.added_by = read_int(conn)
        obj.added_at = Time.parse(conn)
        obj.type = MembershipType.parse(conn)
        return obj

class ReadRange(object):
    def __init__(self, first_read = 0, last_read = 0):
        self.first_read = first_read
        self.last_read = last_read
        
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.first_read = read_int(conn)
        obj.last_read = read_int(conn)
        return obj

    def __repr__(self):
        return "<ReadRange %d-%d>" % (self.first_read, self.last_read)

    def to_string(self):
        return "%d %d" % \
               (self.first_read,
                self.last_read)
    
class Membership11(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.position = read_int(conn)
        obj.last_time_read  = Time.parse(conn)
        obj.conference = read_int(conn)
        obj.priority = read_int(conn)
        obj.read_ranges = Array(ReadRange).parse(conn)
        obj.added_by = read_int(conn)
        obj.added_at = Time.parse(conn)
        obj.type = MembershipType.parse(conn)
        return obj

Membership = Membership11

class Member(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.member  = read_int(conn)
        obj.added_by = read_int(conn)
        obj.added_at = Time.parse(conn)
        obj.type = MembershipType.parse(conn)
        return obj

# TEXT LIST

class TextList(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.first_local_no = read_int(conn)
        obj.texts = Array(TextNo).parse(conn)
        return obj

# TEXT MAPPING

class TextNumberPair(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.local_number = read_int(conn)
        obj.global_number = read_int(conn)
        return obj
    
class TextMapping(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.range_begin = read_int(conn) # Included in the range
        obj.range_end = read_int(conn) # Not included in range (first after)
        obj.later_texts_exists = read_int(conn)
        obj.block_type = read_int(conn)

        obj.dict = {}
        obj.list = []

        if obj.block_type == 0:
            # Sparse
            obj.type_text = "sparse"
            obj.sparse_list = Array(TextNumberPair).parse(conn)
            for tnp in obj.sparse_list:
                obj.dict[tnp.local_number] = tnp.global_number
                obj.list.append((tnp.local_number, tnp.global_number))
        elif obj.block_type == 1:
            # Dense
            obj.type_text = "dense"
            obj.dense_first = read_int(conn)
            obj.dense_texts = Array(Int32).parse(conn)
            local_number = obj.dense_first
            for global_number in obj.dense_texts:
                obj.dict[local_number] = global_number
                obj.list.append((local_number, global_number))
                local_number = local_number + 1
        else:
            raise ProtocolError
        return obj

    def __repr__(self):
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
    def parse(cls, conn):
        obj = cls()
        obj.text_no = read_int(conn)
        obj.type = read_int(conn)
        return obj

    def __repr__(self):
        return "<Mark %d (%d)>" % (self.text_no, self.type)

    def __eq__(self, other):
        return (self.text_no == other.text_no and
                self.type == other.type)
    
    def __ne__(self, other):
        return not self == other


# SERVER INFORMATION

# This class works as Info on reception, and
# Info-Old when being sent.
class Info(object):
    def __init__(self):
        self.version = None
        self.conf_pres_conf = None
        self.pers_pres_conf = None
        self.motd_conf = None
        self.kom_news_conf = None
        self.motd_of_lyskom = None
        self.aux_item_list = [] # not part of Info-Old

    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.version = read_int(conn)
        obj.conf_pres_conf = read_int(conn)
        obj.pers_pres_conf = read_int(conn)
        obj.motd_conf = read_int(conn)
        obj.kom_news_conf = read_int(conn)
        obj.motd_of_lyskom = read_int(conn)
        obj.aux_item_list = Array(AuxItem).parse(conn)
        return obj

    def to_string(self):
        return "%d %d %d %d %d %d" % (
            self.version,
            self.conf_pres_conf,
            self.pers_pres_conf,
            self.motd_conf,
            self.kom_news_conf,
            self.motd_of_lyskom)

class VersionInfo(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.protocol_version = read_int(conn)
        obj.server_software = String.parse(conn)
        obj.software_version = String.parse(conn)
        return obj

    def __repr__(self):
        return "<VersionInfo protocol %d by %s %s>" % \
               (self.protocol_version,
                self.server_software, self.software_version)

# New in protocol version 11
class StaticServerInfo(object): 
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.boot_time = Time.parse(conn)
        obj.save_time = Time.parse(conn)
        obj.db_status = String.parse(conn)
        obj.existing_texts = read_int(conn)
        obj.highest_text_no = read_int(conn)
        obj.existing_confs = read_int(conn)
        obj.existing_persons = read_int(conn)
        obj.highest_conf_no = read_int(conn)
        return obj

    def __repr__(self):
        return "<StaticServerInfo>"

# SESSION INFORMATION

class SessionFlags(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        (obj.invisible,
         obj.user_active_used,
         obj.user_absent,
         obj.reserved3,
         obj.reserved4,
         obj.reserved5,
         obj.reserved6,
         obj.reserved7) = Bitstring.parse(conn, 8)
        return obj

class DynamicSessionInfo(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.session = read_int(conn)
        obj.person = read_int(conn)
        obj.working_conference = read_int(conn)
        obj.idle_time = read_int(conn)
        obj.flags = SessionFlags.parse(conn)
        obj.what_am_i_doing  = String.parse(conn)
        return obj

class StaticSessionInfo(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.username = String.parse(conn)
        obj.hostname = String.parse(conn)
        obj.ident_user = String.parse(conn)
        obj.connection_time = Time.parse(conn)
        return obj

class SchedulingInfo(object):
    @classmethod
    def parse(cls, conn):
        obj = cls()
        obj.priority = read_int(conn)
        obj.weight = read_int(conn)
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
    def parse(cls, conn):
        obj = cls()
        obj.person = read_int(conn)
        obj.working_conference = read_int(conn)
        obj.session = read_int(conn)
        obj.what_am_i_doing  = String.parse(conn)
        obj.username = String.parse(conn)
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
    def parse(cls, conn):
        obj = cls()
        obj.what = Array(String).parse(conn)
        obj.when = Array(Int32).parse(conn)
        return obj
     
    def __repr__(self):
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
    def parse(cls, conn):
        obj = cls()
        obj.average = Float.parse(conn)
        obj.ascent_rate = Float.parse(conn)
        obj.descent_rate = Float.parse(conn)
        return obj

    def __repr__(self):
        return "<Stats %f + %f - %f>" % (self.average,
                                         self.ascent_rate,
                                         self.descent_rate)

    def __eq__(self, other):
        return (self.average == other.average and
                self.ascent_rate == other.ascent_rate and
                self.descent_rate == other.descent_rate)

    def __ne__(self, other):
        return not self == other
