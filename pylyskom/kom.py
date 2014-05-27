# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

import time
import calendar


#
# Constants
#

WHITESPACE = " \t\r\n"
DIGITS = "01234567890"
FLOAT_CHARS = DIGITS + "eE.-+"

ORD_0 = ord("0")
MAX_TEXT_SIZE = int(2**31-1)

# All errors belong to this class
class Error(Exception): pass

# All Protocol A errors are subclasses of ServerError
class ServerError(Error): pass
class NotImplemented(ServerError): pass # (2)
class ObsoleteCall(ServerError): pass # (3)
class InvalidPassword(ServerError): pass # (4)
class StringTooLong(ServerError): pass # (5)
class LoginFirst(ServerError): pass # (6)
class LoginDisallowed(ServerError): pass # (7)
class ConferenceZero(ServerError): pass # (8)
class UndefinedConference(ServerError): pass # (9)
class UndefinedPerson(ServerError): pass # (10)
class AccessDenied(ServerError): pass # (11)
class PermissionDenied(ServerError): pass # (12)
class NotMember(ServerError): pass # (13)
class NoSuchText(ServerError): pass # (14)
class TextZero(ServerError): pass # (15)
class NoSuchLocalText(ServerError): pass # (16)
class LocalTextZero(ServerError): pass # (17)
class BadName(ServerError): pass # (18)
class IndexOutOfRange(ServerError): pass # (19)
class ConferenceExists(ServerError): pass # (20)
class PersonExists(ServerError): pass # (21)
class SecretPublic(ServerError): pass # (22)
class Letterbox(ServerError): pass # (23)
class LdbError(ServerError): pass # (24)
class IllegalMisc(ServerError): pass # (25)
class IllegalInfoType(ServerError): pass # (26)
class AlreadyRecipient(ServerError): pass # (27)
class AlreadyComment(ServerError): pass # (28)
class AlreadyFootnote(ServerError): pass # (29)
class NotRecipient(ServerError): pass # (30)
class NotComment(ServerError): pass # (31)
class NotFootnote(ServerError): pass # (32)
class RecipientLimit(ServerError): pass # (33)
class CommentLimit(ServerError): pass # (34)
class FootnoteLimit(ServerError): pass # (35)
class MarkLimit(ServerError): pass # (36)
class NotAuthor(ServerError): pass # (37)
class NoConnect(ServerError): pass # (38)
class OutOfmemory(ServerError): pass # (39)
class ServerIsCrazy(ServerError): pass # (40)
class ClientIsCrazy(ServerError): pass # (41)
class UndefinedSession(ServerError): pass # (42)
class RegexpError(ServerError): pass # (43)
class NotMarked(ServerError): pass # (44)
class TemporaryFailure(ServerError): pass # (45)
class LongArray(ServerError): pass # (46)
class AnonymousRejected(ServerError): pass # (47)
class IllegalAuxItem(ServerError): pass # (48)
class AuxItemPermission(ServerError): pass # (49)
class UnknownAsync(ServerError): pass # (50)
class InternalError(ServerError): pass # (51)
class FeatureDisabled(ServerError): pass # (52)
class MessageNotSent(ServerError): pass # (53)
class InvalidMembershipType(ServerError): pass # (54)
class InvalidRange(ServerError): pass # (55)
class InvalidRangeList(ServerError): pass # (56)
class UndefinedMeasurement(ServerError): pass # (57)
class PriorityDenied(ServerError): pass # (58)
class WeightDenied(ServerError): pass # (59)
class WeightZero(ServerError): pass # (60)
class BadBool(ServerError): pass # (61)

# Mapping from Protocol A error_no to Python exception
error_dict = {
    2: NotImplemented,
    3: ObsoleteCall,
    4: InvalidPassword,
    5: StringTooLong,
    6: LoginFirst,
    7: LoginDisallowed,
    8: ConferenceZero,
    9: UndefinedConference,
    10: UndefinedPerson,
    11: AccessDenied,
    12: PermissionDenied,
    13: NotMember,
    14: NoSuchText,
    15: TextZero,
    16: NoSuchLocalText,
    17: LocalTextZero,
    18: BadName,
    19: IndexOutOfRange,
    20: ConferenceExists,
    21: PersonExists,
    22: SecretPublic,
    23: Letterbox,
    24: LdbError,
    25: IllegalMisc,
    26: IllegalInfoType,
    27: AlreadyRecipient,
    28: AlreadyComment,
    29: AlreadyFootnote,
    30: NotRecipient,
    31: NotComment,
    32: NotFootnote,
    33: RecipientLimit,
    34: CommentLimit,
    35: FootnoteLimit,
    36: MarkLimit,
    37: NotAuthor,
    38: NoConnect,
    39: OutOfmemory,
    40: ServerIsCrazy,
    41: ClientIsCrazy,
    42: UndefinedSession,
    43: RegexpError,
    44: NotMarked,
    45: TemporaryFailure,
    46: LongArray,
    47: AnonymousRejected,
    48: IllegalAuxItem,
    49: AuxItemPermission,
    50: UnknownAsync,
    51: InternalError,
    52: FeatureDisabled,
    53: MessageNotSent,
    54: InvalidMembershipType,
    55: InvalidRange,
    56: InvalidRangeList,
    57: UndefinedMeasurement,
    58: PriorityDenied,
    59: WeightDenied,
    60: WeightZero,
    61: BadBool,
    }

# All local errors are subclasses of LocalError
class LocalError(Error): pass
class BadInitialResponse(LocalError): pass # Not "LysKOM\n"
class BadRequestId(LocalError): pass  # Bad request id encountered
class ProtocolError(LocalError): pass # E.g. unexpected response
class UnimplementedAsync(LocalError): pass # Unknown asynchronous message
class ReceiveError(LocalError): pass # Error reading data from the server

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


class Requests(object):
    LOGOUT = 1 # (1) Recommended
    CHANGE_CONFERENCE = 2 # (1) Recommended
    CHANGE_NAME = 3 # (1) Recommended
    CHANGE_WHAT_I_AM_DOING = 4 # (1) Recommended
    SET_PRIV_BITS = 7 # (1) Recommended
    SET_PASSWD = 8 # (1) Recommended
    DELETE_CONF = 11 # (1) Recommended
    SUB_MEMBER = 15 # (1) Recommended
    SET_PRESENTATION = 16 # (1) Recommended
    SET_ETC_MOTD = 17 # (1) Recommended
    SET_SUPERVISOR = 18 # (1) Recommended
    SET_PERMITTED_SUBMITTERS = 19 # (1) Recommended
    SET_SUPER_CONF = 20 # (1) Recommended
    SET_CONF_TYPE = 21 # (1) Recommended
    SET_GARB_NICE = 22 # (1) Recommended
    GET_MARKS = 23 # (1) Recommended
    GET_TEXT = 25 # (1) Recommended
    MARK_AS_READ = 27 # (1) Recommended
    DELETE_TEXT = 29 # (1) Recommended
    ADD_RECIPIENT = 30 # (1) Recommended
    SUB_RECIPIENT = 31 # (1) Recommended
    ADD_COMMENT = 32 # (1) Recommended
    SUB_COMMENT = 33 # (1) Recommended
    GET_MAP = 34 # (1) Obsolete (10) Use LOCAL_TO_GLOBAL (103)
    GET_TIME = 35 # (1) Recommended
    ADD_FOOTNOTE = 37 # (1) Recommended
    SUB_FOOTNOTE = 38 # (1) Recommended
    SET_UNREAD = 40 # (1) Recommended
    SET_MOTD_OF_LYSKOM = 41 # (1) Recommended
    ENABLE = 42 # (1) Recommended
    SYNC_KOM = 43 # (1) Recommended
    SHUTDOWN_KOM = 44 # (1) Recommended
    GET_PERSON_STAT = 49 # (1) Recommended
    GET_UNREAD_CONFS = 52 # (1) Recommended
    SEND_MESSAGE = 53 # (1) Recommended
    DISCONNECT = 55 # (1) Recommended
    WHO_AM_I = 56 # (1) Recommended
    SET_USER_AREA = 57 # (2) Recommended
    GET_LAST_TEXT = 58 # (3) Recommended
    FIND_NEXT_TEXT_NO = 60 # (3) Recommended
    FIND_PREVIOUS_TEXT_NO = 61 # (3) Recommended
    LOGIN = 62 # (4) Recommended
    SET_CLIENT_VERSION = 69 # (6) Recommended
    GET_CLIENT_NAME = 70 # (6) Recommended
    GET_CLIENT_VERSION = 71 # (6) Recommended
    MARK_TEXT = 72 # (4) Recommended
    UNMARK_TEXT = 73 # (6) Recommended
    RE_Z_LOOKUP = 74 # (7) Recommended
    GET_VERSION_INFO = 75 # (7) Recommended
    LOOKUP_Z_NAME = 76 # (7) Recommended
    SET_LAST_READ = 77 # (8) Recommended
    GET_UCONF_STAT = 78 # (8) Recommended
    SET_INFO = 79 # (9) Recommended
    ACCEPT_ASYNC = 80 # (9) Recommended
    QUERY_ASYNC = 81 # (9) Recommended
    USER_ACTIVE = 82 # (9) Recommended
    WHO_IS_ON_DYNAMIC = 83 # (9) Recommended
    GET_STATIC_SESSION_INFO = 84 # (9) Recommended
    GET_COLLATE_TABLE = 85 # (10) Recommended
    CREATE_TEXT = 86 # (10) Recommended
    CREATE_ANONYMOUS_TEXT = 87 # (10) Recommended
    CREATE_CONF = 88 # (10) Recommended
    CREATE_PERSON = 89 # (10) Recommended
    GET_TEXT_STAT = 90 # (10) Recommended
    GET_CONF_STAT = 91 # (10) Recommended
    MODIFY_TEXT_INFO = 92 # (10) Recommended
    MODIFY_CONF_INFO = 93 # (10) Recommended
    GET_INFO = 94 # (10) Recommended
    MODIFY_SYSTEM_INFO = 95 # (10) Recommended
    QUERY_PREDEFINED_AUX_ITEMS = 96 # (10) Recommended
    SET_EXPIRE = 97 # (10) Experimental
    QUERY_READ_TEXTS_10 = 98 # (10) Obsolete (11) Use QUERY_READ_TEXTS (107)
    GET_MEMBERSHIP_10 = 99 # (10) Obsolete (11) Use GET_MEMBERSHIP (108)
    ADD_MEMBER = 100 # (10) Recommended
    GET_MEMBERS = 101 # (10) Recommended
    SET_MEMBERSHIP_TYPE = 102 # (10) Recommended
    LOCAL_TO_GLOBAL = 103 # (10) Recommended
    MAP_CREATED_TEXTS = 104 # (10) Recommended
    SET_KEEP_COMMENTED = 105 # (11) Recommended (10) Experimental
    SET_PERS_FLAGS = 106 # (10) Recommended
    QUERY_READ_TEXTS = 107 # (11) Recommended
    GET_MEMBERSHIP = 108 # (11) Recommended
    MARK_AS_UNREAD = 109 # (11) Recommended
    SET_READ_RANGES = 110 # (11) Recommended
    GET_STATS_DESCRIPTION = 111 # (11) Recommended
    GET_STATS = 112 # (11) Recommended
    GET_BOOTTIME_INFO = 113 # (11) Recommended
    FIRST_UNUSED_CONF_NO = 114 # (11) Recommended
    FIRST_UNUSED_TEXT_NO = 115 # (11) Recommended
    FIND_NEXT_CONF_NO = 116 # (11) Recommended
    FIND_PREVIOUS_CONF_NO = 117 # (11) Recommended
    GET_SCHEDULING = 118 # (11) Experimental
    SET_SCHEDULING = 119 # (11) Experimental
    SET_CONNECTION_TIME_FORMAT = 120 # (11) Recommended
    LOCAL_TO_GLOBAL_REVERSE = 121 # (11) Recommended
    MAP_CREATED_TEXTS_REVERSE = 122 # (11) Recommended




