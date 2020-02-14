# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

from typing import Optional, List

from .protocol import MAX_TEXT_SIZE

from .datatypes import (
    MIR_TO,
    AnyConfType,
    ArrayAuxItemInput,
    ArrayDynamicSessionInfo,
    ArrayInt32,
    ArrayLocalTextNo,
    ArrayMark,
    ArrayMember,
    ArrayMembership11,
    ArrayMembership10,
    ArrayReadRange,
    ArrayStats,
    ArrayConfNo,
    ArrayConfZInfo,
    AuxNo,
    Bool,
    ConfNo,
    Conference,
    CookedMiscInfo,
    EmptyResponse,
    GarbNice,
    Info,
    InfoType,
    InfoOld,
    Int8,
    Int16,
    Int32,
    LocalTextNo,
    Membership10,
    Membership11,
    MembershipType,
    PersNo,
    Person,
    PersonalFlags,
    PrivBits,
    SchedulingInfo,
    SessionNo,
    StaticServerInfo,
    StaticSessionInfo,
    StatsDescription,
    String,
    TextList,
    TextMapping,
    TextNo,
    TextStat,
    Time,
    UConference,
    VersionInfo)


class Requests(object):
    """Enum like object which give names to the request call numbers
    in the protocol.
    """
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

class Argument(object):
    def __init__(self, name, data_type, default=None):
        self.name = name
        self.data_type = data_type
        self.default = default

    def __repr__(self):
        return "Argument({!r}, {!r}, default={!r})".format(
            self.name, self.data_type, self.default)


class Request(object):
    CALL_NO: Optional[int] = None # Override - Integer protocol request call number.
    ARGS: Optional[List[Argument]] = None # Override - List of Argument(s).

    def __init__(self, *args, **kwargs):
        """
        @param *args Arguments supplied in the same order as ARGS.

        @param **kwargs Key-word arguments with the names specified in ARGS.
        """
        if self.CALL_NO is None:
            raise TypeError("Must have CALL_NO")

        if self.ARGS is None:
            raise TypeError("Must have ARGS")

        args_count = len(self.ARGS)
        given_args = len(args)
        given_kwargs = len(kwargs)
        given_total = given_args + given_kwargs
        if given_total > args_count:
            raise TypeError("Takes at most {:d} arguments ({:d} given)".format(
                    args_count, given_total))

        self.args = []
        self._serialized_args = []
        for i, arg_def in enumerate(self.ARGS):
            if i < given_args:
                val = args[i]
                if arg_def.name in kwargs:
                    raise TypeError("Argument {} specified both "
                                    "as positional and keyword argument".format(
                            arg_def.name))
            else:
                if arg_def.name in kwargs:
                    val = kwargs[arg_def.name]
                else:
                    if arg_def.default is None:
                        raise TypeError("Argument {} is missing".format(arg_def.name))
                    else:
                        val = arg_def.default

            assert not hasattr(self, arg_def.name), "Invalid argument name"

            # FIXME. This calls the constructor of the datatype with
            # the value as argument.  this might make sense for
            # converting ints and strings to Int32 and String (and
            # similar), but not for complex types, which are expected
            # to be passed as an argument already. In those cases it
            # will just call the constructor of the datatype class
            # with an instance of that type.
            #
            # TODO: call a classmethod on the types instead of the
            # constructor.
            arg = arg_def.data_type(val)

            setattr(self, arg_def.name, arg)
            self.args.append(arg)
            self._serialized_args.append(arg.to_string())

    # TODO: Rename to "to_bytes"
    def to_string(self):
        """Returns the full serialized request, including CALL_NO and
        end of line. To bytes.
        """
        return b' '.join([b"%d" % (self.CALL_NO, )] + self._serialized_args) + b"\n"


    def __repr__(self):
        cls_name = type(self).__name__
        arg_values = []
        for i, arg_def in enumerate(self.ARGS):
            arg_values.append("{}={!r}".format(arg_def.name, self.args[i]))
        return "{cls_name}({args})".format(
            cls_name=cls_name,
            args=", ".join(arg_values))


# login-old [0] (1) Obsolete (4) Use login (62)

# logout [1] (1) Recommended
class ReqLogout(Request):
    CALL_NO = Requests.LOGOUT
    ARGS: List[Argument] = []

