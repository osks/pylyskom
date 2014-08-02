# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

from .protocol import (
    MAX_TEXT_SIZE,
    array_of_int_to_string,
    array_to_string,
    to_hstring)

from .datatypes import (
    MIR_TO,
    AnyConfType,
    ArrayAuxItem,
    ArrayDynamicSessionInfo,
    ArrayInt32,
    ArrayLocalTextNo,
    ArrayMark,
    ArrayMember,
    ArrayMembership11,
    ArrayMembership10,
    ArrayStats,
    ArrayConfNo,
    ArrayConfZInfo,
    ConfNo,
    Conference,
    CookedMiscInfo,
    EmptyResponse,
    GarbNice,
    Info,
    InfoType,
    Int8,
    Int16,
    Int32,
    Membership10,
    Membership11,
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

class Request(object):
    CALL_NO = None # Override - Integer protocol request call number.

    def get_request(self):
        """Returns the serialized call parameters.
        """
        # Override and return the request as a string.
        raise NotImplementedError()

    def to_string(self):
        """Returns the full serialized request, including CALL_NO and
        end of line.
        """
        s = "%d" % (self.CALL_NO, )
        request = self.get_request()
        if len(request) > 0:
            s += " " + request
        return s + "\n"


class Argument(object):
    def __init__(self, name, data_type, default=None):
        self.name = name
        self.data_type = data_type
        self.default = default

    def __repr__(self):
        return "Argument({!r}, {!r}, default={!r})".format(
            self.name, self.data_type, self.default)


class NewRequest(Request):
    CALL_NO = None # Override - Integer protocol request call number.
    ARGS = None # Override - List of Argument(s).

    def __init__(self, *args, **kwargs):
        """
        @param *args Arguments supplied in the same order as ARGS.

        @param **kwargs Key-word arguments with the names specified in ARGS.
        """

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
            arg = arg_def.data_type(val)
            setattr(self, arg_def.name, arg)
            self.args.append(arg)
            self._serialized_args.append(arg.to_string())

    def to_string(self):
        """Returns the full serialized request, including CALL_NO and
        end of line.
        """
        return ' '.join(["%d" % (self.CALL_NO, )] + self._serialized_args) + "\n"


# login-old [0] (1) Obsolete (4) Use login (62)

# logout [1] (1) Recommended
class ReqLogout(NewRequest):
    CALL_NO = Requests.LOGOUT
    ARGS = []

# change-conference [2] (1) Recommended
class ReqChangeConference(NewRequest):
    CALL_NO = Requests.CHANGE_CONFERENCE
    ARGS = [ Argument('conf_no', Int16) ]

# change-name [3] (1) Recommended
class ReqChangeName(NewRequest):
    CALL_NO = Requests.CHANGE_NAME
    ARGS = [ Argument('conf_no', Int16),
             Argument('new_name', String) ]

# change-what-i-am-doing [4] (1) Recommended
class ReqChangeWhatIAmDoing(NewRequest):
    CALL_NO = Requests.CHANGE_WHAT_I_AM_DOING
    ARGS = [ Argument('what', String) ]

# create-person-old [5] (1) Obsolete (10) Use create-person (89)
# get-person-stat-old [6] (1) Obsolete (1) Use get-person-stat (49)

# set-priv-bits [7] (1) Recommended
class ReqSetPrivBits(NewRequest):
    CALL_NO = Requests.SET_PRIV_BITS
    ARGS = [ Argument('person', PersNo),
             Argument('privileges', PrivBits) ]

# set-passwd [8] (1) Recommended
class ReqSetPasswd(NewRequest):
    CALL_NO = Requests.SET_PASSWD
    ARGS = [ Argument('person', PersNo),
             Argument('old_pwd', String),
             Argument('new_pwd', String) ]

# query-read-texts-old [9] (1) Obsolete (10) Use query-read-texts (98)
# create-conf-old [10] (1) Obsolete (10) Use create-conf (88)

# delete-conf [11] (1) Recommended
class ReqDeleteConf(NewRequest):
    CALL_NO = Requests.DELETE_CONF
    ARGS = [ Argument('conf', ConfNo) ]

# lookup-name [12] (1) Obsolete (7) Use lookup-z-name (76)
# get-conf-stat-older [13] (1) Obsolete (10) Use get-conf-stat (91)
# add-member-old [14] (1) Obsolete (10) Use add-member (100)

# sub-member [15] (1) Recommended
class ReqSubMember(NewRequest):
    CALL_NO = Requests.SUB_MEMBER
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('pers_no', PersNo) ]