#
# Classes for requests to the server are all subclasses of Request.
#

class Request(object):
    CALL_NO = None # Override

    def get_request(self):
        """Returns the serialized call parameters.
        """
        # Override and return the request as a string.
        raise NotImplementedError()

    def parse_response(self, conn):
        # Default response parser expects nothing.
        # Override when appropriate.
        return None

    def to_string(self):
        """Returns the full serialized request, including CALL_NO and
        end of line.
        """
        s = "%d" % (self.CALL_NO, )
        request = self.get_request()
        if len(request) > 0:
            s += " " + request
        return s + "\n"


# login-old [0] (1) Obsolete (4) Use login (62)

# logout [1] (1) Recommended
class ReqLogout(Request):
    CALL_NO = Requests.LOGOUT
    def get_request(self):
        return ""

# change-conference [2] (1) Recommended
class ReqChangeConference(Request):
    CALL_NO = Requests.CHANGE_CONFERENCE
    def __init__(self, conf_no):
        self.conf_no = conf_no

    def get_request(self):
        return "%d" % (self.conf_no,)

# change-name [3] (1) Recommended
class ReqChangeName(Request):
    CALL_NO = Requests.CHANGE_NAME
    def __init__(self, conf_no, new_name):
        self.conf_no = conf_no
        self.new_name = new_name

    def get_request(self):
        return "%d %s" % (self.conf_no, to_hstring(self.new_name))

# change-what-i-am-doing [4] (1) Recommended
class ReqChangeWhatIAmDoing(Request):
    CALL_NO = Requests.CHANGE_WHAT_I_AM_DOING
    def __init__(self, what):
        self.what = what

    def get_request(self):
        return "%s" % (to_hstring(self.what),)

# create-person-old [5] (1) Obsolete (10) Use create-person (89)
# get-person-stat-old [6] (1) Obsolete (1) Use get-person-stat (49)

# set-priv-bits [7] (1) Recommended
class ReqSetPrivBits(Request):
    CALL_NO = Requests.SET_PRIV_BITS
    def __init__(self, person_no, privileges):
        self.person_no = person_no
        self.privileges = privileges

    def get_request(self):
        return "%d %s" % (self.person_no, self.privileges.to_string())

# set-passwd [8] (1) Recommended
class ReqSetPasswd(Request):
    CALL_NO = Requests.SET_PASSWD
    def __init__(self, person_no, old_pwd, new_pwd):
        self.person_no = person_no
        self.old_pwd = old_pwd
        self.new_pwd = new_pwd

    def get_request(self):
        return "%d %s %s" % (self.person_no,
                                 to_hstring(self.old_pwd),
                                 to_hstring(self.new_pwd))

# query-read-texts-old [9] (1) Obsolete (10) Use query-read-texts (98)
# create-conf-old [10] (1) Obsolete (10) Use create-conf (88)

# delete-conf [11] (1) Recommended
class ReqDeleteConf(Request):
    CALL_NO = Requests.DELETE_CONF
    def __init__(self, conf_no):
        self.conf_no = conf_no

    def get_request(self):
        return "%d" % (self.conf_no,)

# lookup-name [12] (1) Obsolete (7) Use lookup-z-name (76)
# get-conf-stat-older [13] (1) Obsolete (10) Use get-conf-stat (91)
# add-member-old [14] (1) Obsolete (10) Use add-member (100)

# sub-member [15] (1) Recommended
class ReqSubMember(Request):
    CALL_NO = Requests.SUB_MEMBER
    def __init__(self, conf_no, person_no):
        self.conf_no = conf_no
        self.person_no = person_no
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.person_no)

# set-presentation [16] (1) Recommended
class ReqSetPresentation(Request):
    CALL_NO = Requests.SET_PRESENTATION
    def __init__(self, conf_no, text_no):
        self.conf_no = conf_no
        self.text_no = text_no
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.text_no)

# set-etc-motd [17] (1) Recommended
class ReqSetEtcMoTD(Request):
    CALL_NO = Requests.SET_ETC_MOTD
    def __init__(self, conf_no, text_no):
        self.conf_no = conf_no
        self.text_no = text_no
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.text_no)

# set-supervisor [18] (1) Recommended
class ReqSetSupervisor(Request):
    CALL_NO = Requests.SET_SUPERVISOR
    def __init__(self, conf_no, admin):
        self.conf_no = conf_no
        self.admin = admin
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.admin)

# set-permitted-submitters [19] (1) Recommended
class ReqSetPermittedSubmitters(Request):
    CALL_NO = Requests.SET_PERMITTED_SUBMITTERS
    def __init__(self, conf_no, perm_sub):
        self.conf_no = conf_no
        self.perm_sub = perm_sub
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.perm_sub)

# set-super-conf [20] (1) Recommended
class ReqSetSuperConf(Request):
    CALL_NO = Requests.SET_SUPER_CONF
    def __init__(self, conf_no, super_conf):
        self.conf_no = conf_no
        self.super_conf = super_conf
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.super_conf)

# set-conf-type [21] (1) Recommended
class ReqSetConfType(Request):
    CALL_NO = Requests.SET_CONF_TYPE
    def __init__(self, conf_no, conf_type):
        self.conf_no = conf_no
        self.conf_type = conf_type
        
    def get_request(self):
        return "%d %s" % (self.conf_no, self.conf_type.to_string())

# set-garb-nice [22] (1) Recommended
class ReqSetGarbNice(Request):
    CALL_NO = Requests.SET_GARB_NICE
    def __init__(self, conf_no, nice):
        self.conf_no = conf_no
        self.nice = nice
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.nice)

# get-marks [23] (1) Recommended
class ReqGetMarks(Request):
    CALL_NO = Requests.GET_MARKS
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> string
        return conn.parse_array(Mark)

# mark-text-old [24] (1) Obsolete (4) Use mark-text/unmark-text (72/73)