# change-conference [2] (1) Recommended
class ReqChangeConference(Request):
    CALL_NO = Requests.CHANGE_CONFERENCE
    ARGS = [ Argument('conf_no', Int16) ]

# change-name [3] (1) Recommended
class ReqChangeName(Request):
    CALL_NO = Requests.CHANGE_NAME
    ARGS = [ Argument('conf_no', Int16),
             Argument('new_name', String) ]

# change-what-i-am-doing [4] (1) Recommended
class ReqChangeWhatIAmDoing(Request):
    CALL_NO = Requests.CHANGE_WHAT_I_AM_DOING
    ARGS = [ Argument('what', String) ]

# create-person-old [5] (1) Obsolete (10) Use create-person (89)
# get-person-stat-old [6] (1) Obsolete (1) Use get-person-stat (49)

# set-priv-bits [7] (1) Recommended
class ReqSetPrivBits(Request):
    CALL_NO = Requests.SET_PRIV_BITS
    ARGS = [ Argument('person', PersNo),
             Argument('privileges', PrivBits) ]

# set-passwd [8] (1) Recommended
class ReqSetPasswd(Request):
    CALL_NO = Requests.SET_PASSWD
    ARGS = [ Argument('person', PersNo),
             Argument('old_pwd', String),
             Argument('new_pwd', String) ]

# query-read-texts-old [9] (1) Obsolete (10) Use query-read-texts (98)
# create-conf-old [10] (1) Obsolete (10) Use create-conf (88)

# delete-conf [11] (1) Recommended
class ReqDeleteConf(Request):
    CALL_NO = Requests.DELETE_CONF
    ARGS = [ Argument('conf', ConfNo) ]

# lookup-name [12] (1) Obsolete (7) Use lookup-z-name (76)
# get-conf-stat-older [13] (1) Obsolete (10) Use get-conf-stat (91)
# add-member-old [14] (1) Obsolete (10) Use add-member (100)

# sub-member [15] (1) Recommended
class ReqSubMember(Request):
    CALL_NO = Requests.SUB_MEMBER
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('pers_no', PersNo) ]

# set-presentation [16] (1) Recommended
class ReqSetPresentation(Request):
    CALL_NO = Requests.SET_PRESENTATION
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('text_no', TextNo) ]

# set-etc-motd [17] (1) Recommended
class ReqSetEtcMoTD(Request):
    CALL_NO = Requests.SET_ETC_MOTD
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('text_no', TextNo) ]

# set-supervisor [18] (1) Recommended
class ReqSetSupervisor(Request):
    CALL_NO = Requests.SET_SUPERVISOR
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('admin', ConfNo) ]

# set-permitted-submitters [19] (1) Recommended
class ReqSetPermittedSubmitters(Request):
    CALL_NO = Requests.SET_PERMITTED_SUBMITTERS
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('perm_sub', ConfNo) ]

# set-super-conf [20] (1) Recommended
class ReqSetSuperConf(Request):
    CALL_NO = Requests.SET_SUPER_CONF
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('super_conf', ConfNo) ]

# set-conf-type [21] (1) Recommended
class ReqSetConfType(Request):
    CALL_NO = Requests.SET_CONF_TYPE
    ARGS = [ Argument('conf_no', ConfNo),
             # We use AnyConfType, which means always sending as
             # ExtendedConfType, even if a ConfType is supplied.
             Argument('conf_type', AnyConfType) ]

# set-garb-nice [22] (1) Recommended
class ReqSetGarbNice(Request):
    CALL_NO = Requests.SET_GARB_NICE
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('nice', GarbNice) ]

# get-marks [23] (1) Recommended
class ReqGetMarks(Request):
    CALL_NO = Requests.GET_MARKS
    ARGS: List[Argument] = []

# mark-text-old [24] (1) Obsolete (4) Use mark-text/unmark-text (72/73)

# get-text [25] (1) Recommended
class ReqGetText(Request):
    CALL_NO = Requests.GET_TEXT
    ARGS = [ Argument('text_no', TextNo),
             Argument('start_char', Int32, default=0),
             Argument('end_char', Int32, default=MAX_TEXT_SIZE) ]
    
# get-text-stat-old [26] (1) Obsolete (10) Use get-text-stat (90)