# set-presentation [16] (1) Recommended
class ReqSetPresentation(NewRequest):
    CALL_NO = Requests.SET_PRESENTATION
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('text_no', TextNo) ]

# set-etc-motd [17] (1) Recommended
class ReqSetEtcMoTD(NewRequest):
    CALL_NO = Requests.SET_ETC_MOTD
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('text_no', TextNo) ]

# set-supervisor [18] (1) Recommended
class ReqSetSupervisor(NewRequest):
    CALL_NO = Requests.SET_SUPERVISOR
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('admin', ConfNo) ]

# set-permitted-submitters [19] (1) Recommended
class ReqSetPermittedSubmitters(NewRequest):
    CALL_NO = Requests.SET_PERMITTED_SUBMITTERS
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('perm_sub', ConfNo) ]

# set-super-conf [20] (1) Recommended
class ReqSetSuperConf(NewRequest):
    CALL_NO = Requests.SET_SUPER_CONF
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('super_conf', ConfNo) ]

# set-conf-type [21] (1) Recommended
class ReqSetConfType(NewRequest):
    CALL_NO = Requests.SET_CONF_TYPE
    ARGS = [ Argument('conf_no', ConfNo),
             # We use AnyConfType, which means always sending as
             # ExtendedConfType, even if a ConfType is supplied.
             Argument('conf_type', AnyConfType) ]

# set-garb-nice [22] (1) Recommended
class ReqSetGarbNice(NewRequest):
    CALL_NO = Requests.SET_GARB_NICE
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('nice', GarbNice) ]

# get-marks [23] (1) Recommended
class ReqGetMarks(NewRequest):
    CALL_NO = Requests.GET_MARKS
    ARGS = []

# mark-text-old [24] (1) Obsolete (4) Use mark-text/unmark-text (72/73)

# get-text [25] (1) Recommended
class ReqGetText(NewRequest):
    CALL_NO = Requests.GET_TEXT
    ARGS = [ Argument('text_no', TextNo),
             Argument('start_char', Int32, default=0),
             Argument('end_char', Int32, default=MAX_TEXT_SIZE) ]
    
# get-text-stat-old [26] (1) Obsolete (10) Use get-text-stat (90)

# mark-as-read [27] (1) Recommended
class ReqMarkAsRead(NewRequest):
    CALL_NO = Requests.MARK_AS_READ
    ARGS = [ Argument('conf_no', ConfNo), 
             Argument('texts', ArrayLocalTextNo) ]
                      
# create-text-old [28] (1) Obsolete (10) Use create-text (86)

# delete-text [29] (1) Recommended
class ReqDeleteText(NewRequest):
    CALL_NO = Requests.DELETE_TEXT
    ARGS = [ Argument('text_no', TextNo) ]

# add-recipient [30] (1) Recommended
class ReqAddRecipient(NewRequest):
    CALL_NO = Requests.ADD_RECIPIENT
    ARGS = [ Argument('text_no', TextNo),
             Argument('conf_no', ConfNo),
             Argument('recpt_type', InfoType, default=MIR_TO) ]

# sub-recipient [31] (1) Recommended
class ReqSubRecipient(NewRequest):
    CALL_NO = Requests.SUB_RECIPIENT
    ARGS = [ Argument('text_no', TextNo),
             Argument('conf_no', ConfNo) ]