# get-text [25] (1) Recommended
class ReqGetText(Request):
    CALL_NO = Requests.GET_TEXT
    def __init__(self, text_no, start_char=0, end_char=MAX_TEXT_SIZE):
        self.text_no = text_no
        self.start_char = start_char
        self.end_char = end_char

    def get_request(self):
        return ("%d %d %d" % (self.text_no, self.start_char,
                              self.end_char)).encode('latin1')
    
    def parse_response(self, conn):
        # --> string
        return conn.parse_string()
    
# get-text-stat-old [26] (1) Obsolete (10) Use get-text-stat (90)

# mark-as-read [27] (1) Recommended
class ReqMarkAsRead(Request):
    CALL_NO = Requests.MARK_AS_READ
    def __init__(self, conf_no, texts):
        self.conf_no = conf_no
        self.texts = texts

    def get_request(self):
        return ("%d %s" % (self.conf_no,
                           array_of_int_to_string(self.texts))).encode('latin1')
                      
# create-text-old [28] (1) Obsolete (10) Use create-text (86)

# delete-text [29] (1) Recommended
class ReqDeleteText(Request):
    CALL_NO = Requests.DELETE_TEXT
    def __init__(self, text_no):
        self.text_no = text_no
        
    def get_request(self):
        return "%d" % (self.text_no,)

# add-recipient [30] (1) Recommended
class ReqAddRecipient(Request):
    CALL_NO = Requests.ADD_RECIPIENT
    def __init__(self, text_no, conf_no, recpt_type=MIR_TO):
        self.text_no = text_no
        self.conf_no = conf_no
        self.recpt_type = recpt_type
        
    def get_request(self):
        return "%d %d %d" % (self.text_no, self.conf_no, self.recpt_type)

# sub-recipient [31] (1) Recommended
class ReqSubRecipient(Request):
    CALL_NO = Requests.SUB_RECIPIENT
    def __init__(self, text_no, conf_no):
        self.text_no = text_no
        self.conf_no = conf_no
        
    def get_request(self):
        return "%d %d" % (self.text_no, self.conf_no)

# add-comment [32] (1) Recommended
class ReqAddComment(Request):
    CALL_NO = Requests.ADD_COMMENT
    def __init__(self, text_no, comment_to):
        self.text_no = text_no
        self.comment_to = comment_to
        
    def get_request(self):
        return "%d %d" % (self.text_no, self.comment_to)

# sub-comment [33] (1) Recommended
class ReqSubComment(Request):
    CALL_NO = Requests.SUB_COMMENT
    def __init__(self, text_no, comment_to):
        self.text_no = text_no
        self.comment_to = comment_to
        
    def get_request(self):
        return "%d %d" % (self.text_no, self.comment_to)

# get-map [34] (1) Obsolete (10) Use local-to-global (103)
class ReqGetMap(Request):
    CALL_NO = Requests.GET_MAP
    def __init__(self, conf_no, first_local_no, no_of_texts):
        self.conf_no = conf_no
        self.first_local_no = first_local_no
        self.no_of_texts = no_of_texts
        
    def get_request(self):
        return "%d %d %d" % (self.conf_no, self.first_local_no, self.no_of_texts)

    def parse_response(self, conn):
	# --> Text-List
        return conn.parse_object(TextList)

# get-time [35] (1) Recommended
class ReqGetTime(Request):
    CALL_NO = Requests.GET_TIME
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> Time
        return conn.parse_object(Time)
    
# get-info-old [36] (1) Obsolete (10) Use get-info (94)

# add-footnote [37] (1) Recommended
class ReqAddFootnote(Request):
    CALL_NO = Requests.ADD_FOOTNOTE
    def __init__(self, text_no, footnote_to):
        self.text_no = text_no
        self.footnote_to = footnote_to
        
    def get_request(self):
        return "%d %d" % (self.text_no, self.footnote_to)

# sub-footnote [38] (1) Recommended
class ReqSubFootnote(Request):
    CALL_NO = Requests.SUB_FOOTNOTE
    def __init__(self, text_no, footnote_to):
        self.text_no = text_no
        self.footnote_to = footnote_to
        
    def get_request(self):
        return "%d %d" % (self.text_no, self.footnote_to)

# who-is-on-old [39] (1) Obsolete (9) Use get-static-session-info (84) and
#                                         who-is-on-dynamic (83)

# set-unread [40] (1) Recommended
class ReqSetUnread(Request):
    CALL_NO = Requests.SET_UNREAD
    def __init__(self, conf_no, no_of_unread):
        self.conf_no = conf_no
        self.no_of_unread = no_of_unread
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.no_of_unread)

# set-motd-of-lyskom [41] (1) Recommended
class ReqSetMoTDOfLysKOM(Request):
    CALL_NO = Requests.SET_MOTD_OF_LYSKOM
    def __init__(self, text_no):
        self.text_no = text_no
        
    def get_request(self):
        return "%d" % (self.text_no,)

# enable [42] (1) Recommended
class ReqEnable(Request):
    CALL_NO = Requests.ENABLE
    def __init__(self, level):
        self.level = level
        
    def get_request(self):
        return "%d" % (self.level,)

# sync-kom [43] (1) Recommended
class ReqSyncKOM(Request):
    CALL_NO = Requests.SYNC_KOM
    def get_request(self):
        return ""

# shutdown-kom [44] (1) Recommended
class ReqShutdownKOM(Request):
    CALL_NO = Requests.SHUTDOWN_KOM
    def __init__(self, exit_val):
        self.exit_val = exit_val
        
    def get_request(self):
        return "%d" % (self.exit_val,)

# broadcast [45] (1) Obsolete (1) Use send-message (53)
# get-membership-old [46] (1) Obsolete (10) Use get-membership (99)
# get-created-texts [47] (1) Obsolete (10) Use map-created-texts (104)
# get-members-old [48] (1) Obsolete (10) Use get-members (101)

# get-person-stat [49] (1) Recommended
class ReqGetPersonStat(Request):
    CALL_NO = Requests.GET_PERSON_STAT
    def __init__(self, person_no):
        self.person_no = person_no
        
    def get_request(self):
        return "%d" % (self.person_no,)

    def parse_response(self, conn):
        # --> Person
        return conn.parse_object(Person)

# get-conf-stat-old [50] (1) Obsolete (10) Use get-conf-stat (91)

# who-is-on [51] (1) Obsolete (9)  Use who-is-on-dynamic (83) and
#                                      get-static-session-info (84)

# get-unread-confs [52] (1) Recommended
class ReqGetUnreadConfs(Request):
    CALL_NO = Requests.GET_UNREAD_CONFS
    def __init__(self, person_no):
        self.person_no = person_no
        
    def get_request(self):
        return ("%d" % (self.person_no,)).encode('latin1')

    def parse_response(self, conn):
        # --> ARRAY Conf-No
        return conn.parse_array_of_int()

# send-message [53] (1) Recommended
class ReqSendMessage(Request):
    CALL_NO = Requests.SEND_MESSAGE
    def __init__(self, conf_no, message):
        self.conf_no = conf_no
        self.message = message
        
    def get_request(self):
        return ("%d %dH%s" % (self.conf_no, len(self.message), 
                              self.message)).encode('latin1')

# get-session-info [54] (1) Obsolete (9) Use who-is-on-dynamic (83)

# disconnect [55] (1) Recommended
class ReqDisconnect(Request):
    CALL_NO = Requests.DISCONNECT
    def __init__(self, session_no):
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)

# who-am-i [56] (1) Recommended
class ReqWhoAmI(Request):
    CALL_NO = Requests.WHO_AM_I
    def get_request(self):
        return ""
        
    def parse_response(self, conn):
        # --> Session-No
        return conn.parse_int()

# set-user-area [57] (2) Recommended
class ReqSetUserArea(Request):
    CALL_NO = Requests.SET_USER_AREA
    def __init__(self, person_no, user_area):
        self.person_no = person_no
        self.user_area = user_area
        
    def get_request(self):
        return "%d %d" % (self.person_no, self.user_area)

# get-last-text [58] (3) Recommended
class ReqGetLastText(Request):
    CALL_NO = Requests.GET_LAST_TEXT
    def __init__(self, before):
        self.before = before
        
    def get_request(self):
        return "%s" % (self.before.to_string(),)
        
    def parse_response(self, conn):
        # --> Text-No
        return conn.parse_int()

# create-anonymous-text-old [59] (3) Obsolete (10)
#                                    Use create-anonymous-text (87)

# find-next-text-no [60] (3) Recommended
class ReqFindNextTextNo(Request):
    CALL_NO = Requests.FIND_NEXT_TEXT_NO
    def __init__(self, start):
        self.start = start
        
    def get_request(self):
        return "%d" % (self.start,)
        
    def parse_response(self, conn):
        # --> Text-No
        return conn.parse_int()

# find-previous-text-no [61] (3) Recommended
class ReqFindPreviousTextNo(Request):
    CALL_NO = Requests.FIND_PREVIOUS_TEXT_NO
    def __init__(self, start):
        self.start = start
        
    def get_request(self):
        return "%d" % (self.start,)
        
    def parse_response(self, conn):
        # --> Text-No
        return conn.parse_int()