# mark-as-read [27] (1) Recommended
class ReqMarkAsRead(Request):
    CALL_NO = Requests.MARK_AS_READ
    ARGS = [ Argument('conf_no', ConfNo), 
             Argument('texts', ArrayLocalTextNo) ]
                      
# create-text-old [28] (1) Obsolete (10) Use create-text (86)

# delete-text [29] (1) Recommended
class ReqDeleteText(Request):
    CALL_NO = Requests.DELETE_TEXT
    ARGS = [ Argument('text_no', TextNo) ]

# add-recipient [30] (1) Recommended
class ReqAddRecipient(Request):
    CALL_NO = Requests.ADD_RECIPIENT
    ARGS = [ Argument('text_no', TextNo),
             Argument('conf_no', ConfNo),
             Argument('recpt_type', InfoType, default=MIR_TO) ]

# sub-recipient [31] (1) Recommended
class ReqSubRecipient(Request):
    CALL_NO = Requests.SUB_RECIPIENT
    ARGS = [ Argument('text_no', TextNo),
             Argument('conf_no', ConfNo) ]

# add-comment [32] (1) Recommended
class ReqAddComment(Request):
    CALL_NO = Requests.ADD_COMMENT
    ARGS = [ Argument('text_no', TextNo),
             Argument('comment_to', TextNo) ]

# sub-comment [33] (1) Recommended
class ReqSubComment(Request):
    CALL_NO = Requests.SUB_COMMENT
    ARGS = [ Argument('text_no', TextNo),
             Argument('comment_to', TextNo) ]

# get-map [34] (1) Obsolete (10) Use local-to-global (103)

# get-time [35] (1) Recommended
class ReqGetTime(Request):
    CALL_NO = Requests.GET_TIME
    ARGS: List[Argument] = []

# get-info-old [36] (1) Obsolete (10) Use get-info (94)

# add-footnote [37] (1) Recommended
class ReqAddFootnote(Request):
    CALL_NO = Requests.ADD_FOOTNOTE
    ARGS = [ Argument('text_no', TextNo),
             Argument('footnote_to', TextNo) ]

# sub-footnote [38] (1) Recommended
class ReqSubFootnote(Request):
    CALL_NO = Requests.SUB_FOOTNOTE
    ARGS = [ Argument('text_no', TextNo),
             Argument('footnote_to', TextNo) ]

# who-is-on-old [39] (1) Obsolete (9) Use get-static-session-info (84) and
#                                         who-is-on-dynamic (83)

# set-unread [40] (1) Recommended
class ReqSetUnread(Request):
    CALL_NO = Requests.SET_UNREAD
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('no_of_unread', Int32) ]

# set-motd-of-lyskom [41] (1) Recommended
class ReqSetMoTDOfLysKOM(Request):
    CALL_NO = Requests.SET_MOTD_OF_LYSKOM
    ARGS = [ Argument('text_no', TextNo) ]

# enable [42] (1) Recommended
class ReqEnable(Request):
    CALL_NO = Requests.ENABLE
    ARGS = [ Argument('level', Int8) ]

# sync-kom [43] (1) Recommended
class ReqSyncKOM(Request):
    CALL_NO = Requests.SYNC_KOM
    ARGS: List[Argument] = []

# shutdown-kom [44] (1) Recommended
class ReqShutdownKOM(Request):
    CALL_NO = Requests.SHUTDOWN_KOM
    ARGS = [ Argument('exit_val', Int8) ]

# broadcast [45] (1) Obsolete (1) Use send-message (53)
# get-membership-old [46] (1) Obsolete (10) Use get-membership (99)
# get-created-texts [47] (1) Obsolete (10) Use map-created-texts (104)
# get-members-old [48] (1) Obsolete (10) Use get-members (101)

# get-person-stat [49] (1) Recommended
class ReqGetPersonStat(Request):
    CALL_NO = Requests.GET_PERSON_STAT
    ARGS = [ Argument('pers_no', PersNo) ]

# get-conf-stat-old [50] (1) Obsolete (10) Use get-conf-stat (91)

# who-is-on [51] (1) Obsolete (9)  Use who-is-on-dynamic (83) and
#                                      get-static-session-info (84)

# get-unread-confs [52] (1) Recommended
class ReqGetUnreadConfs(Request):
    CALL_NO = Requests.GET_UNREAD_CONFS
    ARGS = [ Argument('pers_no', PersNo) ] 