# add-comment [32] (1) Recommended
class ReqAddComment(NewRequest):
    CALL_NO = Requests.ADD_COMMENT
    ARGS = [ Argument('text_no', TextNo),
             Argument('comment_to', TextNo) ]

# sub-comment [33] (1) Recommended
class ReqSubComment(NewRequest):
    CALL_NO = Requests.SUB_COMMENT
    ARGS = [ Argument('text_no', TextNo),
             Argument('comment_to', TextNo) ]

# get-map [34] (1) Obsolete (10) Use local-to-global (103)

# get-time [35] (1) Recommended
class ReqGetTime(NewRequest):
    CALL_NO = Requests.GET_TIME
    ARGS = []
    
# get-info-old [36] (1) Obsolete (10) Use get-info (94)

# add-footnote [37] (1) Recommended
class ReqAddFootnote(NewRequest):
    CALL_NO = Requests.ADD_FOOTNOTE
    ARGS = [ Argument('text_no', TextNo),
             Argument('footnote_to', TextNo) ]

# sub-footnote [38] (1) Recommended
class ReqSubFootnote(NewRequest):
    CALL_NO = Requests.SUB_FOOTNOTE
    ARGS = [ Argument('text_no', TextNo),
             Argument('footnote_to', TextNo) ]

# who-is-on-old [39] (1) Obsolete (9) Use get-static-session-info (84) and
#                                         who-is-on-dynamic (83)

# set-unread [40] (1) Recommended
class ReqSetUnread(NewRequest):
    CALL_NO = Requests.SET_UNREAD
    ARGS = [ Argument('conf_no', ConfNo),
             Argument('no_of_unread', Int32) ]

# set-motd-of-lyskom [41] (1) Recommended
class ReqSetMoTDOfLysKOM(NewRequest):
    CALL_NO = Requests.SET_MOTD_OF_LYSKOM
    ARGS = [ Argument('text_no', TextNo) ]

# enable [42] (1) Recommended
class ReqEnable(NewRequest):
    CALL_NO = Requests.ENABLE
    ARGS = [ Argument('level', Int8) ]

# sync-kom [43] (1) Recommended
class ReqSyncKOM(NewRequest):
    CALL_NO = Requests.SYNC_KOM
    ARGS = []

# shutdown-kom [44] (1) Recommended
class ReqShutdownKOM(NewRequest):
    CALL_NO = Requests.SHUTDOWN_KOM
    ARGS = [ Argument('exit_val', Int8) ]

# broadcast [45] (1) Obsolete (1) Use send-message (53)
# get-membership-old [46] (1) Obsolete (10) Use get-membership (99)
# get-created-texts [47] (1) Obsolete (10) Use map-created-texts (104)
# get-members-old [48] (1) Obsolete (10) Use get-members (101)

# get-person-stat [49] (1) Recommended
class ReqGetPersonStat(NewRequest):
    CALL_NO = Requests.GET_PERSON_STAT
    ARGS = [ Argument('pers_no', PersNo) ]

# get-conf-stat-old [50] (1) Obsolete (10) Use get-conf-stat (91)

# who-is-on [51] (1) Obsolete (9)  Use who-is-on-dynamic (83) and
#                                      get-static-session-info (84)

# get-unread-confs [52] (1) Recommended
class ReqGetUnreadConfs(NewRequest):
    CALL_NO = Requests.GET_UNREAD_CONFS
    ARGS = [ Argument('pers_no', PersNo) ] 

# send-message [53] (1) Recommended
class ReqSendMessage(Request):
    CALL_NO = Requests.SEND_MESSAGE
    def __init__(self, conf_no, message):
        Request.__init__(self)
        self.conf_no = conf_no
        self.message = message
        
    def get_request(self):
        return "%d %s" % (self.conf_no, to_hstring(self.message))

