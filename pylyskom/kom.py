# -*- coding: iso-8859-1 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2013 Oskar Skoog. Released under GPL.

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


#
# Classes for requests to the server are all subclasses of Request.
#
# N.B: the identifier "c" below should be read as "connection"
#

class Request:
    def register(self, c):
        self.id = c.register_request(self)
        self.c = c
        
    def response(self):
        return self.c.wait_and_dequeue(self.id)

    # Default response parser expects nothing.
    # Override when appropriate.
    def parse_response(self):
        return None

# login-old [0] (1) Obsolete (4) Use login (62)

# logout [1] (1) Recommended
class ReqLogout(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string(("%d 1\n" % self.id).encode('latin1'))

# change-conference [2] (1) Recommended
class ReqChangeConference(Request):
    def __init__(self, c, conf_no):
        self.register(c)
        c.send_string(("%d 2 %d\n" % (self.id, conf_no)).encode('latin1'))

# change-name [3] (1) Recommended
class ReqChangeName(Request):
    def __init__(self, c, conf_no, new_name):
        self.register(c)
        c.send_string("%d 3 %d %dH%s\n" % (self.id, conf_no,
                                           len(new_name), new_name))

# change-what-i-am-doing [4] (1) Recommended
class ReqChangeWhatIAmDoing(Request):
    def __init__(self, c, what):
        self.register(c)
        c.send_string(("%d 4 %dH%s\n" % (self.id, 
                                          len(what), what)).encode('latin1'))

# create-person-old [5] (1) Obsolete (10) Use create-person (89)
# get-person-stat-old [6] (1) Obsolete (1) Use get-person-stat (49)

# set-priv-bits [7] (1) Recommended
class ReqSetPrivBits(Request):
    def __init__(self, c, person_no, privileges):
        self.register(c)
        c.send_string("%d 7 %d %s\n" % (self.id,
                                        person_no,
                                        privileges.to_string()))

# set-passwd [8] (1) Recommended
class ReqSetPasswd(Request):
    def __init__(self, c, person_no, old_pwd, new_pwd):
        self.register(c)
        c.send_string("%d 8 %d %dH%s %dH%s\n" % (self.id,
                                                 person_no,
                                                 len(old_pwd), old_pwd,
                                                 len(new_pwd), new_pwd))

# query-read-texts-old [9] (1) Obsolete (10) Use query-read-texts (98)
# create-conf-old [10] (1) Obsolete (10) Use create-conf (88)

# delete-conf [11] (1) Recommended
class ReqDeleteConf(Request):
    def __init__(self, c, conf_no):
        self.register(c)
        c.send_string("%d 11 %d\n" % (self.id, conf_no))

# lookup-name [12] (1) Obsolete (7) Use lookup-z-name (76)
# get-conf-stat-older [13] (1) Obsolete (10) Use get-conf-stat (91)
# add-member-old [14] (1) Obsolete (10) Use add-member (100)

# sub-member [15] (1) Recommended
class ReqSubMember(Request):
    def __init__(self, c, conf_no, person_no):
        self.register(c)
        c.send_string("%d 15 %d %d\n" % (self.id, conf_no, person_no))

# set-presentation [16] (1) Recommended
class ReqSetPresentation(Request):
    def __init__(self, c, conf_no, text_no):
        self.register(c)
        c.send_string("%d 16 %d %d\n" % (self.id, conf_no, text_no))

# set-etc-motd [17] (1) Recommended
class ReqSetEtcMoTD(Request):
    def __init__(self, c, conf_no, text_no):
        self.register(c)
        c.send_string("%d 17 %d %d\n" % (self.id, conf_no, text_no))

# set-supervisor [18] (1) Recommended
class ReqSetSupervisor(Request):
    def __init__(self, c, conf_no, admin):
        self.register(c)
        c.send_string("%d 18 %d %d\n" % (self.id, conf_no, admin))

# set-permitted-submitters [19] (1) Recommended
class ReqSetPermittedSubmitters(Request):
    def __init__(self, c, conf_no, perm_sub):
        self.register(c)
        c.send_string("%d 19 %d %d\n" % (self.id, conf_no, perm_sub))

# set-super-conf [20] (1) Recommended
class ReqSetSuperConf(Request):
    def __init__(self, c, conf_no, super_conf):
        self.register(c)
        c.send_string("%d 20 %d %d\n" % (self.id, conf_no, super_conf))

# set-conf-type [21] (1) Recommended
class ReqSetConfType(Request):
    def __init__(self, c, conf_no, type):
        self.register(c)
        c.send_string("%d 21 %d %s\n" % (self.id,
                                         conf_no,
                                         type.to_string()))

# set-garb-nice [22] (1) Recommended
class ReqSetGarbNice(Request):
    def __init__(self, c, conf_no, nice):
        self.register(c)
        c.send_string("%d 22 %d %d\n" % (self.id, conf_no, nice))

# get-marks [23] (1) Recommended
class ReqGetMarks(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 23\n" % (self.id))

    def parse_response(self):
        # --> string
        return self.c.parse_array(Mark)

# mark-text-old [24] (1) Obsolete (4) Use mark-text/unmark-text (72/73)

# get-text [25] (1) Recommended
class ReqGetText(Request):
    def __init__(self, c, text_no,
                 start_char = 0,
                 end_char = MAX_TEXT_SIZE):
        self.register(c)
        c.send_string(("%d 25 %d %d %d\n" % 
                       (self.id, text_no, 
                        start_char, end_char)).encode('latin1'))

    def parse_response(self):
        # --> string
        return self.c.parse_string()
    
# get-text-stat-old [26] (1) Obsolete (10) Use get-text-stat (90)

# mark-as-read [27] (1) Recommended
class ReqMarkAsRead(Request):
    def __init__(self, c, conf_no, texts):
        self.register(c)
        c.send_string(("%d 27 %d %s\n" %
                       (self.id,
                        conf_no,
                        c.array_of_int_to_string(texts))).encode('latin1'))
                      
# create-text-old [28] (1) Obsolete (10) Use create-text (86)

# delete-text [29] (1) Recommended
class ReqDeleteText(Request):
    def __init__(self, c, text_no):
        self.register(c)
        c.send_string("%d 29 %d\n" % (self.id, text_no))

# add-recipient [30] (1) Recommended
class ReqAddRecipient(Request):
    def __init__(self, c, text_no, conf_no, recpt_type = MIR_TO):
        self.register(c)
        c.send_string("%d 30 %d %d %d\n" % \
                      (self.id, text_no, conf_no, recpt_type))

# sub-recipient [31] (1) Recommended
class ReqSubRecipient(Request):
    def __init__(self, c, text_no, conf_no):
        self.register(c)
        c.send_string("%d 31 %d %d\n" % \
                      (self.id, text_no, conf_no))

# add-comment [32] (1) Recommended
class ReqAddComment(Request):
    def __init__(self, c, text_no, comment_to):
        self.register(c)
        c.send_string("%d 32 %d %d\n" % \
                      (self.id, text_no, comment_to))

# sub-comment [33] (1) Recommended
class ReqSubComment(Request):
    def __init__(self, c, text_no, comment_to):
        self.register(c)
        c.send_string("%d 33 %d %d\n" % \
                      (self.id, text_no, comment_to))

# get-map [34] (1) Obsolete (10) Use local-to-global (103)
class ReqGetMap(Request):
    def __init__(self, c, conf_no, first_local_no, no_of_texts):
        self.register(c)
        c.send_string("%d 34 %d %d %d\n" %
		      (self.id, conf_no, first_local_no, no_of_texts))

    def parse_response(self):
	# --> Text-List
        return self.c.parse_object(TextList)

# get-time [35] (1) Recommended
class ReqGetTime(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 35\n" % self.id)

    def parse_response(self):
        # --> Time
        return self.c.parse_object(Time)
    
# get-info-old [36] (1) Obsolete (10) Use get-info (94)

# add-footnote [37] (1) Recommended
class ReqAddFootnote(Request):
    def __init__(self, c, text_no, footnote_to):
        self.register(c)
        c.send_string("%d 37 %d %d\n" % \
                      (self.id, text_no, footnote_to))

# sub-footnote [38] (1) Recommended
class ReqSubFootnote(Request):
    def __init__(self, c, text_no, footnote_to):
        self.register(c)
        c.send_string("%d 38 %d %d\n" % \
                      (self.id, text_no, footnote_to))

# who-is-on-old [39] (1) Obsolete (9) Use get-static-session-info (84) and
#                                         who-is-on-dynamic (83)

# set-unread [40] (1) Recommended
class ReqSetUnread(Request):
    def __init__(self, c, conf_no, no_of_unread):
        self.register(c)
        c.send_string("%d 40 %d %d\n" % \
                      (self.id, conf_no, no_of_unread))

# set-motd-of-lyskom [41] (1) Recommended
class ReqSetMoTDOfLysKOM(Request):
    def __init__(self, c, text_no):
        self.register(c)
        c.send_string("%d 41 %d\n" % \
                      (self.id, text_no))

# enable [42] (1) Recommended
class ReqEnable(Request):
    def __init__(self, c, level):
        self.register(c)
        c.send_string("%d 42 %d\n" % (self.id, level))

# sync-kom [43] (1) Recommended
class ReqSyncKOM(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 43\n" % (self.id))

# shutdown-kom [44] (1) Recommended
class ReqShutdownKOM(Request):
    def __init__(self, c, exit_val):
        self.register(c)
        c.send_string("%d 44 %d\n" % (self.id, exit_val))

# broadcast [45] (1) Obsolete (1) Use send-message (53)
# get-membership-old [46] (1) Obsolete (10) Use get-membership (99)
# get-created-texts [47] (1) Obsolete (10) Use map-created-texts (104)
# get-members-old [48] (1) Obsolete (10) Use get-members (101)

# get-person-stat [49] (1) Recommended
class ReqGetPersonStat(Request):
    def __init__(self, c, person_no):
        self.register(c)
        c.send_string("%d 49 %d\n" % (self.id, person_no))

    def parse_response(self):
        # --> Person
        return self.c.parse_object(Person)

# get-conf-stat-old [50] (1) Obsolete (10) Use get-conf-stat (91)

# who-is-on [51] (1) Obsolete (9)  Use who-is-on-dynamic (83) and
#                                      get-static-session-info (84)

# get-unread-confs [52] (1) Recommended
class ReqGetUnreadConfs(Request):
    def __init__(self, c, person_no):
        self.register(c)
        c.send_string(("%d 52 %d\n" % (self.id, person_no)).encode('latin1'))

    def parse_response(self):
        # --> ARRAY Conf-No
        return self.c.parse_array_of_int()

# send-message [53] (1) Recommended
class ReqSendMessage(Request):
    def __init__(self, c, conf_no, message):
        self.register(c)
        c.send_string(("%d 53 %d %dH%s\n" %
                       (self.id, conf_no, len(message), 
                        message)).encode('latin1'))

# get-session-info [54] (1) Obsolete (9) Use who-is-on-dynamic (83)

# disconnect [55] (1) Recommended
class ReqDisconnect(Request):
    def __init__(self, c, session_no):
        self.register(c)
        c.send_string("%d 55 %d\n" %
                      (self.id, session_no))

# who-am-i [56] (1) Recommended
class ReqWhoAmI(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 56\n" % (self.id))
        
    def parse_response(self):
        # --> Session-No
        return self.c.parse_int()

# set-user-area [57] (2) Recommended
class ReqSetUserArea(Request):
    def __init__(self, c, person_no, user_area):
        self.register(c)
        c.send_string("%d 57 %d %d\n" % (self.id, person_no, user_area))

# get-last-text [58] (3) Recommended
class ReqGetLastText(Request):
    def __init__(self, c, before):
        self.register(c)
        c.send_string("%d 58 %s\n" % (self.id, before.to_string()))
        
    def parse_response(self):
        # --> Text-No
        return self.c.parse_int()

# create-anonymous-text-old [59] (3) Obsolete (10)
#                                    Use create-anonymous-text (87)

# find-next-text-no [60] (3) Recommended
class ReqFindNextTextNo(Request):
    def __init__(self, c, start):
        self.register(c)
        c.send_string("%d 60 %d\n" % (self.id, start))
        
    def parse_response(self):
        # --> Text-No
        return self.c.parse_int()

# find-previous-text-no [61] (3) Recommended
class ReqFindPreviousTextNo(Request):
    def __init__(self, c, start):
        self.register(c)
        c.send_string("%d 61 %d\n" % (self.id, start))
        
    def parse_response(self):
        # --> Text-No
        return self.c.parse_int()

# login [62] (4) Recommended
class ReqLogin(Request):
    def __init__(self, c, person_no, password, invisible = 1):
        self.register(c)
        c.send_string(("%d 62 %d %dH%s %d\n" %
                      (self.id, person_no, len(password), password, 
                       invisible)).encode('latin1'))

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
    def __init__(self, c, client_name, client_version):
        self.register(c)
        c.send_string (("%d 69 %dH%s %dH%s\n" %
                        (self.id,
                         len(client_name), client_name,
                         len(client_version), client_version)).encode('latin1'))

# get-client-name [70] (6) Recommended
class ReqGetClientName(Request):
    def __init__(self, c, session_no):
        self.register(c)
        c.send_string("%d 70 %d\n" % (self.id, session_no))
        
    def parse_response(self):
        # --> Hollerith
        return self.c.parse_string()

# get-client-version [71] (6) Recommended
class ReqGetClientVersion(Request):
    def __init__(self, c, session_no):
        self.register(c)
        c.send_string("%d 71 %d\n" % (self.id, session_no))
        
    def parse_response(self):
        # --> Hollerith
        return self.c.parse_string()

# mark-text [72] (4) Recommended
class ReqMarkText(Request):
    def __init__(self, c, text_no, mark_type):
        self.register(c)
        c.send_string("%d 72 %d %d\n" % (self.id, text_no, mark_type))

# unmark-text [73] (6) Recommended
class ReqUnmarkText(Request):
    def __init__(self, c, text_no):
        self.register(c)
        c.send_string("%d 73 %d\n" % (self.id, text_no))

# re-z-lookup [74] (7) Recommended
class ReqReZLookup(Request):
    def __init__(self, c, regexp, want_pers = 0, want_confs = 0):
        self.register(c)
        c.send_string("%d 74 %dH%s %d %d\n" %
                      (self.id, len(regexp), regexp, want_pers, want_confs))

    def parse_response(self):
        # --> ARRAY ConfZInfo
        return self.c.parse_array(ConfZInfo)

# get-version-info [75] (7) Recommended
class ReqGetVersionInfo(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 75\n" % (self.id))

    def parse_response(self):
        # --> Version-Info
        return self.c.parse_object(VersionInfo)

# lookup-z-name [76] (7) Recommended
class ReqLookupZName(Request):
    def __init__(self, c, name, want_pers = 0, want_confs = 0):
        self.register(c)
        c.send_string(("%d 76 %dH%s %d %d\n" %
                       (self.id, len(name), name, 
                        want_pers, want_confs)).encode('latin1'))

    def parse_response(self):
        # --> ARRAY ConfZInfo
        return self.c.parse_array(ConfZInfo)

# set-last-read [77] (8) Recommended
class ReqSetLastRead(Request):
    def __init__(self, c, conf_no, last_read):
        self.register(c)
        c.send_string("%d 77 %d %d\n" % \
                      (self.id, conf_no, last_read))

# get-uconf-stat [78] (8) Recommended
class ReqGetUconfStat(Request):
    def __init__(self, c, conf_no):
        self.register(c)
        c.send_string(("%d 78 %d\n" % (self.id, conf_no)).encode('latin1'))

    def parse_response(self):
        # --> UConference
        return self.c.parse_object(UConference)

# set-info [79] (9) Recommended
class ReqSetInfo(Request):
    def __init__(self, c, info):
        self.register(c)
        c.send_string("%d 79 %s\n" % (self.id, info.to_string()))

# accept-async [80] (9) Recommended
class ReqAcceptAsync(Request):
    def __init__(self, c, request_list):
        self.register(c)
        c.send_string(("%d 80 %s\n" %
                      (self.id,
                       c.array_of_int_to_string(request_list)))\
                          .encode('latin1'))

# query-async [81] (9) Recommended
class ReqQueryAsync(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 81\n" % (self.id))

    def parse_response(self):
        # --> ARRAY INT32
        return self.c.parse_array_of_int()

# user-active [82] (9) Recommended
class ReqUserActive(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 82\n" % (self.id))

# who-is-on-dynamic [83] (9) Recommended
class ReqWhoIsOnDynamic(Request):
    def __init__(self, c,
                 want_visible = 1, want_invisible = 0,
                 active_last = 0):
        self.register(c)
        c.send_string("%d 83 %d %d %d\n" % \
                      (self.id, want_visible, want_invisible, active_last))

    def parse_response(self):
        # --> ARRAY Dynamic-Session-Info
        return self.c.parse_array(DynamicSessionInfo)

# get-static-session-info [84] (9) Recommended
class ReqGetStaticSessionInfo(Request):
    def __init__(self, c, session_no):
        self.register(c)
        c.send_string("%d 84 %d\n" % (self.id, session_no))

    def parse_response(self):
        # --> Static-Session-Info
        return self.c.parse_object(StaticSessionInfo)

# get-collate-table [85] (10) Recommended
class ReqGetCollateTable(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 85\n" % (self.id))

    def parse_response(self):
        # --> HOLLERITH
        return self.c.parse_string()

# create-text [86] (10) Recommended
class ReqCreateText(Request):
    def __init__(self, c, text, misc_info, aux_items = []):
        self.register(c)
        c.send_string("%d 86 %dH%s %s %s\n" %
                      (self.id,
                       len(text), text,
                       misc_info.to_string(),
                       c.array_to_string(aux_items)))
        
    def parse_response(self):
        # --> Text-No
        return self.c.parse_int()

# create-anonymous-text [87] (10) Recommended
class ReqCreateAnonymousText(Request):
    def __init__(self, c, text, misc_info, aux_items = []):
        self.register(c)
        c.send_string("%d 87 %dH%s %s %s\n" %
                      (self.id,
                       len(text), text,
                       misc_info.to_string(),
                       c.array_to_string(aux_items)))
        
    def parse_response(self):
        # --> Text-No
        return self.c.parse_int()

# create-conf [88] (10) Recommended
class ReqCreateConf(Request):
    def __init__(self, c, name, type, aux_items = []):
        self.register(c)
        c.send_string("%d 88 %dH%s %s %s\n" %
                      (self.id,
                       len(name), name,
                       type.to_string(),
                       c.array_to_string(aux_items)))
        
    def parse_response(self):
        # --> Conf-No
        return self.c.parse_int()

# create-person [89] (10) Recommended
class ReqCreatePerson(Request):
    def __init__(self, c, name, passwd, flags, aux_items = []):
        self.register(c)
        c.send_string("%d 89 %dH%s %dH%s %s %s\n" %
                      (self.id,
                       len(name), name,
                       len(passwd), passwd,
                       flags.to_string(),
                       c.array_to_string(aux_items)))
        
    def parse_response(self):
        # --> Pers-No
        return self.c.parse_int()

# get-text-stat [90] (10) Recommended
class ReqGetTextStat(Request):
    def __init__(self, c, text_no):
        self.register(c)
        c.send_string(("%d 90 %d\n" %
                      (self.id, text_no)).encode('latin1'))

    def parse_response(self):
        # --> TextStat
        return self.c.parse_object(TextStat)

# get-conf-stat [91] (10) Recommended
class ReqGetConfStat(Request):
    def __init__(self, c, conf_no):
        self.register(c)
        c.send_string(("%d 91 %d\n" % (self.id, conf_no)).encode('latin1'))

    def parse_response(self):
        # --> Conference
        return self.c.parse_object(Conference)

# modify-text-info [92] (10) Recommended
class ReqModifyTextInfo(Request):
    def __init__(self, c, text_no, delete, add):
        self.register(c)
        c.send_string("%d 92 %d %s %s\n" %
                      (self.id,
                       text_no,
                       c.array_of_int_to_string(delete),
                       c.array_to_string(add)))

# modify-conf-info [93] (10) Recommended
class ReqModifyConfInfo(Request):
    def __init__(self, c, conf_no, delete, add):
        self.register(c)
        c.send_string("%d 93 %d %s %s\n" %
                      (self.id,
                       conf_no,
                       c.array_of_int_to_string(delete),
                       c.array_to_string(add)))

# get-info [94] (10) Recommended
class ReqGetInfo(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string(("%d 94\n" % (self.id)).encode('latin1'))

    def parse_response(self):
        # --> Info
        return self.c.parse_object(Info)

# modify-system-info [95] (10) Recommended
class ReqModifySystemInfo(Request):
    def __init__(self, c, delete, add):
        self.register(c)
        c.send_string("%d 95 %s %s\n" %
                      (self.id,
                       c.array_of_int_to_string(delete),
                       c.array_to_string(add)))

# query-predefined-aux-items [96] (10) Recommended
class ReqQueryPredefinedAuxItems(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 96\n" % (self.id))

    def parse_response(self):
        # --> ARRAY INT32
        return self.c.parse_array_of_int()

# set-expire [97] (10) Experimental
class ReqSetExpire(Request):
    def __init__(self, c, conf_no, expire):
        self.register(c)
        c.send_string("%d 97 %d %d\n" % (self.id, conf_no, expire))

# query-read-texts-10 [98] (10) Obsolete (11) Use query-read-texts (107)
class ReqQueryReadTexts10(Request):
    def __init__(self, c, person_no, conf_no):
        self.register(c)
        c.send_string("%d 98 %d %d\n" % (self.id, person_no, conf_no))

    def parse_response(self):
        # --> Membership10
        return self.c.parse_object(Membership10)

# get-membership-10 [99] (10) Obsolete (11) Use get-membership (108)

class ReqGetMembership10(Request):
    def __init__(self, c, person_no, first, no_of_confs, want_read_texts):
        self.register(c)
        c.send_string("%d 99 %d %d %d %d\n" % \
                      (self.id, person_no,
                       first, no_of_confs, want_read_texts))

    def parse_response(self):
        # --> ARRAY Membership10
        return self.c.parse_array(Membership10)

# add-member [100] (10) Recommended
class ReqAddMember(Request):
    def __init__(self, c, conf_no, person_no, priority, where, type):
        self.register(c)
        c.send_string("%d 100 %d %d %d %d %s\n" % \
                      (self.id, conf_no, person_no,
                       priority, where, type.to_string()))

# get-members [101] (10) Recommended
class ReqGetMembers(Request):
    def __init__(self, c, conf_no, first, no_of_members):
        self.register(c)
        c.send_string("%d 101 %d %d %d\n" % \
                      (self.id, conf_no, first, no_of_members))

    def parse_response(self):
        # --> ARRAY Member
        return self.c.parse_array(Member)

# set-membership-type [102] (10) Recommended
class ReqSetMembershipType(Request):
    def __init__(self, c, person_no, conf_no, type):
        self.register(c)
        c.send_string("%d 102 %d %d %s\n" % \
                      (self.id, person_no, conf_no, type.to_string()))

# local-to-global [103] (10) Recommended
class ReqLocalToGlobal(Request):
    def __init__(self, c, conf_no, first_local_no, no_of_existing_texts):
        self.register(c)
        c.send_string(("%d 103 %d %d %d\n" % \
                      (self.id, conf_no, first_local_no, 
                       no_of_existing_texts)).encode('latin1'))

    def parse_response(self):
        # --> Text-Mapping
        return self.c.parse_object(TextMapping)

# map-created-texts [104] (10) Recommended
class ReqMapCreatedTexts(Request):
    def __init__(self, c, author, first_local_no, no_of_existing_texts):
        self.register(c)
        c.send_string("%d 104 %d %d %d\n" % \
                      (self.id, author, first_local_no, no_of_existing_texts))

    def parse_response(self):
        # --> Text-Mapping
        return self.c.parse_object(TextMapping)

# set-keep-commented [105] (11) Recommended (10) Experimental
class ReqSetKeepCommented(Request):
    def __init__(self, c, conf_no, keep_commented):
        self.register(c)
        c.send_string("%d 105 %d %d\n" % (self.id, conf_no, keep_commented))

# set-pers-flags [106] (10) Recommended

class ReqSetPersFlags(Request):
    def __init__(self, c, person_no, flags):
        self.register(c)
        c.send_string("%d 106 %d %s\n" % (self.id,
                                        person_no,
                                        flags.to_string()))

### --- New in protocol version 11 ---

# query-read-texts [107] (11) Recommended
class ReqQueryReadTexts11(Request):
    def __init__(self, c, person_no, conf_no,
                 want_read_ranges, max_ranges):
        self.register(c)
        c.send_string(("%d 107 %d %d %d %d\n" % (self.id, person_no, conf_no,
                                                want_read_ranges,
                                                max_ranges)).encode('latin1'))

    def parse_response(self):
        # --> Membership11
        return self.c.parse_object(Membership11)

ReqQueryReadTexts = ReqQueryReadTexts11

# get-membership [108] (11) Recommended
class ReqGetMembership11(Request):
    def __init__(self, c, person_no, first, no_of_confs,
                 want_read_ranges, max_ranges):
        self.register(c)
        c.send_string("%d 108 %d %d %d %d %d\n" % \
                      (self.id, person_no,
                       first, no_of_confs,
                       want_read_ranges, max_ranges))

    def parse_response(self):
        # --> ARRAY Membership11
        return self.c.parse_array(Membership11)

ReqGetMembership = ReqGetMembership11

# mark-as-unread [109] (11) Recommended
class ReqMarkAsUnread(Request):
    def __init__(self, c, conf_no, text_no):
        self.register(c)
        c.send_string("%d 109 %d %d\n" %
                      (self.id,
                       conf_no,
                       text_no))

# set-read-ranges [110] (11) Recommended
class ReqSetReadRanges(Request):
    def __init__(self, c, conf_no, read_ranges):
        self.register(c)
        c.send_string("%d 110 %s %s\n" %
                      (self.id,
                       conf_no,
                       c.array_to_string(read_ranges)))

# get-stats-description [111] (11) Recommended
class ReqGetStatsDescription(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 111 \n" % (self.id))

    def parse_response(self):
        # --> Stats-Description
        return self.c.parse_object(StatsDescription)

# get-stats [112] (11) Recommended
class ReqGetStats(Request):
    def __init__(self, c, what):
        self.register(c)
        c.send_string("%d 112 %dH%s\n" % (self.id,
                                          len(what), what))

    def parse_response(self):
        # --> ARRAY Stats
        return self.c.parse_array(Stats)

# get-boottime-info [113] (11) Recommended
class ReqGetBoottimeInfo(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 113 \n" % (self.id))

    def parse_response(self):
        # --> Static-Server-Info
        return self.c.parse_object(StaticServerInfo)

# first-unused-conf-no [114] (11) Recommended
class ReqFirstUnusedConfNo(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 114\n" % (self.id))

    def parse_response(self):
        # --> Conf-No
        return self.c.parse_int()

# first-unused-text-no [115] (11) Recommended
class ReqFirstUnusedTextNo(Request):
    def __init__(self, c):
        self.register(c)
        c.send_string("%d 115\n" % (self.id))

    def parse_response(self):
        # --> Text-No
        return self.c.parse_int()

# find-next-conf-no [116] (11) Recommended
class ReqFindNextConfNo(Request):
    def __init__(self, c, conf_no):
        self.register(c)
        c.send_string("%d 116 %d\n" % (self.id, conf_no))

    def parse_response(self):
        # --> Conf-No
        return self.c.parse_int()

# find-previous-conf-no [117] (11) Recommended
class ReqFindPreviousConfNo(Request):
    def __init__(self, c, conf_no):
        self.register(c)
        c.send_string("%d 117 %d\n" % (self.id, conf_no))

    def parse_response(self):
        # --> Conf-No
        return self.c.parse_int()

# get-scheduling [118] (11) Experimental
class ReqGetScheduling(Request):
    def __init__(self, c, session_no):
        self.register(c)
        c.send_string("%d 118 %d\n" % (self.id, session_no))

    def parse_response(self):
        # --> SchedulingInfo
        return self.c.parse_object(SchedulingInfo)

# set-scheduling [119] (11) Experimental
class ReqSetScheduling(Request):
    def __init__(self, c, session_no, priority, weight):
        self.register(c)
        c.send_string("%d 119 %d %d %d\n" % (self.id, session_no,
                                             priority, weight))

# set-connection-time-format [120] (11) Recommended
class ReqSetConnectionTimeFormat(Request):
    def __init__(self, c, use_utc):
        self.register(c)
        c.send_string("%d 120 %d\n" %
                      (self.id,
                       use_utc))

# local-to-global-reverse [121] (11) Recommended
class ReqLocalToGlobalReverse(Request):
    def __init__(self, c, conf_no, local_no_ceiling, no_of_existing_texts):
        self.register(c)
        c.send_string("%d 121 %d %d %d\n" % \
                      (self.id, conf_no, local_no_ceiling,
                       no_of_existing_texts))

    def parse_response(self):
        # --> Text-Mapping
        return self.c.parse_object(TextMapping)

# map-created-texts-reverse [122] (11) Recommended
class ReqMapCreatedTextsReverse(Request):
    def __init__(self, c, author, local_no_ceiling, no_of_existing_texts):
        self.register(c)
        c.send_string("%d 122 %d %d %d\n" % \
                      (self.id, author, local_no_ceiling,
                       no_of_existing_texts))

    def parse_response(self):
        # --> Text-Mapping
        return self.c.parse_object(TextMapping)


#
# Classes for asynchronous messages from the server are all
# subclasses of AsyncMessage.
#

class AsyncMessage:
    pass

# async-new-text-old [0] (1) Obsolete (10) <DEFAULT>
ASYNC_NEW_TEXT_OLD = 0
class AsyncNewTextOld(AsyncMessage):
    def parse(self, c):
        self.text_no = c.parse_int()
        self.text_stat = c.parse_old_object(TextStat)

# async-i-am-off [1] (1) Obsolete
# async-i-am-on-onsolete [2] (1) Obsolete

# async-new-name [5] (1) Recommended <DEFAULT>
ASYNC_NEW_NAME = 5
class AsyncNewName(AsyncMessage):
    def parse(self, c):
        self.conf_no = c.parse_int()
        self.old_name = c.parse_string()
        self.new_name = c.parse_string()

# async-i-am-on [6] Recommended
ASYNC_I_AM_ON = 6
class AsyncIAmOn(AsyncMessage):
    def parse(self, c):
        self.info = c.parse_object(WhoInfo)

# async-sync-db [7] (1) Recommended <DEFAULT>
ASYNC_SYNC_DB = 7
class AsyncSyncDB(AsyncMessage):
    def parse(self, c):
        pass

# async-leave-conf [8] (1) Recommended <DEFAULT>
ASYNC_LEAVE_CONF = 8
class AsyncLeaveConf(AsyncMessage):
    def parse(self, c):
        self.conf_no = c.parse_int()

# async-login [9] (1) Recommended <DEFAULT>
ASYNC_LOGIN = 9
class AsyncLogin(AsyncMessage):
    def parse(self, c):
        self.person_no = c.parse_int()
        self.session_no = c.parse_int()

# async-broadcast [10] Obsolete

# async-rejected-connection [11] (1) Recommended <DEFAULT>
ASYNC_REJECTED_CONNECTION = 11
class AsyncRejectedConnection(AsyncMessage):
    def parse(self, c):
        pass

# async-send-message [12] (1) Recommended <DEFAULT>
ASYNC_SEND_MESSAGE = 12
class AsyncSendMessage(AsyncMessage):
    def parse(self, c):
        self.recipient = c.parse_int()
        self.sender = c.parse_int()
        self.message = c.parse_string()

# async-logout [13] (1) Recommended <DEFAULT>
ASYNC_LOGOUT = 13
class AsyncLogout(AsyncMessage):
    def parse(self, c):
        self.person_no = c.parse_int()
        self.session_no = c.parse_int()

# async-deleted-text [14] (10) Recommended
ASYNC_DELETED_TEXT = 14
class AsyncDeletedText(AsyncMessage):
    def parse(self, c):
        self.text_no = c.parse_int()
        self.text_stat = c.parse_object(TextStat)

# async-new-text [15] (10) Recommended
ASYNC_NEW_TEXT = 15
class AsyncNewText(AsyncMessage):
    def parse(self, c):
        self.text_no = c.parse_int()
        self.text_stat = c.parse_object(TextStat)

# async-new-recipient [16] (10) Recommended
ASYNC_NEW_RECIPIENT = 16
class AsyncNewRecipient(AsyncMessage):
    def parse(self, c):
        self.text_no = c.parse_int()
        self.conf_no = c.parse_int()
        self.type = c.parse_int()

# async-sub-recipient [17] (10) Recommended
ASYNC_SUB_RECIPIENT = 17
class AsyncSubRecipient(AsyncMessage):
    def parse(self, c):
        self.text_no = c.parse_int()
        self.conf_no = c.parse_int()
        self.type = c.parse_int()

# async-new-membership [18] (10) Recommended
ASYNC_NEW_MEMBERSHIP = 18
class AsyncNewMembership(AsyncMessage):
    def parse(self, c):
        self.person_no = c.parse_int()
        self.conf_no = c.parse_int()

# async-new-user-area [19] (11) Recommended
ASYNC_NEW_USER_AREA = 19
class AsyncNewUserArea(AsyncMessage):
    def parse(self, c):
        self.person_no = c.parse_int()
        self.old_user_area = c.parse_int()
        self.new_user_area = c.parse_int()

# async-new-presentation [20] (11) Recommended
ASYNC_NEW_PRESENTATION = 20
class AsyncNewPresentation(AsyncMessage):
    def parse(self, c):
        self.conf_no = c.parse_int()
        self.old_presentation = c.parse_int()
        self.new_presentation = c.parse_int()

# async-new-motd [21] (11) Recommended
ASYNC_NEW_MOTD = 21
class AsyncNewMotd(AsyncMessage):
    def parse(self, c):
        self.conf_no = c.parse_int()
        self.old_motd = c.parse_int()
        self.new_motd = c.parse_int()

# async-text-aux-changed [22] (11) Recommended
ASYNC_TEXT_AUX_CHANGED = 22
class AsyncTextAuxChanged(AsyncMessage):
    def parse(self, c):
        self.text_no = c.parse_int()
        self.deleted = c.parse_array(AuxItem)
        self.added = c.parse_array(AuxItem)

async_dict = {
    ASYNC_NEW_TEXT_OLD: AsyncNewTextOld,
    ASYNC_NEW_NAME: AsyncNewName,
    ASYNC_I_AM_ON: AsyncIAmOn,
    ASYNC_SYNC_DB: AsyncSyncDB,
    ASYNC_LEAVE_CONF: AsyncLeaveConf,
    ASYNC_LOGIN: AsyncLogin,
    ASYNC_REJECTED_CONNECTION: AsyncRejectedConnection,
    ASYNC_SEND_MESSAGE: AsyncSendMessage,
    ASYNC_LOGOUT: AsyncLogout,
    ASYNC_DELETED_TEXT: AsyncDeletedText,
    ASYNC_NEW_TEXT: AsyncNewText,
    ASYNC_NEW_RECIPIENT: AsyncNewRecipient,
    ASYNC_SUB_RECIPIENT: AsyncSubRecipient,
    ASYNC_NEW_MEMBERSHIP: AsyncNewMembership,
    ASYNC_NEW_USER_AREA: AsyncNewUserArea,
    ASYNC_NEW_PRESENTATION: AsyncNewPresentation,
    ASYNC_NEW_MOTD: AsyncNewMotd,
    ASYNC_TEXT_AUX_CHANGED: AsyncTextAuxChanged,
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