# send-message [53] (1) Recommended
class ReqSendMessage(Request):
    CALL_NO = Requests.SEND_MESSAGE
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('message', String) ]

# get-session-info [54] (1) Obsolete (9) Use who-is-on-dynamic (83)

# disconnect [55] (1) Recommended
class ReqDisconnect(Request):
    CALL_NO = Requests.DISCONNECT
    ARGS = [ Argument('session_no', SessionNo) ]

# who-am-i [56] (1) Recommended
class ReqWhoAmI(Request):
    CALL_NO = Requests.WHO_AM_I
    ARGS: List[Argument] = []

# set-user-area [57] (2) Recommended
class ReqSetUserArea(Request):
    CALL_NO = Requests.SET_USER_AREA
    ARGS = [ Argument('pers_no', PersNo),
             Argument('user_area', TextNo) ]

# get-last-text [58] (3) Recommended
class ReqGetLastText(Request):
    CALL_NO = Requests.GET_LAST_TEXT
    ARGS = [ Argument('before', Time) ]

# create-anonymous-text-old [59] (3) Obsolete (10)
#                                    Use create-anonymous-text (87)

# find-next-text-no [60] (3) Recommended
class ReqFindNextTextNo(Request):
    CALL_NO = Requests.FIND_NEXT_TEXT_NO
    ARGS = [ Argument('start', TextNo) ]

# find-previous-text-no [61] (3) Recommended
class ReqFindPreviousTextNo(Request):
    CALL_NO = Requests.FIND_PREVIOUS_TEXT_NO
    ARGS = [ Argument('start', TextNo) ]

# login [62] (4) Recommended
class ReqLogin(Request):
    CALL_NO = Requests.LOGIN
    ARGS = [ Argument('person', PersNo),
             Argument('password', String),
             Argument('invisible', Bool, default=1) ]

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
    ARGS = [ Argument('client_name', String),
             Argument('client_version', String) ]

# get-client-name [70] (6) Recommended
class ReqGetClientName(Request):
    CALL_NO = Requests.GET_CLIENT_NAME
    ARGS = [ Argument('session_no', SessionNo) ]

# get-client-version [71] (6) Recommended
class ReqGetClientVersion(Request):
    CALL_NO = Requests.GET_CLIENT_VERSION
    ARGS = [ Argument('session_no', SessionNo) ]

# mark-text [72] (4) Recommended
class ReqMarkText(Request):
    CALL_NO = Requests.MARK_TEXT
    ARGS = [ Argument('text_no', TextNo),
             Argument('mark_type', Int8) ]

# unmark-text [73] (6) Recommended
class ReqUnmarkText(Request):
    CALL_NO = Requests.UNMARK_TEXT
    ARGS = [ Argument('text_no', TextNo) ]

# re-z-lookup [74] (7) Recommended
class ReqReZLookup(Request):
    CALL_NO = Requests.RE_Z_LOOKUP
    ARGS = [ Argument('regexp', String),
             Argument('want_persons', Bool),
             Argument('want_confs', Bool) ]

# get-version-info [75] (7) Recommended
class ReqGetVersionInfo(Request):
    CALL_NO = Requests.GET_VERSION_INFO
    ARGS: List[Argument] = []

# lookup-z-name [76] (7) Recommended
class ReqLookupZName(Request):
    CALL_NO = Requests.LOOKUP_Z_NAME
    ARGS = [ Argument('name', String),
             Argument('want_pers', Bool),
             Argument('want_confs', Bool) ]

# set-last-read [77] (8) Recommended
class ReqSetLastRead(Request):
    CALL_NO = Requests.SET_LAST_READ
    ARGS = [ Argument('conference', ConfNo),
             Argument('last_read', LocalTextNo) ]

# get-uconf-stat [78] (8) Recommended
class ReqGetUconfStat(Request):
    CALL_NO = Requests.GET_UCONF_STAT
    ARGS = [ Argument('conf_no', ConfNo) ]

# set-info [79] (9) Recommended
class ReqSetInfo(Request):
    CALL_NO = Requests.SET_INFO
    ARGS = [ Argument('info', InfoOld) ]

# accept-async [80] (9) Recommended
class ReqAcceptAsync(Request):
    CALL_NO = Requests.ACCEPT_ASYNC
    ARGS = [ Argument('request_list', ArrayInt32) ]