# get-session-info [54] (1) Obsolete (9) Use who-is-on-dynamic (83)

# disconnect [55] (1) Recommended
class ReqDisconnect(Request):
    CALL_NO = Requests.DISCONNECT
    def __init__(self, session_no):
        Request.__init__(self)
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)

# who-am-i [56] (1) Recommended
class ReqWhoAmI(Request):
    CALL_NO = Requests.WHO_AM_I
    def get_request(self):
        return ""

# set-user-area [57] (2) Recommended
class ReqSetUserArea(Request):
    CALL_NO = Requests.SET_USER_AREA
    def __init__(self, person_no, user_area):
        Request.__init__(self)
        self.person_no = person_no
        self.user_area = user_area
        
    def get_request(self):
        return "%d %d" % (self.person_no, self.user_area)

# get-last-text [58] (3) Recommended
class ReqGetLastText(Request):
    CALL_NO = Requests.GET_LAST_TEXT
    def __init__(self, before):
        Request.__init__(self)
        self.before = before
        
    def get_request(self):
        return "%s" % (self.before.to_string(),)

# create-anonymous-text-old [59] (3) Obsolete (10)
#                                    Use create-anonymous-text (87)

# find-next-text-no [60] (3) Recommended
class ReqFindNextTextNo(Request):
    CALL_NO = Requests.FIND_NEXT_TEXT_NO
    def __init__(self, start):
        Request.__init__(self)
        self.start = start
        
    def get_request(self):
        return "%d" % (self.start,)

# find-previous-text-no [61] (3) Recommended
class ReqFindPreviousTextNo(Request):
    CALL_NO = Requests.FIND_PREVIOUS_TEXT_NO
    def __init__(self, start):
        Request.__init__(self)
        self.start = start
        
    def get_request(self):
        return "%d" % (self.start,)

# login [62] (4) Recommended
class ReqLogin(Request):
    CALL_NO = Requests.LOGIN
    def __init__(self, person_no, password, invisible=1):
        Request.__init__(self)
        self.person_no = person_no
        self.password = password
        self.invisible = invisible
        
    def get_request(self):
        return ("%d %s %d" %
                (self.person_no, to_hstring(self.password), self.invisible))

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
        Request.__init__(self)
        self.client_name = client_name
        self.client_version = client_version
        
    def get_request(self):
        return ("%s %s" % (to_hstring(self.client_name),
                           to_hstring(self.client_version)))

# get-client-name [70] (6) Recommended
class ReqGetClientName(Request):
    CALL_NO = Requests.GET_CLIENT_NAME
    def __init__(self, session_no):
        Request.__init__(self)
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)

# get-client-version [71] (6) Recommended
class ReqGetClientVersion(Request):
    CALL_NO = Requests.GET_CLIENT_VERSION
    def __init__(self, session_no):
        Request.__init__(self)
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)

# mark-text [72] (4) Recommended
class ReqMarkText(Request):
    CALL_NO = Requests.MARK_TEXT
    def __init__(self, text_no, mark_type):
        Request.__init__(self)
        self.text_no = text_no
        
    def get_request(self):
        return "%d %d" % (self.text_no, self.mark_type)

# unmark-text [73] (6) Recommended
class ReqUnmarkText(Request):
    CALL_NO = Requests.UNMARK_TEXT
    def __init__(self, text_no):
        Request.__init__(self)
        self.text_no = text_no
        
    def get_request(self):
        return "%d" % (self.text_no,)

# re-z-lookup [74] (7) Recommended
class ReqReZLookup(Request):
    CALL_NO = Requests.RE_Z_LOOKUP
    def __init__(self, regexp, want_pers=0, want_confs=0):
        Request.__init__(self)
        self.regexp = regexp
        self.want_pers = want_pers
        self.want_confs = want_confs
        
    def get_request(self):
        return "%s %d %d" % (to_hstring(self.regexp), self.want_pers, self.want_confs)