# login [62] (4) Recommended
class ReqLogin(Request):
    CALL_NO = Requests.LOGIN
    def __init__(self, person_no, password, invisible=1):
        self.person_no = person_no
        self.password = password
        self.invisible = invisible
        
    def get_request(self):
        return ("%d %dH%s %d" %
                (self.person_no, len(self.password), self.password, 
                 self.invisible)).encode('latin1')

# who-is-on-ident [63] (4) Obsolete (9) Use who-is-on-dynamic (83) and
#                                           get-static-session-info (84)
# get-session-info-ident [64] (4) Obsolete (9) Use who-is-on-dynamic (83) and
#                                              get-static-session-info (84)
# re-lookup-person [65] (5) Obsolete (7) Use re-z-lookup (74)
# re-lookup-conf [66] (5) Obsolete (7) Use re-z-lookup (74)
# lookup-person [67] (6) Obsolete (7) Use lookup-z-name (76)
# lookup-conf [68] (6) Obsolete (7) Use lookup-z-name (76)

# set-client-version [69] (6) Recommended
class ReqSetClientVersion(Request):
    CALL_NO = Requests.SET_CLIENT_VERSION
    def __init__(self, client_name, client_version):
        self.client_name = client_name
        self.client_version = client_version
        
    def get_request(self):
        return ("%dH%s %dH%s" % (
                len(self.client_name), self.client_name,
                len(self.client_version), self.client_version)).encode('latin1')

# get-client-name [70] (6) Recommended
class ReqGetClientName(Request):
    CALL_NO = Requests.GET_CLIENT_NAME
    def __init__(self, session_no):
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)
        
    def parse_response(self, conn):
        # --> Hollerith
        return conn.parse_string()

# get-client-version [71] (6) Recommended
class ReqGetClientVersion(Request):
    CALL_NO = Requests.GET_CLIENT_VERSION
    def __init__(self, session_no):
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)
        
    def parse_response(self, conn):
        # --> Hollerith
        return conn.parse_string()

# mark-text [72] (4) Recommended
class ReqMarkText(Request):
    CALL_NO = Requests.MARK_TEXT
    def __init__(self, text_no, mark_type):
        self.text_no = text_no
        pass
        
    def get_request(self):
        return "%d %d" % (self.text_no, self.mark_type)

# unmark-text [73] (6) Recommended
class ReqUnmarkText(Request):
    CALL_NO = Requests.UNMARK_TEXT
    def __init__(self, text_no):
        self.text_no = text_no
        
    def get_request(self):
        return "%d" % (self.text_no,)

# re-z-lookup [74] (7) Recommended
class ReqReZLookup(Request):
    CALL_NO = Requests.RE_Z_LOOKUP
    def __init__(self, regexp, want_pers=0, want_confs=0):
        self.regexp = regexp
        self.want_pers = want_pers
        self.want_confs = want_confs
        
    def get_request(self):
        return "%dH%s %d %d" % (len(self.regexp), self.regexp,
                                self.want_pers, self.want_confs)

    def parse_response(self, conn):
        # --> ARRAY ConfZInfo
        return conn.parse_array(ConfZInfo)

# get-version-info [75] (7) Recommended
class ReqGetVersionInfo(Request):
    CALL_NO = Requests.GET_VERSION_INFO
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> Version-Info
        return conn.parse_object(VersionInfo)

# lookup-z-name [76] (7) Recommended
class ReqLookupZName(Request):
    CALL_NO = Requests.LOOKUP_Z_NAME
    def __init__(self, name, want_pers=0, want_confs=0):
        self.name = name
        self.want_pers = want_pers
        self.want_confs = want_confs
        
    def get_request(self):
        return ("%dH%s %d %d" % (len(self.name), self.name,
                                 self.want_pers, self.want_confs)).encode('latin1')

    def parse_response(self, conn):
        # --> ARRAY ConfZInfo
        return conn.parse_array(ConfZInfo)

# set-last-read [77] (8) Recommended
class ReqSetLastRead(Request):
    CALL_NO = Requests.SET_LAST_READ
    def __init__(self, conf_no, last_read):
        self.conf_no = conf_no
        self.last_read = last_read
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.last_read)

# get-uconf-stat [78] (8) Recommended
class ReqGetUconfStat(Request):
    CALL_NO = Requests.GET_UCONF_STAT
    def __init__(self, conf_no):
        self.conf_no = conf_no
        
    def get_request(self):
        return ("%d" % (self.conf_no,)).encode('latin1')

    def parse_response(self, conn):
        # --> UConference
        return conn.parse_object(UConference)

# set-info [79] (9) Recommended
class ReqSetInfo(Request):
    CALL_NO = Requests.SET_INFO
    def __init__(self, info):
        self.info = info
        
    def get_request(self):
        return "%s" % (self.info.to_string(),)

# accept-async [80] (9) Recommended
class ReqAcceptAsync(Request):
    CALL_NO = Requests.ACCEPT_ASYNC
    def __init__(self, request_list):
        self.request_list = request_list
        
    def get_request(self):
        return ("%s" % (array_of_int_to_string(self.request_list),)).encode('latin1')

# query-async [81] (9) Recommended
class ReqQueryAsync(Request):
    CALL_NO = Requests.QUERY_ASYNC
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> ARRAY INT32
        return conn.parse_array_of_int()

# user-active [82] (9) Recommended
class ReqUserActive(Request):
    CALL_NO = Requests.USER_ACTIVE
    def get_request(self):
        return ""

# who-is-on-dynamic [83] (9) Recommended
class ReqWhoIsOnDynamic(Request):
    CALL_NO = Requests.WHO_IS_ON_DYNAMIC
    def __init__(self, want_visible=1, want_invisible=0, active_last=0):
        self.want_visible = want_visible
        self.want_invisible = want_invisible
        self.active_last = active_last
        
    def get_request(self):
        return "%d %d %d" % (self.want_visible, self.want_invisible, self.active_last)

    def parse_response(self, conn):
        # --> ARRAY Dynamic-Session-Info
        return conn.parse_array(DynamicSessionInfo)

# get-static-session-info [84] (9) Recommended
class ReqGetStaticSessionInfo(Request):
    CALL_NO = Requests.GET_STATIC_SESSION_INFO
    def __init__(self, session_no):
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)

    def parse_response(self, conn):
        # --> Static-Session-Info
        return conn.parse_object(StaticSessionInfo)

# get-collate-table [85] (10) Recommended
class ReqGetCollateTable(Request):
    CALL_NO = Requests.GET_COLLATE_TABLE
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> HOLLERITH
        return conn.parse_string()

# create-text [86] (10) Recommended
class ReqCreateText(Request):
    CALL_NO = Requests.CREATE_TEXT
    def __init__(self, text, misc_info, aux_items=[]):
        self.text = text
        self.misc_info = misc_info
        self.aux_items = aux_items
        
    def get_request(self):
        return "%dH%s %s %s" % (len(self.text), self.text,
                                self.misc_info.to_string(),
                                array_to_string(self.aux_items))
        
    def parse_response(self, conn):
        # --> Text-No
        return conn.parse_int()

# create-anonymous-text [87] (10) Recommended
class ReqCreateAnonymousText(Request):
    CALL_NO = Requests.CREATE_ANONYMOUS_TEXT
    def __init__(self, text, misc_info, aux_items=[]):
        self.text = text
        self.misc_info = misc_info
        self.aux_items = aux_items
        
    def get_request(self):
        return "%dH%s %s %s" % (len(self.text), self.text,
                                self.misc_info.to_string(),
                                array_to_string(self.aux_items))
        
    def parse_response(self, conn):
        # --> Text-No
        return conn.parse_int()

# create-conf [88] (10) Recommended
class ReqCreateConf(Request):
    CALL_NO = Requests.CREATE_CONF
    def __init__(self, name, conf_type, aux_items=[]):
        self.name = name
        self.conf_type = conf_type
        self.aux_items = aux_items
        
    def get_request(self):
        return "%dH%s %s %s" % (len(self.name), self.name,
                                self.conf_type.to_string(),
                                array_to_string(self.aux_items))
        
    def parse_response(self, conn):
        # --> Conf-No
        return conn.parse_int()

# create-person [89] (10) Recommended
class ReqCreatePerson(Request):
    CALL_NO = Requests.CREATE_PERSON
    def __init__(self, name, passwd, flags, aux_items=[]):
        self.name = name
        self.passwd = passwd
        self.flags = flags
        self.aux_items = aux_items
        
    def get_request(self):
        return "%dH%s %dH%s %s %s" % (len(self.name), self.name,
                                      len(self.passwd), self.passwd,
                                      self.flags.to_string(),
                                      array_to_string(self.aux_items))
        
    def parse_response(self, conn):
        # --> Pers-No
        return conn.parse_int()