# query-async [81] (9) Recommended
class ReqQueryAsync(Request):
    CALL_NO = Requests.QUERY_ASYNC
    ARGS: List[Argument] = []

# user-active [82] (9) Recommended
class ReqUserActive(Request):
    CALL_NO = Requests.USER_ACTIVE
    ARGS: List[Argument] = []

# who-is-on-dynamic [83] (9) Recommended
class ReqWhoIsOnDynamic(Request):
    CALL_NO = Requests.WHO_IS_ON_DYNAMIC
    ARGS = [ Argument('want_visible', Bool),
             Argument('want_invisible', Bool),
             Argument('active_last', Int32) ]

# get-static-session-info [84] (9) Recommended
class ReqGetStaticSessionInfo(Request):
    CALL_NO = Requests.GET_STATIC_SESSION_INFO
    ARGS = [ Argument('session_no', SessionNo) ]

# get-collate-table [85] (10) Recommended
class ReqGetCollateTable(Request):
    CALL_NO = Requests.GET_COLLATE_TABLE
    ARGS: List[Argument] = []

# create-text [86] (10) Recommended
class ReqCreateText(Request):
    CALL_NO = Requests.CREATE_TEXT
    ARGS = [ Argument('text', String),
             Argument('misc_info', CookedMiscInfo),
             Argument('aux_items', ArrayAuxItemInput) ]

# create-anonymous-text [87] (10) Recommended
class ReqCreateAnonymousText(Request):
    CALL_NO = Requests.CREATE_ANONYMOUS_TEXT
    ARGS = [ Argument('text', String),
             Argument('misc_info', CookedMiscInfo),
             Argument('aux_items', ArrayAuxItemInput) ]

# create-conf [88] (10) Recommended
class ReqCreateConf(Request):
    CALL_NO = Requests.CREATE_CONF
    ARGS = [ Argument('name', String),
             Argument('type', AnyConfType),
             Argument('aux_items', ArrayAuxItemInput) ]

# create-person [89] (10) Recommended
class ReqCreatePerson(Request):
    CALL_NO = Requests.CREATE_PERSON
    ARGS = [ Argument('name', String),
             Argument('passwd', String),
             Argument('flags', PersonalFlags),
             Argument('aux_items', ArrayAuxItemInput) ]

# get-text-stat [90] (10) Recommended
class ReqGetTextStat(Request):
    CALL_NO = Requests.GET_TEXT_STAT
    ARGS = [ Argument('text_no', TextNo) ]

# get-conf-stat [91] (10) Recommended
class ReqGetConfStat(Request):
    CALL_NO = Requests.GET_CONF_STAT
    ARGS = [ Argument('conf_no', ConfNo) ]

# modify-text-info [92] (10) Recommended
class ReqModifyTextInfo(Request):
    CALL_NO = Requests.MODIFY_TEXT_INFO
    ARGS = [ Argument('text', TextNo),
             Argument('delete', AuxNo),
             Argument('add', ArrayAuxItemInput) ]

# modify-conf-info [93] (10) Recommended
class ReqModifyConfInfo(Request):
    CALL_NO = Requests.MODIFY_CONF_INFO
    ARGS = [ Argument('conf', ConfNo),
             Argument('delete', AuxNo),
             Argument('add', ArrayAuxItemInput) ]

# get-info [94] (10) Recommended
class ReqGetInfo(Request):
    CALL_NO = Requests.GET_INFO
    ARGS: List[Argument] = []

# modify-system-info [95] (10) Recommended
class ReqModifySystemInfo(Request):
    CALL_NO = Requests.MODIFY_SYSTEM_INFO
    ARGS = [ Argument('items_to_delete', AuxNo),
             Argument('items_to_add', ArrayAuxItemInput) ]

# query-predefined-aux-items [96] (10) Recommended
class ReqQueryPredefinedAuxItems(Request):
    CALL_NO = Requests.QUERY_PREDEFINED_AUX_ITEMS
    ARGS: List[Argument] = []

# set-expire [97] (10) Experimental
class ReqSetExpire(Request):
    CALL_NO = Requests.SET_EXPIRE
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('expire', GarbNice) ]