# get-version-info [75] (7) Recommended
class ReqGetVersionInfo(Request):
    CALL_NO = Requests.GET_VERSION_INFO
    def get_request(self):
        return ""

# lookup-z-name [76] (7) Recommended
class ReqLookupZName(Request):
    CALL_NO = Requests.LOOKUP_Z_NAME
    def __init__(self, name, want_pers=0, want_confs=0):
        Request.__init__(self)
        self.name = name
        self.want_pers = want_pers
        self.want_confs = want_confs
        
    def get_request(self):
        return "%s %d %d" % (to_hstring(self.name), self.want_pers,
                             self.want_confs)

# set-last-read [77] (8) Recommended
class ReqSetLastRead(Request):
    CALL_NO = Requests.SET_LAST_READ
    def __init__(self, conf_no, last_read):
        Request.__init__(self)
        self.conf_no = conf_no
        self.last_read = last_read
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.last_read)

# get-uconf-stat [78] (8) Recommended
class ReqGetUconfStat(NewRequest):
    CALL_NO = Requests.GET_UCONF_STAT
    ARGS = [ Argument('conf_no', ConfNo) ]

    def __repr__(self):
        return "ReqGetUconfStat(%d)" % self.conf_no

# set-info [79] (9) Recommended
class ReqSetInfo(Request):
    CALL_NO = Requests.SET_INFO
    def __init__(self, info):
        Request.__init__(self)
        self.info = info
        
    def get_request(self):
        return "%s" % (self.info.to_string(),)

# accept-async [80] (9) Recommended
class ReqAcceptAsync(Request):
    CALL_NO = Requests.ACCEPT_ASYNC
    def __init__(self, request_list):
        Request.__init__(self)
        self.request_list = request_list
        
    def get_request(self):
        return ("%s" % (array_of_int_to_string(self.request_list),))

# query-async [81] (9) Recommended
class ReqQueryAsync(Request):
    CALL_NO = Requests.QUERY_ASYNC
    def get_request(self):
        return ""

# user-active [82] (9) Recommended
class ReqUserActive(Request):
    CALL_NO = Requests.USER_ACTIVE
    def get_request(self):
        return ""

# who-is-on-dynamic [83] (9) Recommended
class ReqWhoIsOnDynamic(Request):
    CALL_NO = Requests.WHO_IS_ON_DYNAMIC
    def __init__(self, want_visible=1, want_invisible=0, active_last=0):
        Request.__init__(self)
        self.want_visible = want_visible
        self.want_invisible = want_invisible
        self.active_last = active_last
        
    def get_request(self):
        return "%d %d %d" % (self.want_visible, self.want_invisible, self.active_last)

# get-static-session-info [84] (9) Recommended
class ReqGetStaticSessionInfo(Request):
    CALL_NO = Requests.GET_STATIC_SESSION_INFO
    def __init__(self, session_no):
        Request.__init__(self)
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)

# get-collate-table [85] (10) Recommended
class ReqGetCollateTable(Request):
    CALL_NO = Requests.GET_COLLATE_TABLE
    def get_request(self):
        return ""

# create-text [86] (10) Recommended
class ReqCreateText(NewRequest):
    CALL_NO = Requests.CREATE_TEXT
    ARGS = [ Argument('text', String),
             Argument('misc_info', CookedMiscInfo),
             Argument('aux_items', ArrayAuxItem) ]

# create-anonymous-text [87] (10) Recommended
class ReqCreateAnonymousText(Request):
    CALL_NO = Requests.CREATE_ANONYMOUS_TEXT
    def __init__(self, text, misc_info, aux_items=[]):
        Request.__init__(self)
        self.text = text
        self.misc_info = misc_info
        self.aux_items = aux_items
        
    def get_request(self):
        return "%s %s %s" % (to_hstring(self.text),
                             self.misc_info.to_string(),
                             array_to_string(self.aux_items))