# get-text-stat [90] (10) Recommended
class ReqGetTextStat(Request):
    CALL_NO = Requests.GET_TEXT_STAT
    def __init__(self, text_no):
        self.text_no = text_no
        
    def get_request(self):
        return ("%d" % (self.text_no,)).encode('latin1')

    def parse_response(self, conn):
        # --> TextStat
        return conn.parse_object(TextStat)

# get-conf-stat [91] (10) Recommended
class ReqGetConfStat(Request):
    CALL_NO = Requests.GET_CONF_STAT
    def __init__(self, conf_no):
        self.conf_no = conf_no
        
    def get_request(self):
        return ("%d" % (self.conf_no,)).encode('latin1')

    def parse_response(self, conn):
        # --> Conference
        return conn.parse_object(Conference)

# modify-text-info [92] (10) Recommended
class ReqModifyTextInfo(Request):
    CALL_NO = Requests.MODIFY_TEXT_INFO
    def __init__(self, text_no, delete, add):
        self.text_no = text_no
        self.delete = delete
        self.add = add
        
    def get_request(self):
        return "%d %s %s" % (self.text_no,
                             array_of_int_to_string(self.delete),
                             array_to_string(self.add))

# modify-conf-info [93] (10) Recommended
class ReqModifyConfInfo(Request):
    CALL_NO = Requests.MODIFY_CONF_INFO
    def __init__(self, conf_no, delete, add):
        self.conf_no = conf_no
        self.delete = delete
        self.add = add
        
    def get_request(self):
        return "%d %s %s" % (self.conf_no,
                             array_of_int_to_string(self.delete),
                             array_to_string(self.add))

# get-info [94] (10) Recommended
class ReqGetInfo(Request):
    CALL_NO = Requests.GET_INFO
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> Info
        return conn.parse_object(Info)

# modify-system-info [95] (10) Recommended
class ReqModifySystemInfo(Request):
    CALL_NO = Requests.MODIFY_SYSTEM_INFO
    def __init__(self, delete, add):
        self.delete = delete
        self.add = add
        
    def get_request(self):
        return "%s %s" % (array_of_int_to_string(self.delete),
                          array_to_string(self.add))

# query-predefined-aux-items [96] (10) Recommended
class ReqQueryPredefinedAuxItems(Request):
    CALL_NO = Requests.QUERY_PREDEFINED_AUX_ITEMS
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> ARRAY INT32
        return conn.parse_array_of_int()

# set-expire [97] (10) Experimental
class ReqSetExpire(Request):
    CALL_NO = Requests.SET_EXPIRE
    def __init__(self, conf_no, expire):
        self.conf_no = conf_no
        self.expire = expire
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.expire)

# query-read-texts-10 [98] (10) Obsolete (11) Use query-read-texts (107)
class ReqQueryReadTexts10(Request):
    CALL_NO = Requests.QUERY_READ_TEXTS_10
    def __init__(self, person_no, conf_no):
        self.person_no = person_no
        self.conf_no = conf_no
        
    def get_request(self):
        return "%d %d" % (self.person_no, self.conf_no)

    def parse_response(self, conn):
        # --> Membership10
        return conn.parse_object(Membership10)

# get-membership-10 [99] (10) Obsolete (11) Use get-membership (108)

class ReqGetMembership10(Request):
    def __init__(self, person_no, first, no_of_confs, want_read_texts):
        self.person_no = person_no
        self.first = first
        self.no_of_confs = no_of_confs
        self.want_read_texts = want_read_texts
        
    def get_request(self):
        return "%d %d %d %d" % (self.person_no, self.first,
                                self.no_of_confs, self.want_read_texts)

    def parse_response(self, conn):
        # --> ARRAY Membership10
        return conn.parse_array(Membership10)

# add-member [100] (10) Recommended
class ReqAddMember(Request):
    CALL_NO = Requests.ADD_MEMBER
    def __init__(self, conf_no, person_no, priority, where, membership_type):
        self.conf_no = conf_no
        self.person_no = person_no
        self.priority = priority
        self.where = where
        self.membership_type = membership_type
        
    def get_request(self):
        return "%d %d %d %d %s" % (self.conf_no, self.person_no,
                                   self.priority, self.where,
                                   self.membership_type.to_string())

# get-members [101] (10) Recommended
class ReqGetMembers(Request):
    CALL_NO = Requests.GET_MEMBERS
    def __init__(self, conf_no, first, no_of_members):
        self.conf_no = conf_no
        self.first = first
        self.no_of_members = no_of_members
        
        
    def get_request(self):
        return "%d %d %d" % (self.conf_no, self.first, self.no_of_members)

    def parse_response(self, conn):
        # --> ARRAY Member
        return conn.parse_array(Member)

# set-membership-type [102] (10) Recommended
class ReqSetMembershipType(Request):
    CALL_NO = Requests.SET_MEMBERSHIP_TYPE
    def __init__(self, person_no, conf_no, membership_type):
        self.person_no = person_no
        self.conf_no = conf_no
        self.membership_type = membership_type
        
    def get_request(self):
        return "%d %d %s" % (self.person_no, self.conf_no, self.membership_type.to_string())

# local-to-global [103] (10) Recommended
class ReqLocalToGlobal(Request):
    CALL_NO = Requests.LOCAL_TO_GLOBAL
    def __init__(self, conf_no, first_local_no, no_of_existing_texts):
        self.conf_no = conf_no
        self.first_local_no = first_local_no
        self.no_of_existing_texts = no_of_existing_texts
        
    def get_request(self):
        return ("%d %d %d" % (self.conf_no, self.first_local_no, 
                              self.no_of_existing_texts)).encode('latin1')

    def parse_response(self, conn):
        # --> Text-Mapping
        return conn.parse_object(TextMapping)

# map-created-texts [104] (10) Recommended
class ReqMapCreatedTexts(Request):
    CALL_NO = Requests.MAP_CREATED_TEXTS
    def __init__(self, author, first_local_no, no_of_existing_texts):
        self.author = author
        self.first_local_no = first_local_no
        self.no_of_existing_texts = no_of_existing_texts
        
    def get_request(self):
        return "%d %d %d" % (self.author, self.first_local_no, self.no_of_existing_texts)

    def parse_response(self, conn):
        # --> Text-Mapping
        return conn.parse_object(TextMapping)

# set-keep-commented [105] (11) Recommended (10) Experimental
class ReqSetKeepCommented(Request):
    CALL_NO = Requests.SET_KEEP_COMMENTED
    def __init__(self, conf_no, keep_commented):
        self.conf_no = conf_no
        self.keep_commented = keep_commented
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.keep_commented)

# set-pers-flags [106] (10) Recommended

class ReqSetPersFlags(Request):
    def __init__(self, person_no, flags):
        self.person_no = person_no
        self.flags = flags
        
    def get_request(self):
        return "%d %s" % (self.person_no, self.flags.to_string())

### --- New in protocol version 11 ---

# query-read-texts [107] (11) Recommended
class ReqQueryReadTexts11(Request):
    CALL_NO = Requests.QUERY_READ_TEXTS
    def __init__(self, person_no, conf_no,
                 want_read_ranges, max_ranges):
        self.person_no = person_no
        self.conf_no = conf_no
        self.want_read_ranges = want_read_ranges
        self.max_ranges = max_ranges
        
    def get_request(self):
        return ("%d %d %d %d" % (self.person_no, self.conf_no,
                                 self.want_read_ranges,
                                 self.max_ranges)).encode('latin1')

    def parse_response(self, conn):
        # --> Membership11
        return conn.parse_object(Membership11)

ReqQueryReadTexts = ReqQueryReadTexts11

# get-membership [108] (11) Recommended
class ReqGetMembership11(Request):
    CALL_NO = Requests.GET_MEMBERSHIP
    def __init__(self, person_no, first, no_of_confs,
                 want_read_ranges, max_ranges):
        self.person_no = person_no
        self.first = first
        self.no_of_confs = no_of_confs
        self.want_read_ranges = want_read_ranges
        self.max_ranges = max_ranges
        
    def get_request(self):
        return "%d %d %d %d %d" % (self.person_no,
                                   self.first, self.no_of_confs,
                                   self.want_read_ranges, self.max_ranges)

    def parse_response(self, conn):
        # --> ARRAY Membership11
        return conn.parse_array(Membership11)

ReqGetMembership = ReqGetMembership11

# mark-as-unread [109] (11) Recommended
class ReqMarkAsUnread(Request):
    CALL_NO = Requests.MARK_AS_UNREAD
    def __init__(self, conf_no, text_no):
        self.conf_no = conf_no
        self.text_no = text_no
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.text_no)

# set-read-ranges [110] (11) Recommended
class ReqSetReadRanges(Request):
    CALL_NO = Requests.SET_READ_RANGES
    def __init__(self, conf_no, read_ranges):
        self.conf_no = conf_no
        self.read_ranges = read_ranges
        
    def get_request(self):
        return "%s %s" % (self.conf_no, array_to_string(self.read_ranges))