# query-read-texts-10 [98] (10) Obsolete (11) Use query-read-texts (107)
class ReqQueryReadTexts10(Request):
    CALL_NO = Requests.QUERY_READ_TEXTS_10
    ARGS = [ Argument('person', PersNo),
             Argument('conference', ConfNo) ]

# get-membership-10 [99] (10) Obsolete (11) Use get-membership (108)

class ReqGetMembership10(Request):
    CALL_NO = Requests.GET_MEMBERSHIP_10
    ARGS = [ Argument('person', PersNo),
             Argument('first', Int16),
             Argument('no_of_confs', Int16),
             Argument('want_read_texts', Bool) ]

# add-member [100] (10) Recommended
class ReqAddMember(Request):
    CALL_NO = Requests.ADD_MEMBER
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('pers_no', PersNo),
             Argument('priority', Int8),
             Argument('where', Int16),
             Argument('type', MembershipType) ]

# get-members [101] (10) Recommended
class ReqGetMembers(Request):
    CALL_NO = Requests.GET_MEMBERS
    ARGS = [ Argument('conf', ConfNo),
             Argument('first', Int16),
             Argument('no_of_members', Int16) ]

# set-membership-type [102] (10) Recommended
class ReqSetMembershipType(Request):
    CALL_NO = Requests.SET_MEMBERSHIP_TYPE
    ARGS = [ Argument('pers', PersNo),
             Argument('conf', ConfNo),
             Argument('type', MembershipType) ]

# local-to-global [103] (10) Recommended
class ReqLocalToGlobal(Request):
    CALL_NO = Requests.LOCAL_TO_GLOBAL
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('first_local_no', LocalTextNo),
             Argument('no_of_existing_texts', Int32) ]

# map-created-texts [104] (10) Recommended
class ReqMapCreatedTexts(Request):
    CALL_NO = Requests.MAP_CREATED_TEXTS
    ARGS = [ Argument('author', PersNo),
             Argument('first_local_no', LocalTextNo),
             Argument('no_of_existing_texts', Int32) ]

# set-keep-commented [105] (11) Recommended (10) Experimental
class ReqSetKeepCommented(Request):
    CALL_NO = Requests.SET_KEEP_COMMENTED
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('keep_commented', GarbNice) ]

# set-pers-flags [106] (10) Recommended

class ReqSetPersFlags(Request):
    CALL_NO = Requests.SET_PERS_FLAGS
    ARGS = [ Argument('pers_no', PersNo),
             Argument('flags', PersonalFlags) ]

### --- New in protocol version 11 ---

# query-read-texts [107] (11) Recommended
class ReqQueryReadTexts11(Request):
    CALL_NO = Requests.QUERY_READ_TEXTS
    ARGS = [ Argument('person', PersNo),
             Argument('conference', ConfNo),
             Argument('want_read_ranges', Bool),
             Argument('max_ranges', Int32) ]

ReqQueryReadTexts = ReqQueryReadTexts11

# get-membership [108] (11) Recommended
class ReqGetMembership11(Request):
    CALL_NO = Requests.GET_MEMBERSHIP
    ARGS = [ Argument('person', PersNo),
             Argument('first', Int16),
             Argument('no_of_confs', Int16),
             Argument('want_read_ranges', Bool),
             Argument('max_ranges', Int32) ]

ReqGetMembership = ReqGetMembership11

# mark-as-unread [109] (11) Recommended
class ReqMarkAsUnread(Request):
    CALL_NO = Requests.MARK_AS_UNREAD
    ARGS = [ Argument('conference', ConfNo),
             Argument('text', LocalTextNo) ]

# set-read-ranges [110] (11) Recommended
class ReqSetReadRanges(Request):
    CALL_NO = Requests.SET_READ_RANGES
    ARGS = [ Argument('conference', ConfNo),
             Argument('read_ranges', ArrayReadRange) ]

# get-stats-description [111] (11) Recommended
class ReqGetStatsDescription(Request):
    CALL_NO = Requests.GET_STATS_DESCRIPTION
    ARGS: List[Argument] = []

# get-stats [112] (11) Recommended
class ReqGetStats(Request):
    CALL_NO = Requests.GET_STATS
    ARGS = [ Argument('what', String) ]

# get-boottime-info [113] (11) Recommended
class ReqGetBoottimeInfo(Request):
    CALL_NO = Requests.GET_BOOTTIME_INFO
    ARGS: List[Argument] = []