# create-conf [88] (10) Recommended
class ReqCreateConf(Request):
    CALL_NO = Requests.CREATE_CONF
    def __init__(self, name, conf_type, aux_items=[]):
        Request.__init__(self)
        self.name = name
        self.conf_type = conf_type
        self.aux_items = aux_items
        
    def get_request(self):
        return "%s %s %s" % (to_hstring(self.name),
                             self.conf_type.to_string(),
                             array_to_string(self.aux_items))

# create-person [89] (10) Recommended
class ReqCreatePerson(NewRequest):
    CALL_NO = Requests.CREATE_PERSON
    ARGS = [ Argument('name', String),
             Argument('passwd', String),
             Argument('flags', PersonalFlags),
             Argument('aux_items', ArrayAuxItem) ]

# get-text-stat [90] (10) Recommended
class ReqGetTextStat(Request):
    CALL_NO = Requests.GET_TEXT_STAT
    def __init__(self, text_no):
        Request.__init__(self)
        self.text_no = text_no
        
    def get_request(self):
        return ("%d" % (self.text_no,))

# get-conf-stat [91] (10) Recommended
class ReqGetConfStat(Request):
    CALL_NO = Requests.GET_CONF_STAT
    def __init__(self, conf_no):
        Request.__init__(self)
        self.conf_no = conf_no
        
    def get_request(self):
        return ("%d" % (self.conf_no,))

# modify-text-info [92] (10) Recommended
class ReqModifyTextInfo(Request):
    CALL_NO = Requests.MODIFY_TEXT_INFO
    def __init__(self, text_no, delete, add):
        Request.__init__(self)
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
        Request.__init__(self)
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

# modify-system-info [95] (10) Recommended
class ReqModifySystemInfo(Request):
    CALL_NO = Requests.MODIFY_SYSTEM_INFO
    def __init__(self, delete, add):
        Request.__init__(self)
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

# set-expire [97] (10) Experimental
class ReqSetExpire(Request):
    CALL_NO = Requests.SET_EXPIRE
    def __init__(self, conf_no, expire):
        Request.__init__(self)
        self.conf_no = conf_no
        self.expire = expire
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.expire)

# query-read-texts-10 [98] (10) Obsolete (11) Use query-read-texts (107)
class ReqQueryReadTexts10(Request):
    CALL_NO = Requests.QUERY_READ_TEXTS_10
    def __init__(self, person_no, conf_no):
        Request.__init__(self)
        self.person_no = person_no
        self.conf_no = conf_no
        
    def get_request(self):
        return "%d %d" % (self.person_no, self.conf_no)

# get-membership-10 [99] (10) Obsolete (11) Use get-membership (108)

class ReqGetMembership10(Request):
    CALL_NO = Requests.GET_MEMBERSHIP_10
    def __init__(self, person_no, first, no_of_confs, want_read_texts):
        Request.__init__(self)
        self.person_no = person_no
        self.first = first
        self.no_of_confs = no_of_confs
        self.want_read_texts = want_read_texts
        
    def get_request(self):
        return "%d %d %d %d" % (self.person_no, self.first,
                                self.no_of_confs, self.want_read_texts)

# add-member [100] (10) Recommended
class ReqAddMember(Request):
    CALL_NO = Requests.ADD_MEMBER
    def __init__(self, conf_no, person_no, priority, where, membership_type):
        Request.__init__(self)
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
        Request.__init__(self)
        self.conf_no = conf_no
        self.first = first
        self.no_of_members = no_of_members
        
        
    def get_request(self):
        return "%d %d %d" % (self.conf_no, self.first, self.no_of_members)