# get-stats-description [111] (11) Recommended
class ReqGetStatsDescription(Request):
    CALL_NO = Requests.GET_STATS_DESCRIPTION
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> Stats-Description
        return conn.parse_object(StatsDescription)

# get-stats [112] (11) Recommended
class ReqGetStats(Request):
    CALL_NO = Requests.GET_STATS
    def __init__(self, what):
        pass
        
    def get_request(self):
        return "%dH%s" % (len(self.what), self.what)

    def parse_response(self, conn):
        # --> ARRAY Stats
        return conn.parse_array(Stats)

# get-boottime-info [113] (11) Recommended
class ReqGetBoottimeInfo(Request):
    CALL_NO = Requests.GET_BOOTTIME_INFO
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> Static-Server-Info
        return conn.parse_object(StaticServerInfo)

# first-unused-conf-no [114] (11) Recommended
class ReqFirstUnusedConfNo(Request):
    CALL_NO = Requests.FIRST_UNUSED_CONF_NO
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> Conf-No
        return conn.parse_int()

# first-unused-text-no [115] (11) Recommended
class ReqFirstUnusedTextNo(Request):
    CALL_NO = Requests.FIRST_UNUSED_TEXT_NO
    def get_request(self):
        return ""

    def parse_response(self, conn):
        # --> Text-No
        return conn.parse_int()

# find-next-conf-no [116] (11) Recommended
class ReqFindNextConfNo(Request):
    CALL_NO = Requests.FIND_NEXT_CONF_NO
    def __init__(self, conf_no):
        self.conf_no = conf_no
        pass
        
    def get_request(self):
        return "%d" % (self.conf_no,)

    def parse_response(self, conn):
        # --> Conf-No
        return conn.parse_int()

# find-previous-conf-no [117] (11) Recommended
class ReqFindPreviousConfNo(Request):
    CALL_NO = Requests.FIND_PREVIOUS_CONF_NO
    def __init__(self, conf_no):
        self.conf_no = conf_no
        pass
        
    def get_request(self):
        return "%d" % (self.conf_no,)

    def parse_response(self, conn):
        # --> Conf-No
        return conn.parse_int()

# get-scheduling [118] (11) Experimental
class ReqGetScheduling(Request):
    CALL_NO = Requests.GET_SCHEDULING
    def __init__(self, session_no):
        self.session_no = session_no
        pass
        
    def get_request(self):
        return "%d" % (self.session_no,)

    def parse_response(self, conn):
        # --> SchedulingInfo
        return conn.parse_object(SchedulingInfo)

# set-scheduling [119] (11) Experimental
class ReqSetScheduling(Request):
    CALL_NO = Requests.SET_SCHEDULING
    def __init__(self, session_no, priority, weight):
        self.session_no = session_no
        self.prority = priority
        self.weight = weight
        
    def get_request(self):
        return "%d %d %d" % (self.session_no, self.priority, self.weight)

# set-connection-time-format [120] (11) Recommended
class ReqSetConnectionTimeFormat(Request):
    CALL_NO = Requests.SET_CONNECTION_TIME_FORMAT
    def __init__(self, use_utc):
        self.use_utc = use_utc
        
    def get_request(self):
        return "%d" % (self.use_utc,)

# local-to-global-reverse [121] (11) Recommended
class ReqLocalToGlobalReverse(Request):
    CALL_NO = Requests.LOCAL_TO_GLOBAL_REVERSE
    def __init__(self, conf_no, local_no_ceiling, no_of_existing_texts):
        self.conf_no = conf_no
        self.local_no_ceiling = local_no_ceiling
        self.no_of_existing_texts = no_of_existing_texts
        
    def get_request(self):
        return "%d %d %d" % (self.conf_no, self.local_no_ceiling, self.no_of_existing_texts)

    def parse_response(self, conn):
        # --> Text-Mapping
        return conn.parse_object(TextMapping)

# map-created-texts-reverse [122] (11) Recommended
class ReqMapCreatedTextsReverse(Request):
    CALL_NO = 122
    def __init__(self, author, local_no_ceiling, no_of_existing_texts):
        self.author = author
        self.local_no_ceiling = local_no_ceiling
        self.no_of_existing_texts = no_of_existing_texts
        
    def get_request(self):
        return "%d %d %d" % (self.author, self.local_no_ceiling, self.no_of_existing_texts)

    def parse_response(self, conn):
        # --> Text-Mapping
        return conn.parse_object(TextMapping)


request_dict = {
}


class AsyncMessages(object):
    NEW_TEXT_OLD = 0
    NEW_NAME = 5
    I_AM_ON = 6
    SYNC_DB = 7
    LEAVE_CONF = 8
    LOGIN = 9
    REJECTED_CONNECTION = 11
    SEND_MESSAGE = 12
    LOGOUT = 13
    DELETED_TEXT = 14
    NEW_TEXT = 15
    NEW_RECIPIENT = 16
    SUB_RECIPIENT = 17
    NEW_MEMBERSHIP = 18
    NEW_USER_AREA = 19
    NEW_PRESENTATION = 20
    NEW_MOTD = 21
    TEXT_AUX_CHANGED = 22


#
# Classes for asynchronous messages from the server are all
# subclasses of AsyncMessage.
#

class AsyncMessage:
    MSG_NO = None
    pass