# first-unused-conf-no [114] (11) Recommended
class ReqFirstUnusedConfNo(Request):
    CALL_NO = Requests.FIRST_UNUSED_CONF_NO
    ARGS: List[Argument] = []

# first-unused-text-no [115] (11) Recommended
class ReqFirstUnusedTextNo(Request):
    CALL_NO = Requests.FIRST_UNUSED_TEXT_NO
    ARGS: List[Argument] = []

# find-next-conf-no [116] (11) Recommended
class ReqFindNextConfNo(Request):
    CALL_NO = Requests.FIND_NEXT_CONF_NO
    ARGS = [ Argument('start', ConfNo) ]

# find-previous-conf-no [117] (11) Recommended
class ReqFindPreviousConfNo(Request):
    CALL_NO = Requests.FIND_PREVIOUS_CONF_NO
    ARGS = [ Argument('start', ConfNo) ]

# get-scheduling [118] (11) Experimental
class ReqGetScheduling(Request):
    CALL_NO = Requests.GET_SCHEDULING
    ARGS = [ Argument('session_no', SessionNo) ]

# set-scheduling [119] (11) Experimental
class ReqSetScheduling(Request):
    CALL_NO = Requests.SET_SCHEDULING
    ARGS = [ Argument('session_no', SessionNo),
             Argument('priority', Int16),
             Argument('weight', Int16) ]

# set-connection-time-format [120] (11) Recommended
class ReqSetConnectionTimeFormat(Request):
    CALL_NO = Requests.SET_CONNECTION_TIME_FORMAT
    ARGS = [ Argument('use_utc', Bool) ]

# local-to-global-reverse [121] (11) Recommended
class ReqLocalToGlobalReverse(Request):
    CALL_NO = Requests.LOCAL_TO_GLOBAL_REVERSE
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('local_no_ceiling', LocalTextNo),
             Argument('no_of_existing_texts', Int32) ]

# map-created-texts-reverse [122] (11) Recommended
class ReqMapCreatedTextsReverse(Request):
    CALL_NO = Requests.MAP_CREATED_TEXTS_REVERSE
    ARGS = [ Argument('author', PersNo),
             Argument('local_no_ceiling', LocalTextNo),
             Argument('no_of_existing_texts', Int32) ]