# set-membership-type [102] (10) Recommended
class ReqSetMembershipType(Request):
    CALL_NO = Requests.SET_MEMBERSHIP_TYPE
    def __init__(self, person_no, conf_no, membership_type):
        Request.__init__(self)
        self.person_no = person_no
        self.conf_no = conf_no
        self.membership_type = membership_type
        
    def get_request(self):
        return "%d %d %s" % (self.person_no, self.conf_no, self.membership_type.to_string())

# local-to-global [103] (10) Recommended
class ReqLocalToGlobal(Request):
    CALL_NO = Requests.LOCAL_TO_GLOBAL
    def __init__(self, conf_no, first_local_no, no_of_existing_texts):
        Request.__init__(self)
        self.conf_no = conf_no
        self.first_local_no = first_local_no
        self.no_of_existing_texts = no_of_existing_texts
        
    def get_request(self):
        return ("%d %d %d" % (self.conf_no, self.first_local_no, 
                              self.no_of_existing_texts))

# map-created-texts [104] (10) Recommended
class ReqMapCreatedTexts(Request):
    CALL_NO = Requests.MAP_CREATED_TEXTS
    def __init__(self, author, first_local_no, no_of_existing_texts):
        Request.__init__(self)
        self.author = author
        self.first_local_no = first_local_no
        self.no_of_existing_texts = no_of_existing_texts
        
    def get_request(self):
        return "%d %d %d" % (self.author, self.first_local_no, self.no_of_existing_texts)

# set-keep-commented [105] (11) Recommended (10) Experimental
class ReqSetKeepCommented(Request):
    CALL_NO = Requests.SET_KEEP_COMMENTED
    def __init__(self, conf_no, keep_commented):
        Request.__init__(self)
        self.conf_no = conf_no
        self.keep_commented = keep_commented
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.keep_commented)

# set-pers-flags [106] (10) Recommended

class ReqSetPersFlags(Request):
    def __init__(self, person_no, flags):
        Request.__init__(self)
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
        Request.__init__(self)
        self.person_no = person_no
        self.conf_no = conf_no
        self.want_read_ranges = want_read_ranges
        self.max_ranges = max_ranges
        
    def get_request(self):
        return ("%d %d %d %d" % (self.person_no, self.conf_no,
                                 self.want_read_ranges,
                                 self.max_ranges))

    def __repr__(self):
        return "ReqQueryReadTexts11(%d, %d, %d, %d)" % (self.person_no, self.conf_no,
                                                        self.want_read_ranges,
                                                        self.max_ranges)

ReqQueryReadTexts = ReqQueryReadTexts11

# get-membership [108] (11) Recommended
class ReqGetMembership11(Request):
    CALL_NO = Requests.GET_MEMBERSHIP
    def __init__(self, person_no, first, no_of_confs,
                 want_read_ranges, max_ranges):
        Request.__init__(self)
        self.person_no = person_no
        self.first = first
        self.no_of_confs = no_of_confs
        self.want_read_ranges = want_read_ranges
        self.max_ranges = max_ranges
        
    def get_request(self):
        return "%d %d %d %d %d" % (self.person_no,
                                   self.first, self.no_of_confs,
                                   self.want_read_ranges, self.max_ranges)

ReqGetMembership = ReqGetMembership11

# mark-as-unread [109] (11) Recommended
class ReqMarkAsUnread(Request):
    CALL_NO = Requests.MARK_AS_UNREAD
    def __init__(self, conf_no, text_no):
        Request.__init__(self)
        self.conf_no = conf_no
        self.text_no = text_no
        
    def get_request(self):
        return "%d %d" % (self.conf_no, self.text_no)

# set-read-ranges [110] (11) Recommended
class ReqSetReadRanges(Request):
    CALL_NO = Requests.SET_READ_RANGES
    def __init__(self, conf_no, read_ranges):
        Request.__init__(self)
        self.conf_no = conf_no
        self.read_ranges = read_ranges
        
    def get_request(self):
        return "%s %s" % (self.conf_no, array_to_string(self.read_ranges))