# async-new-text-old [0] (1) Obsolete (10) <DEFAULT>
class AsyncNewTextOld(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_TEXT_OLD
    def parse(self, c):
        self.text_no = c.parse_int()
        self.text_stat = c.parse_old_object(TextStat)

# async-i-am-off [1] (1) Obsolete
# async-i-am-on-onsolete [2] (1) Obsolete

# async-new-name [5] (1) Recommended <DEFAULT>
class AsyncNewName(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_NAME
    def parse(self, c):
        self.conf_no = c.parse_int()
        self.old_name = c.parse_string()
        self.new_name = c.parse_string()

# async-i-am-on [6] Recommended
class AsyncIAmOn(AsyncMessage):
    MSG_NO = AsyncMessages.I_AM_ON
    def parse(self, c):
        self.info = c.parse_object(WhoInfo)

# async-sync-db [7] (1) Recommended <DEFAULT>
class AsyncSyncDB(AsyncMessage):
    MSG_NO = AsyncMessages.SYNC_DB
    def parse(self, c):
        pass

# async-leave-conf [8] (1) Recommended <DEFAULT>
class AsyncLeaveConf(AsyncMessage):
    MSG_NO = AsyncMessages.LEAVE_CONF
    def parse(self, c):
        self.conf_no = c.parse_int()

# async-login [9] (1) Recommended <DEFAULT>
class AsyncLogin(AsyncMessage):
    MSG_NO = AsyncMessages.LOGIN
    def parse(self, c):
        self.person_no = c.parse_int()
        self.session_no = c.parse_int()

# async-broadcast [10] Obsolete

# async-rejected-connection [11] (1) Recommended <DEFAULT>
class AsyncRejectedConnection(AsyncMessage):
    MSG_NO = AsyncMessages.REJECTED_CONNECTION
    def parse(self, c):
        pass

# async-send-message [12] (1) Recommended <DEFAULT>
class AsyncSendMessage(AsyncMessage):
    MSG_NO = AsyncMessages.SEND_MESSAGE
    def parse(self, c):
        self.recipient = c.parse_int()
        self.sender = c.parse_int()
        self.message = c.parse_string()

# async-logout [13] (1) Recommended <DEFAULT>
class AsyncLogout(AsyncMessage):
    MSG_NO = AsyncMessages.LOGOUT
    def parse(self, c):
        self.person_no = c.parse_int()
        self.session_no = c.parse_int()

# async-deleted-text [14] (10) Recommended
class AsyncDeletedText(AsyncMessage):
    MSG_NO = AsyncMessages.DELETED_TEXT
    def parse(self, c):
        self.text_no = c.parse_int()
        self.text_stat = c.parse_object(TextStat)

# async-new-text [15] (10) Recommended
class AsyncNewText(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_TEXT
    def parse(self, c):
        self.text_no = c.parse_int()
        self.text_stat = c.parse_object(TextStat)

# async-new-recipient [16] (10) Recommended
class AsyncNewRecipient(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_RECIPIENT
    def parse(self, c):
        self.text_no = c.parse_int()
        self.conf_no = c.parse_int()
        self.type = c.parse_int()

# async-sub-recipient [17] (10) Recommended
class AsyncSubRecipient(AsyncMessage):
    MSG_NO = AsyncMessages.SUB_RECIPIENT
    def parse(self, c):
        self.text_no = c.parse_int()
        self.conf_no = c.parse_int()
        self.type = c.parse_int()

# async-new-membership [18] (10) Recommended
class AsyncNewMembership(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_MEMBERSHIP
    def parse(self, c):
        self.person_no = c.parse_int()
        self.conf_no = c.parse_int()

# async-new-user-area [19] (11) Recommended
class AsyncNewUserArea(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_USER_AREA
    def parse(self, c):
        self.person_no = c.parse_int()
        self.old_user_area = c.parse_int()
        self.new_user_area = c.parse_int()

# async-new-presentation [20] (11) Recommended
class AsyncNewPresentation(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_PRESENTATION
    def parse(self, c):
        self.conf_no = c.parse_int()
        self.old_presentation = c.parse_int()
        self.new_presentation = c.parse_int()

# async-new-motd [21] (11) Recommended
class AsyncNewMotd(AsyncMessage):
    MSG_NO = AsyncMessages.NEW_MOTD
    def parse(self, c):
        self.conf_no = c.parse_int()
        self.old_motd = c.parse_int()
        self.new_motd = c.parse_int()

# async-text-aux-changed [22] (11) Recommended
class AsyncTextAuxChanged(AsyncMessage):
    MSG_NO = AsyncMessages.TEXT_AUX_CHANGED
    def parse(self, c):
        self.text_no = c.parse_int()
        self.deleted = c.parse_array(AuxItem)
        self.added = c.parse_array(AuxItem)

async_dict = {
    AsyncMessages.NEW_TEXT_OLD: AsyncNewTextOld,
    AsyncMessages.NEW_NAME: AsyncNewName,
    AsyncMessages.I_AM_ON: AsyncIAmOn,
    AsyncMessages.SYNC_DB: AsyncSyncDB,
    AsyncMessages.LEAVE_CONF: AsyncLeaveConf,
    AsyncMessages.LOGIN: AsyncLogin,
    AsyncMessages.REJECTED_CONNECTION: AsyncRejectedConnection,
    AsyncMessages.SEND_MESSAGE: AsyncSendMessage,
    AsyncMessages.LOGOUT: AsyncLogout,
    AsyncMessages.DELETED_TEXT: AsyncDeletedText,
    AsyncMessages.NEW_TEXT: AsyncNewText,
    AsyncMessages.NEW_RECIPIENT: AsyncNewRecipient,
    AsyncMessages.SUB_RECIPIENT: AsyncSubRecipient,
    AsyncMessages.NEW_MEMBERSHIP: AsyncNewMembership,
    AsyncMessages.NEW_USER_AREA: AsyncNewUserArea,
    AsyncMessages.NEW_PRESENTATION: AsyncNewPresentation,
    AsyncMessages.NEW_MOTD: AsyncNewMotd,
    AsyncMessages.TEXT_AUX_CHANGED: AsyncTextAuxChanged,
    }

#
# CLASSES for KOM data types
#

# TIME

class Time:
    """Assumes all dates are in UTC timezone.
    """
    def __init__(self, ptime = None):
        if ptime is None:
            self.seconds = 0
            self.minutes = 0
            self.hours = 0 
            self.day = 0
            self.month = 0 # 0 .. 11 
            self.year = 0 # no of years since 1900
            self.day_of_week = 0 # 0 = Sunday ... 6 = Saturday
            self.day_of_year = 0 # 0 ... 365
            self.is_dst = 0
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

    def parse(self, c):
        self.seconds = c.parse_int()
        self.minutes = c.parse_int()
        self.hours = c.parse_int()
        self.day = c.parse_int()
        self.month = c.parse_int()
        self.year = c.parse_int()
        self.day_of_week = c.parse_int()
        self.day_of_year = c.parse_int()
        self.is_dst = c.parse_int()

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
        return "<Time %s>" % self.to_date_and_time()

# RESULT FROM LOOKUP-Z-NAME

class ConfZInfo:
    def parse(self, c):
        self.name = c.parse_string()
        self.type = c.parse_old_object(ConfType)
        self.conf_no = c.parse_int()

    def __repr__(self):
        return "<ConfZInfo %d: %s>" % \
            (self.conf_no, self.name)

# RAW MISC-INFO (AS IT IS IN PROTOCOL A)

class RawMiscInfo:
    def parse(self, c):
        self.type = c.parse_int()
        if self.type in [MI_REC_TIME, MI_SENT_AT]:
            self.data = c.parse_object(Time)
        else:
            self.data = c.parse_int()

    def __repr__(self):
        return "<MiscInfo %d: %s>" % (self.type, self.data)

# COOKED MISC-INFO (MORE TASTY)
# N.B: This class represents the whole array, not just one item

class MIRecipient:
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

class MICommentTo:
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

class MICommentIn:
    def __init__(self, type = MIC_COMMENT, text_no = 0):
        self.type = type
        self.text_no = text_no

    def get_tuples(self):
        # Cannot send these to sever
        return []

class CookedMiscInfo:
    def __init__(self):
        self.recipient_list = []
        self.comment_to_list = []
        self.comment_in_list = []

    def parse(self, c):
        raw = c.parse_array(RawMiscInfo)
        i = 0
        while i < len(raw):
            if raw[i].type in [MI_RECPT, MI_CC_RECPT, MI_BCC_RECPT]:
                r = MIRecipient(raw[i].type, raw[i].data)
                i = r.decode_additional(raw, i+1)
                self.recipient_list.append(r)
            elif raw[i].type in [MI_COMM_TO, MI_FOOTN_TO]:
                ct = MICommentTo(raw[i].type, raw[i].data)
                i = ct.decode_additional(raw, i+1)
                self.comment_to_list.append(ct)
            elif raw[i].type in [MI_COMM_IN, MI_FOOTN_IN]:
                ci = MICommentIn(raw[i].type - 1 , raw[i].data  ) # KLUDGE :-)
                i = i + 1
                self.comment_in_list.append(ci)
            else:
                raise ProtocolError

    def to_string(self):
        list = []
        for r in self.comment_to_list + \
            self.recipient_list + \
            self.comment_in_list:
            list = list + r.get_tuples()
        return "%d { %s}" % (len(list),
                             "".join(["%d %d " % \
                                          (x[0], x[1]) for x in list]))
                             

# AUX INFO

class AuxItemFlags:
    def __init__(self):
        self.deleted = 0
        self.inherit = 0
        self.secret = 0
        self.hide_creator = 0
        self.dont_garb = 0
        self.reserved2 = 0
        self.reserved3 = 0
        self.reserved4 = 0

    def parse(self, c):
        (self.deleted,
         self.inherit,
         self.secret,
         self.hide_creator,
         self.dont_garb,
         self.reserved2,
         self.reserved3,
         self.reserved4) = c.parse_bitstring(8)

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

# This class works as Aux-Item on reception, and
# Aux-Item-Input when being sent.
class AuxItem: 
    def __init__(self, tag = None, data = ""):
        self.aux_no = None # not part of Aux-Item-Input
        self.tag = tag
        self.creator = None # not part of Aux-Item-Input
        self.created_at = None # not part of Aux-Item-Input
        self.flags = AuxItemFlags()
        self.inherit_limit = 0
        self.data = data

    def parse(self, c):
        self.aux_no = c.parse_int()
        self.tag = c.parse_int()
        self.creator = c.parse_int()
        self.created_at = c.parse_object(Time)
        self.flags = c.parse_object(AuxItemFlags)
        self.inherit_limit = c.parse_int()
        self.data = c.parse_string()

    def __repr__(self):
        return "<AuxItem %d>" % self.tag
    def to_string(self):
        return "%d %s %d %dH%s" % \
               (self.tag,
                self.flags.to_string(),
                self.inherit_limit,
                len(self.data), self.data)

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

class TextStat:
    def parse(self, c, old_format = 0):
        self.creation_time = c.parse_object(Time)
        self.author = c.parse_int()
        self.no_of_lines = c.parse_int()
        self.no_of_chars = c.parse_int()
        self.no_of_marks = c.parse_int()
        self.misc_info = c.parse_object(CookedMiscInfo)
        if old_format:
            self.aux_items = []
        else:
            self.aux_items = c.parse_array(AuxItem)

# CONFERENCE

class ConfType:
    def __init__(self):
        self.rd_prot = 0
        self.original = 0
        self.secret = 0
        self.letterbox = 0
        self.allow_anonymous = 0
        self.forbid_secret = 0
        self.reserved2 = 0
        self.reserved3 = 0

    def parse(self, c, old_format = 0):
        if old_format:
            (self.rd_prot,
             self.original,
             self.secret,
             self.letterbox) = c.parse_bitstring(4)
            (self.allow_anonymous,
             self.forbid_secret,
             self.reserved2,
             self.reserved3) = (0,0,0,0)
        else:
            (self.rd_prot,
             self.original,
             self.secret,
             self.letterbox,
             self.allow_anonymous,
             self.forbid_secret,
             self.reserved2,
             self.reserved3) = c.parse_bitstring(8)

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

class Conference:
    def parse(self, c):
        self.name = c.parse_string()
        self.type = c.parse_object(ConfType)
        self.creation_time = c.parse_object(Time)
        self.last_written = c.parse_object(Time)
        self.creator = c.parse_int()
        self.presentation = c.parse_int()
        self.supervisor = c.parse_int()
        self.permitted_submitters = c.parse_int()
        self.super_conf = c.parse_int()
        self.msg_of_day = c.parse_int()
        self.nice = c.parse_int()
        self.keep_commented = c.parse_int()
        self.no_of_members = c.parse_int()
        self.first_local_no = c.parse_int()
        self.no_of_texts = c.parse_int()
        self.expire = c.parse_int()
        self.aux_items = c.parse_array(AuxItem)

    def __repr__(self):
        return "<Conference %s>" % self.name
    
class UConference:
    def parse(self, c):
        self.name = c.parse_string()
        self.type = c.parse_object(ConfType)
        self.highest_local_no = c.parse_int()
        self.nice = c.parse_int()

    def __repr__(self):
        return "<UConference %s>" % self.name
    
# PERSON

class PrivBits:
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

    def parse(self, c):
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
         self.flg16) = c.parse_bitstring(16)

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
    
class PersonalFlags:
    def __init__(self):
        self.unread_is_secret = 0
        self.flg2 = 0
        self.flg3 = 0
        self.flg4 = 0
        self.flg5 = 0
        self.flg6 = 0
        self.flg7 = 0
        self.flg8 = 0

    def parse(self, c):
        (self.unread_is_secret,
         self.flg2,
         self.flg3,
         self.flg4,
         self.flg5,
         self.flg6,
         self.flg7,
         self.flg8) = c.parse_bitstring(8)

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

class Person:
    def parse(self, c):
        self.username = c.parse_string()
        self.privileges = c.parse_object(PrivBits)
        self.flags = c.parse_object(PersonalFlags)
        self.last_login = c.parse_object(Time)
        self.user_area = c.parse_int()
        self.total_time_present = c.parse_int()
        self.sessions = c.parse_int()
        self.created_lines = c.parse_int()
        self.created_bytes = c.parse_int()
        self.read_texts = c.parse_int()
        self.no_of_text_fetches = c.parse_int()
        self.created_persons = c.parse_int()
        self.created_confs = c.parse_int()
        self.first_created_local_no = c.parse_int()
        self.no_of_created_texts = c.parse_int()
        self.no_of_marks = c.parse_int()
        self.no_of_confs = c.parse_int()

# MEMBERSHIP

class MembershipType:
    def __init__(self):
        self.invitation = 0
        self.passive = 0
        self.secret = 0
        self.passive_message_invert = 0
        self.reserved2 = 0
        self.reserved3 = 0
        self.reserved4 = 0
        self.reserved5 = 0

    def parse(self, c):
        (self.invitation,
         self.passive,
         self.secret,
         self.passive_message_invert,
         self.reserved2,
         self.reserved3,
         self.reserved4,
         self.reserved5) = c.parse_bitstring(8)

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

class Membership10:
    def parse(self, c):
        self.position = c.parse_int()
        self.last_time_read  = c.parse_object(Time)
        self.conference = c.parse_int()
        self.priority = c.parse_int()
        self.last_text_read = c.parse_int()
        self.read_texts = c.parse_array_of_int()
        self.added_by = c.parse_int()
        self.added_at = c.parse_object(Time)
        self.type = c.parse_object(MembershipType)

class ReadRange:
    def __init__(self, first_read = 0, last_read = 0):
        self.first_read = first_read
        self.last_read = last_read
        
    def parse(self, c):
        self.first_read = c.parse_int()
        self.last_read = c.parse_int()

    def __repr__(self):
        return "<ReadRange %d-%d>" % (self.first_read, self.last_read)

    def to_string(self):
        return "%d %d" % \
               (self.first_read,
                self.last_read)
    
class Membership11:
    def parse(self, c):
        self.position = c.parse_int()
        self.last_time_read  = c.parse_object(Time)
        self.conference = c.parse_int()
        self.priority = c.parse_int()
        self.read_ranges = c.parse_array(ReadRange)
        self.added_by = c.parse_int()
        self.added_at = c.parse_object(Time)
        self.type = c.parse_object(MembershipType)

Membership = Membership11

class Member:
    def parse(self, c):
        self.member  = c.parse_int()
        self.added_by = c.parse_int()
        self.added_at = c.parse_object(Time)
        self.type = c.parse_object(MembershipType)

# TEXT LIST

class TextList:
    def parse(self, c):
        self.first_local_no = c.parse_int()
        self.texts = c.parse_array_of_int()

# TEXT MAPPING

class TextNumberPair:
    def parse(self, c):
        self.local_number = c.parse_int()
        self.global_number = c.parse_int()
    
class TextMapping:
    def parse(self, c):
        self.range_begin = c.parse_int() # Included in the range
        self.range_end = c.parse_int() # Not included in range (first after)
        self.later_texts_exists = c.parse_int()
        self.block_type = c.parse_int()

        self.dict = {}
        self.list = []

        if self.block_type == 0:
            # Sparse
            self.type_text = "sparse"
            self.sparse_list = c.parse_array(TextNumberPair)
            for tnp in self.sparse_list:
                self.dict[tnp.local_number] = tnp.global_number
                self.list.append((tnp.local_number, tnp.global_number))
        elif self.block_type == 1:
            # Dense
            self.type_text = "dense"
            self.dense_first = c.parse_int()
            self.dense_texts = c.parse_array_of_int()
            local_number = self.dense_first
            for global_number in self.dense_texts:
                self.dict[local_number] = global_number
                self.list.append((local_number, global_number))
                local_number = local_number + 1
        else:
            raise ProtocolError

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

class Mark:
    def parse(self, c):
        self.text_no = c.parse_int()
        self.type = c.parse_int()

    def __repr__(self):
        return "<Mark %d (%d)>" % (self.text_no, self.type)


# SERVER INFORMATION

# This class works as Info on reception, and
# Info-Old when being sent.
class Info:
    def __init__(self):
        self.version = None
        self.conf_pres_conf = None
        self.pers_pres_conf = None
        self.motd_conf = None
        self.kom_news_conf = None
        self.motd_of_lyskom = None
        self.aux_item_list = [] # not part of Info-Old

    def parse(self, c):
        self.version = c.parse_int()
        self.conf_pres_conf = c.parse_int()
        self.pers_pres_conf = c.parse_int()
        self.motd_conf = c.parse_int()
        self.kom_news_conf = c.parse_int()
        self.motd_of_lyskom = c.parse_int()
        self.aux_item_list = c.parse_array(AuxItem)

    def to_string(self):
        return "%d %d %d %d %d %d" % (
            self.version,
            self.conf_pres_conf,
            self.pers_pres_conf,
            self.motd_conf,
            self.kom_news_conf,
            self.motd_of_lyskom)

class VersionInfo:
    def parse(self, c):
        self.protocol_version = c.parse_int()
        self.server_software = c.parse_string()
        self.software_version = c.parse_string()

    def __repr__(self):
        return "<VersionInfo protocol %d by %s %s>" % \
               (self.protocol_version,
                self.server_software, self.software_version)

# New in protocol version 11
class StaticServerInfo: 
    def parse(self, c):
        self.boot_time = c.parse_object(Time)
        self.save_time = c.parse_object(Time)
        self.db_status = c.parse_string()
        self.existing_texts = c.parse_int()
        self.highest_text_no = c.parse_int()
        self.existing_confs = c.parse_int()
        self.existing_persons = c.parse_int()
        self.highest_conf_no = c.parse_int()

    def __repr__(self):
        return "<StaticServerInfo>"

# SESSION INFORMATION

class SessionFlags:
    def parse(self, c):
        (self.invisible,
         self.user_active_used,
         self.user_absent,
         self.reserved3,
         self.reserved4,
         self.reserved5,
         self.reserved6,
         self.reserved7) = c.parse_bitstring(8)

class DynamicSessionInfo:
    def parse(self, c):
        self.session = c.parse_int()
        self.person = c.parse_int()
        self.working_conference = c.parse_int()
        self.idle_time = c.parse_int()
        self.flags = c.parse_object(SessionFlags)
        self.what_am_i_doing  = c.parse_string()

class StaticSessionInfo:
    def parse(self, c):
        self.username = c.parse_string()
        self.hostname = c.parse_string()
        self.ident_user = c.parse_string()
        self.connection_time = c.parse_object(Time)

class SchedulingInfo:
    def parse(self, c):
        self.priority = c.parse_int()
        self.weight = c.parse_int()

class WhoInfo:
    def parse(self, c):
        self.person = c.parse_int()
        self.working_conference = c.parse_int()
        self.session = c.parse_int()
        self.what_am_i_doing  = c.parse_string()
        self.username = c.parse_string()
     
# STATISTICS

class StatsDescription:
    def parse(self, c):
        self.what = c.parse_array_of_string()
        self.when = c.parse_array_of_int()
     
    def __repr__(self):
        return "<StatsDescription>"

class Stats:
    def parse(self, c):
        self.average = c.parse_float()
        self.ascent_rate = c.parse_float()
        self.descent_rate = c.parse_float()

    def __repr__(self):
        return "<Stats %f + %f - %f>" % (self.average,
                                         self.ascent_rate,
                                         self.descent_rate)



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