# Mapping from request type to response type.
response_dict = {
    Requests.ACCEPT_ASYNC: EmptyResponse,
    Requests.ADD_COMMENT: EmptyResponse,
    Requests.ADD_FOOTNOTE: EmptyResponse,
    Requests.ADD_MEMBER: EmptyResponse,
    Requests.ADD_RECIPIENT: EmptyResponse,
    Requests.CHANGE_CONFERENCE: EmptyResponse,
    Requests.CHANGE_NAME: EmptyResponse,
    Requests.CHANGE_WHAT_I_AM_DOING: EmptyResponse,
    Requests.CREATE_ANONYMOUS_TEXT: TextNo,
    Requests.CREATE_CONF: ConfNo,
    Requests.CREATE_PERSON: PersNo,
    Requests.CREATE_TEXT: TextNo,
    Requests.DELETE_CONF: EmptyResponse,
    Requests.DELETE_TEXT: EmptyResponse,
    Requests.DISCONNECT: EmptyResponse,
    Requests.ENABLE: EmptyResponse,
    Requests.FIND_NEXT_CONF_NO: ConfNo,
    Requests.FIND_NEXT_TEXT_NO: TextNo,
    Requests.FIND_PREVIOUS_CONF_NO: ConfNo,
    Requests.FIND_PREVIOUS_TEXT_NO: TextNo,
    Requests.FIRST_UNUSED_CONF_NO: ConfNo,
    Requests.FIRST_UNUSED_TEXT_NO: TextNo,
    Requests.GET_BOOTTIME_INFO: StaticServerInfo,
    Requests.GET_CLIENT_NAME: String,
    Requests.GET_CLIENT_VERSION: String,
    Requests.GET_COLLATE_TABLE: String,
    Requests.GET_CONF_STAT: Conference,
    Requests.GET_INFO: EmptyResponse,
    Requests.GET_INFO: Info,
    Requests.GET_LAST_TEXT: TextNo,
    Requests.GET_MAP: TextList,
    Requests.GET_MARKS: ArrayMark,
    Requests.GET_MEMBERS: ArrayMember,
    Requests.GET_MEMBERSHIP: ArrayMembership11,
    Requests.GET_MEMBERSHIP_10: ArrayMembership10,
    Requests.GET_PERSON_STAT: Person,
    Requests.GET_SCHEDULING: SchedulingInfo,
    Requests.GET_STATIC_SESSION_INFO: StaticSessionInfo,
    Requests.GET_STATS: ArrayStats,
    Requests.GET_STATS_DESCRIPTION: StatsDescription,
    Requests.GET_TEXT: String,
    Requests.GET_TEXT_STAT: TextStat,
    Requests.GET_TIME: Time,
    Requests.GET_UCONF_STAT: UConference,
    Requests.GET_UNREAD_CONFS: ArrayConfNo,
    Requests.GET_VERSION_INFO: VersionInfo,
    Requests.LOCAL_TO_GLOBAL: TextMapping,
    Requests.LOCAL_TO_GLOBAL_REVERSE: TextMapping,
    Requests.LOGIN: EmptyResponse,
    Requests.LOGOUT: EmptyResponse,
    Requests.LOOKUP_Z_NAME: ArrayConfZInfo,
    Requests.MAP_CREATED_TEXTS: TextMapping,
    Requests.MAP_CREATED_TEXTS_REVERSE: TextMapping,
    Requests.MARK_AS_READ: EmptyResponse,
    Requests.MARK_AS_UNREAD: EmptyResponse,
    Requests.MARK_TEXT: EmptyResponse,
    Requests.MODIFY_CONF_INFO: EmptyResponse,
    Requests.MODIFY_SYSTEM_INFO: EmptyResponse,
    Requests.MODIFY_TEXT_INFO: EmptyResponse,
    Requests.QUERY_ASYNC: ArrayInt32,
    Requests.QUERY_PREDEFINED_AUX_ITEMS: ArrayInt32,
    Requests.QUERY_READ_TEXTS: Membership11,
    Requests.QUERY_READ_TEXTS_10: Membership10,
    Requests.RE_Z_LOOKUP: ArrayConfZInfo,
    Requests.SEND_MESSAGE: EmptyResponse,
    Requests.SET_CLIENT_VERSION: EmptyResponse,
    Requests.SET_CONF_TYPE: EmptyResponse,
    Requests.SET_CONNECTION_TIME_FORMAT: EmptyResponse,
    Requests.SET_ETC_MOTD: EmptyResponse,
    Requests.SET_EXPIRE: EmptyResponse,
    Requests.SET_GARB_NICE: EmptyResponse,
    Requests.SET_INFO: EmptyResponse,
    Requests.SET_KEEP_COMMENTED: EmptyResponse,
    Requests.SET_LAST_READ: EmptyResponse,
    Requests.SET_MEMBERSHIP_TYPE: EmptyResponse,
    Requests.SET_MOTD_OF_LYSKOM: EmptyResponse,
    Requests.SET_PASSWD: EmptyResponse,
    Requests.SET_PERMITTED_SUBMITTERS: EmptyResponse,
    Requests.SET_PERS_FLAGS: EmptyResponse,
    Requests.SET_PRESENTATION: EmptyResponse,
    Requests.SET_PRIV_BITS: EmptyResponse,
    Requests.SET_READ_RANGES: EmptyResponse,
    Requests.SET_SCHEDULING: EmptyResponse,
    Requests.SET_SUPERVISOR: EmptyResponse,
    Requests.SET_SUPER_CONF: EmptyResponse,
    Requests.SET_UNREAD: EmptyResponse,
    Requests.SET_USER_AREA: EmptyResponse,
    Requests.SHUTDOWN_KOM: EmptyResponse,
    Requests.SUB_COMMENT: EmptyResponse,
    Requests.SUB_FOOTNOTE: EmptyResponse,
    Requests.SUB_MEMBER: EmptyResponse,
    Requests.SUB_RECIPIENT: EmptyResponse,
    Requests.SYNC_KOM: EmptyResponse,
    Requests.UNMARK_TEXT: EmptyResponse,
    Requests.USER_ACTIVE: EmptyResponse,
    Requests.WHO_AM_I: SessionNo,
    Requests.WHO_IS_ON_DYNAMIC: ArrayDynamicSessionInfo,
}