# get-stats-description [111] (11) Recommended
class ReqGetStatsDescription(Request):
    CALL_NO = Requests.GET_STATS_DESCRIPTION
    def get_request(self):
        return ""

# get-stats [112] (11) Recommended
class ReqGetStats(Request):
    CALL_NO = Requests.GET_STATS
    def __init__(self, what):
        Request.__init__(self)
        self.what = what
        
    def get_request(self):
        return "%s" % (to_hstring(self.what),)

# get-boottime-info [113] (11) Recommended
class ReqGetBoottimeInfo(Request):
    CALL_NO = Requests.GET_BOOTTIME_INFO
    def get_request(self):
        return ""

# first-unused-conf-no [114] (11) Recommended
class ReqFirstUnusedConfNo(Request):
    CALL_NO = Requests.FIRST_UNUSED_CONF_NO
    def get_request(self):
        return ""

# first-unused-text-no [115] (11) Recommended
class ReqFirstUnusedTextNo(Request):
    CALL_NO = Requests.FIRST_UNUSED_TEXT_NO
    def get_request(self):
        return ""

# find-next-conf-no [116] (11) Recommended
class ReqFindNextConfNo(Request):
    CALL_NO = Requests.FIND_NEXT_CONF_NO
    def __init__(self, conf_no):
        Request.__init__(self)
        self.conf_no = conf_no
        
    def get_request(self):
        return "%d" % (self.conf_no,)

# find-previous-conf-no [117] (11) Recommended
class ReqFindPreviousConfNo(Request):
    CALL_NO = Requests.FIND_PREVIOUS_CONF_NO
    def __init__(self, conf_no):
        Request.__init__(self)
        self.conf_no = conf_no
        
    def get_request(self):
        return "%d" % (self.conf_no,)

# get-scheduling [118] (11) Experimental
class ReqGetScheduling(Request):
    CALL_NO = Requests.GET_SCHEDULING
    def __init__(self, session_no):
        Request.__init__(self)
        self.session_no = session_no
        
    def get_request(self):
        return "%d" % (self.session_no,)

# set-scheduling [119] (11) Experimental
class ReqSetScheduling(Request):
    CALL_NO = Requests.SET_SCHEDULING
    def __init__(self, session_no, priority, weight):
        Request.__init__(self)
        self.session_no = session_no
        self.prority = priority
        self.weight = weight
        
    def get_request(self):
        return "%d %d %d" % (self.session_no, self.priority, self.weight)

# set-connection-time-format [120] (11) Recommended
class ReqSetConnectionTimeFormat(Request):
    CALL_NO = Requests.SET_CONNECTION_TIME_FORMAT
    def __init__(self, use_utc):
        Request.__init__(self)
        self.use_utc = use_utc
        
    def get_request(self):
        return "%d" % (self.use_utc,)

# local-to-global-reverse [121] (11) Recommended
class ReqLocalToGlobalReverse(Request):
    CALL_NO = Requests.LOCAL_TO_GLOBAL_REVERSE
    def __init__(self, conf_no, local_no_ceiling, no_of_existing_texts):
        Request.__init__(self)
        self.conf_no = conf_no
        self.local_no_ceiling = local_no_ceiling
        self.no_of_existing_texts = no_of_existing_texts
        
    def get_request(self):
        return "%d %d %d" % (self.conf_no, self.local_no_ceiling, self.no_of_existing_texts)

# map-created-texts-reverse [122] (11) Recommended
class ReqMapCreatedTextsReverse(Request):
    CALL_NO = Requests.MAP_CREATED_TEXTS_REVERSE
    def __init__(self, author, local_no_ceiling, no_of_existing_texts):
        Request.__init__(self)
        self.author = author
        self.local_no_ceiling = local_no_ceiling
        self.no_of_existing_texts = no_of_existing_texts
        
    def get_request(self):
        return "%d %d %d" % (self.author, self.local_no_ceiling, self.no_of_existing_texts)





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
