# -*- coding: iso-8859-1 -*-

import socket
import select

import kom


class Requests(object):
    """Used as an enum.
    """
    (AcceptAsync,
     AddMember,
     ChangeConference,
     CreateConf,
     CreatePerson,
     CreateText,
     Disconnect,
     GetCollateTable,
     GetConfStat,
     GetMarks,
     GetMembership,
     GetMembership11,
     GetPersonStat,
     GetText,
     GetTextStat,
     GetUconfStat,
     GetUnreadConfs,
     LocalToGlobal,
     LocalToGlobalReverse,
     Login,
     Logout,
     LookupZName,
     MarkAsRead,
     MarkAsUnread,
     MarkText,
     QueryReadTexts,
     QueryReadTexts11,
     ReZLookup,
     SetClientVersion,
     SetConnectionTimeFormat,
     SetUnread,
     SetUserArea,
     SubMember,
     UnmarkText,
     UserActive,
     WhoAmI) = range(36) # UPDATE WHEN ADDING/REMOVING VALUES.
    # range() is used to make sure that each "enum type" get a different value


_kom_request_to_class = {
    Requests.AcceptAsync: kom.ReqAcceptAsync,
    Requests.AddMember: kom.ReqAddMember,
    Requests.ChangeConference: kom.ReqChangeConference,
    Requests.CreateConf: kom.ReqCreateConf,
    Requests.CreatePerson: kom.ReqCreatePerson,
    Requests.CreateText: kom.ReqCreateText,
    Requests.Disconnect: kom.ReqDisconnect,
    Requests.GetCollateTable: kom.ReqGetCollateTable,
    Requests.GetConfStat: kom.ReqGetConfStat,
    Requests.GetMarks: kom.ReqGetMarks,
    Requests.GetMembership11: kom.ReqGetMembership11,
    Requests.GetMembership: kom.ReqGetMembership11,
    Requests.GetPersonStat: kom.ReqGetPersonStat,
    Requests.GetText: kom.ReqGetText,
    Requests.GetTextStat: kom.ReqGetTextStat,
    Requests.GetUconfStat: kom.ReqGetUconfStat,
    Requests.GetUnreadConfs: kom.ReqGetUnreadConfs,
    Requests.LocalToGlobal: kom.ReqLocalToGlobal,
    Requests.LocalToGlobalReverse: kom.ReqLocalToGlobalReverse,
    Requests.Login: kom.ReqLogin,
    Requests.Logout: kom.ReqLogout,
    Requests.LookupZName: kom.ReqLookupZName,
    Requests.MarkAsRead: kom.ReqMarkAsRead,
    Requests.MarkAsUnread: kom.ReqMarkAsUnread,
    Requests.MarkText: kom.ReqMarkText,
    Requests.QueryReadTexts11: kom.ReqQueryReadTexts11,
    Requests.QueryReadTexts: kom.ReqQueryReadTexts11,
    Requests.ReZLookup: kom.ReqReZLookup,
    Requests.SetClientVersion: kom.ReqSetClientVersion,
    Requests.SetConnectionTimeFormat: kom.ReqSetConnectionTimeFormat,
    Requests.SetUnread: kom.ReqSetUnread,
    Requests.SubMember: kom.ReqSubMember,
    Requests.SetUserArea: kom.ReqSetUserArea,
    Requests.UnmarkText: kom.ReqUnmarkText,
    Requests.UserActive: kom.ReqUserActive,
    Requests.WhoAmI: kom.ReqWhoAmI,
    # ... todo ...
}

class RequestFactory(object):
    def __init__(self, mapping):
        self.mapping = mapping

    def new(self, request):
        assert request in self.mapping
        return self.mapping[request]

default_request_factory = RequestFactory(_kom_request_to_class)


#
# CLASS for a connection
#

class Connection(object):
    # INITIALIZATION ETC.

    def __init__(self, request_factory=default_request_factory):
        self._rfactory = request_factory
        self.socket = None
        
        # Requests
        self.req_id = 0      # Last used ID (i.e. increment before use)
        self.req_queue = {}  # Requests sent to server, waiting for answers
        self.resp_queue = {} # Answers received from the server
        self.error_queue = {} # Errors received from the server
        self.req_histo = None # Histogram of request types
        
        # Receive buffer
        self.rb = ""    # Buffer for data received from socket
        self.rb_len = 0 # Length of the buffer
        self.rb_pos = 0 # Position of first unread byte in buffer

        # Asynchronous message handlers
        self.async_handlers = {}

    def request(self, request, *args, **kwargs):
        return self._rfactory.new(request)(self, *args, **kwargs)
    
    def connect(self, host, port = 4894, user = "", localbind=None):
        # Remember the host and port for later identification of sessions
        self.host = host
        self.port = port
        
        # Create socket and connect
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if None != localbind:
            self.socket.bind(localbind)
        self.socket.connect((self.host, self.port))

        # Send initial string 
        self.send_string(("A%dH%s\n" % (len(user), user)).encode('latin1'))

        # Wait for answer "LysKOM\n"
        resp = self.receive_string(7) # FIXME: receive line here
        if resp != "LysKOM\n":
            raise kom.BadInitialResponse

    # ASYNCHRONOUS MESSAGES HANDLERS
    
    def add_async_handler(self, msg_no, handler, skip_accept_async=False):
        if msg_no not in kom.async_dict:
            raise kom.UnimplementedAsync
        if msg_no in self.async_handlers:
            self.async_handlers[msg_no].append(handler)
        else:
            self.async_handlers[msg_no] = [handler]
            if not skip_accept_async:
                self.request(Requests.AcceptAsync, self.async_handlers.keys())

    # REQUEST QUEUE
    
    # Allocate an ID for a request and register it in the queue
    def register_request(self, req):
        self.req_id = self.req_id +1
        self.req_queue[self.req_id] = req
        if self.req_histo is not None:
            name =  req.__class__.__name__
            try:
                self.req_histo[name] = self.req_histo[name] + 1
            except KeyError:
                self.req_histo[name] = 1
        return self.req_id

    # Wait for a request to be answered, return response or signal error
    def wait_and_dequeue(self, id):
        while id not in self.resp_queue and \
              id not in self.error_queue:
            #print "Request", id,"not responded to, getting some more"
            self.parse_server_message()
        if id in self.resp_queue:
            # Response
            ret = self.resp_queue[id]
            del self.resp_queue[id]
            return ret
        else:
            # Error
            (error_no, error_status) = self.error_queue[id]
            del self.error_queue[id]
            raise kom.error_dict[error_no](error_status)

    # Parse all present data
    def parse_present_data(self):
        while select.select([self.socket], [], [], 0)[0]:
            ch = self.receive_char()
            if ch in kom.WHITESPACE:
                continue
            if ch == "=":
                self.parse_response()
            elif ch == "%":
                self.parse_error()
            elif ch == ":":
                self.parse_asynchronous_message()
            else:
                raise kom.ProtocolError
            
    # Enable request histogram
    def enable_req_histo(self):
        self.req_histo = {}
        
    # Show request histogram
    def show_req_histo(self):
        l = [(-x[1], x[0]) for x in list(self.req_histo.items())]
        l.sort()
        print("Count  Request")
        for (negcount, name) in l:
            print("%5d: %s" % (-negcount, name))
    
    # PARSING SERVER MESSAGES

    # Parse one server message
    # Could be: - answer to request (begins with =)
    #           - error for request (begins with %)
    #           - asynchronous message (begins with :)
    
    def parse_server_message(self):
        ch = self.parse_first_non_ws()
        if ch == "=":
            self.parse_response()
        elif ch == "%":
            self.parse_error()
        elif ch == ":":
            self.parse_asynchronous_message()
        else:
            raise kom.ProtocolError

    # Parse response
    def parse_response(self):
        id = self.parse_int()
        #print "Response for",id,"coming"
        if id in self.req_queue:
            # Delegate parsing to the ReqXXXX class
            resp = self.req_queue[id].parse_response()
            # Remove request and add response
            del self.req_queue[id]
            self.resp_queue[id] = resp
        else:
            raise kom.BadRequestId(id)

    # Parse error
    def parse_error(self):
        id = self.parse_int()
        error_no = self.parse_int()
        error_status = self.parse_int()
        if id in self.req_queue:
            # Remove request and add error
            del self.req_queue[id]
            self.error_queue[id] = (error_no, error_status)
        else:
            raise kom.BadRequestId(id)

    # Parse asynchronous message
    def parse_asynchronous_message(self):
        self.parse_int() # read no_args
        msg_no = self.parse_int()

        if msg_no in kom.async_dict:
            msg = kom.async_dict[msg_no]()
            msg.parse(self)
            if msg_no in self.async_handlers:
                for handler in self.async_handlers[msg_no]:
                    handler(msg,self)
        else:
            raise kom.UnimplementedAsync(msg_no)
        
    # PARSING KOM DATA TYPES

    def parse_object(self, classname):
        obj = classname()
        obj.parse(self)
        return obj

    def parse_old_object(self, classname):
        obj = classname()
        obj.parse(self, old_format=1)
        return obj
        
    # PARSING ARRAYS

    def parse_array(self, element_class):
        len = self.parse_int()
        res = []
        if len > 0:
            left = self.parse_first_non_ws()
            if left == "*":
                # Special case of unwanted data
                return []
            elif left != "{": raise kom.ProtocolError
            for i in range(0, len):
                obj = element_class()
                obj.parse(self)
                res.append(obj)
            right = self.parse_first_non_ws()
            if right != "}": raise kom.ProtocolError
        else:
            star = self.parse_first_non_ws()
            if star != "*": raise kom.ProtocolError
        return res

    def array_to_string(self, array):
        return "%d { %s }" % (len(array), 
                              " ".join([x.to_string() for x in array]))
                             
    def parse_array_of_basictype(self, basic_type_parser):
        len = self.parse_int()
        res = []
        if len > 0:
            left = self.parse_first_non_ws()
            if left == "*":
                # Special case of unwanted data
                return []
            elif left != "{": raise kom.ProtocolError
            for i in range(0, len):
                res.append(basic_type_parser())
            right = self.parse_first_non_ws()
            if right != "}": raise kom.ProtocolError
        else:
            star = self.parse_first_non_ws()
            if star != "*": raise kom.ProtocolError
        return res

    def parse_array_of_int(self):
        return self.parse_array_of_basictype(self.parse_int)

    def array_of_int_to_string(self, array):
        return "%d { %s }" % (len(array),
                             " ".join(list(map(str, array))))
                             
    def parse_array_of_string(self):
        return self.parse_array_of_basictype(self.parse_string)

    # PARSING BITSTRINGS
    def parse_bitstring(self, len):
        res = []
        char = self.parse_first_non_ws()
        for i in range(0,len):
            if char == "0":
                res.append(0)
            elif char == "1":
                res.append(1)
            else:
                raise kom.ProtocolError
            char = self.receive_char()
        return res

    # PARSING BASIC DATA TYPES

    # Skip whitespace and return first non-ws character
    def parse_first_non_ws(self):
        c = self.receive_char()
        while c in kom.WHITESPACE:
            c = self.receive_char()
        return c

    # Get an integer and next character from the receive buffer
    def parse_int_and_next(self):
        c = self.parse_first_non_ws()
        n = 0
        while c in kom.DIGITS:
            n = n * 10 + (ord(c) - kom.ORD_0)
            c = self.receive_char()
        return (n, c)
    
    # Get an integer from the receive buffer (discard next character)
    def parse_int(self):
        (c, n) = self.parse_int_and_next()
        return c

    # Get a float from the receive buffer (discard next character)
    def parse_float(self):
        c = self.parse_first_non_ws()
        digs = []
        while c in kom.FLOAT_CHARS:
            digs.append(c)
            c = self.receive_char()
        return float("".join(digs))
    
    # Parse a string (Hollerith notation)
    def parse_string(self):
        (len, h) = self.parse_int_and_next()
        if h != "H": raise kom.ProtocolError
        return self.receive_string(len)
    
    # LOW LEVEL ROUTINES FOR SENDING AND RECEIVING

    # Send a raw string
    def send_string(self, s):
        #print(">>>",s)
        while len(s) > 0:
            done = self.socket.send(s)
            s = s[done:]

    # Ensure that there are at least N bytes in the receive buffer
    # FIXME: Rewrite for speed and clarity
    def ensure_receive_buffer_size(self, size):
        present = self.rb_len - self.rb_pos 
        while present < size:
            needed = size - present
            wanted = max(needed,128) # FIXME: Optimize
            #print "Only %d chars present, need %d: asking for %d" % \
            #      (present, size, wanted)
            data = self.socket.recv(wanted)
            if len(data) == 0: raise kom.ReceiveError
            #print("<<<", data)
            self.rb = self.rb[self.rb_pos:] + data
            self.rb_pos = 0
            self.rb_len = len(self.rb)
            present = self.rb_len
        #print "%d chars present (needed %d)" % \
        #      (present, size)
            
    # Get a string from the receive buffer (receiving more if necessary)
    def receive_string(self, len):
        self.ensure_receive_buffer_size(len)
        res = self.rb[self.rb_pos:self.rb_pos+len]
        self.rb_pos = self.rb_pos + len
        return res

    # Get a character from the receive buffer (receiving more if necessary)
    # FIXME: Optimize for speed
    def receive_char(self):
        self.ensure_receive_buffer_size(1)
        res = self.rb[self.rb_pos]
        self.rb_pos = self.rb_pos + 1
        return res


#
# CLASS for a connection with...
# * Caches for:
#   - UConference
#   - Conference
#   - Person
#   - TextStat 
#   - Subjects
#   No negative caching. No time-outs.
#   Some automatic invalidation (if accept-async called appropriately).
#
# * Lookup function (conference/person name -> numbers)
# * Helper function get_unread_texts to get a list of local and global
#   numbers of all unread text in a conference for a person

class CachedConnection(Connection):
    def __init__(self, request_factory=default_request_factory):
        Connection.__init__(self, request_factory)

    def connect(self, host, port = 4894, user = "", localbind=None):
        Connection.connect(self, host, port, user, localbind)
        
        # Caches
        #
        # TODO: Instead of exposing these dictionary like cache
        # objects, we could override the request method in the
        # Connection class, and call the cache objects if the request
        # type matches the cache. Then we could have a the same
        # interface as Connection, which makes it easier to use and
        # test (fewer methods). IMPORTANT: It would however make it
        # less clear that we might get a cached response and that
        # could be dangerous. Sometime it is okay with cached
        # responses, and sometimes it is not. How can we make it
        # possible to force no cached?
        self.uconferences = Cache(self.fetch_uconference, "UConference")
        self.conferences = Cache(self.fetch_conference, "Conference")
        self.persons = Cache(self.fetch_person, "Person")
        self.textstats = Cache(self.fetch_textstat, "TextStat")

        # Setup up async handlers for invalidating cache entries. Skip
        # sending accept-async until the last call.
        self.add_async_handler(kom.ASYNC_NEW_NAME, self.cah_new_name, True)
        self.add_async_handler(kom.ASYNC_LEAVE_CONF, self.cah_leave_conf, True)
        self.add_async_handler(kom.ASYNC_DELETED_TEXT, self.cah_deleted_text, True)
        self.add_async_handler(kom.ASYNC_NEW_TEXT, self.cah_new_text, True)
        self.add_async_handler(kom.ASYNC_NEW_RECIPIENT, self.cah_new_recipient, True)
        self.add_async_handler(kom.ASYNC_SUB_RECIPIENT, self.cah_sub_recipient, True)
        self.add_async_handler(kom.ASYNC_NEW_MEMBERSHIP, self.cah_new_membership)

    # Fetching functions (internal use)
    def fetch_uconference(self, no):
        return self.request(Requests.GetUconfStat, no).response()

    def fetch_conference(self, no):
        return self.request(Requests.GetConfStat, no).response()

    def fetch_person(self, no):
        return self.request(Requests.GetPersonStat, no).response()

    def fetch_textstat(self, no):
        return self.request(Requests.GetTextStat, no).response()

    # Handlers for asynchronous messages (internal use)
    # FIXME: Most of these handlers should do more clever things than just
    # invalidating. 
    def cah_new_name(self, msg, c):
        # A new name makes uconferences[].name invalid
        self.uconferences.invalidate(msg.conf_no)
        # A new name makes conferences[].name invalid
        self.conferences.invalidate(msg.conf_no)

    def cah_leave_conf(self, msg, c):
        # Leaving a conference makes conferences[].no_of_members invalid
        self.conferences.invalidate(msg.conf_no)

    def cah_deleted_text(self, msg, c):
        # Deletion of a text makes conferences[].no_of_texts invalid
        ts = msg.text_stat
        for rcpt in ts.misc_info.recipient_list:
            self.conferences.invalidate(rcpt.recpt)
            
    def cah_new_text(self, msg, c):
        # A new text. conferences[].no_of_texts and
        # uconferences[].highest_local_no is invalid. Also invalidates
        # the textstats for the commented texts.
        for rcpt in msg.text_stat.misc_info.recipient_list:
            self.conferences.invalidate(rcpt.recpt)
            self.uconferences.invalidate(rcpt.recpt)
        for ct in msg.text_stat.misc_info.comment_to_list:
            self.textstats.invalidate(ct.text_no)
        # FIXME: A new text makes persons[author].no_of_created_texts invalid

    def cah_new_recipient(self, msg, c):
        # Just like a new text; conferences[].no_of_texts and
        # uconferences[].highest_local_no gets invalid. 
        self.conferences.invalidate(msg.conf_no)
        self.uconferences.invalidate(msg.conf_no)
        # textstats.misc_info_recipient_list gets invalid as well.
        self.textstats.invalidate(msg.text_no)

    def cah_sub_recipient(self, msg, c):
        # Invalid conferences[].no_of_texts
        self.conferences.invalidate(msg.conf_no)
        # textstats.misc_info_recipient_list gets invalid as well.
        self.textstats.invalidate(msg.text_no)

    def cah_new_membership(self, msg, c):
        # Joining a conference makes conferences[].no_of_members invalid
        self.conferences.invalidate(msg.conf_no)

    # Report cache usage
    def report_cache_usage(self):
        self.uconferences.report()
        self.conferences.report()
        self.persons.report()
        self.textstats.report()

    # Common operation: get name of conference (via uconference)
    def conf_name(self, conf_no, default = "", include_no = 0):
        try:
            conf_name = self.uconferences[conf_no].name.decode('latin1')
            if include_no:
                return "%s (#%d)" % (conf_name, conf_no)
            else:
                return conf_name
        except:
            if default.find("%d") != -1:
                return default % conf_no
            else:
                return default

    # Lookup function (name -> (list of tuples(no, name))
    # Special case: "#number" is not looked up
    def lookup_name(self, name, want_pers, want_confs):
        if name[:1] == "#":
            # Numerical case
            try:
                no = int(name[1:]) # Exception if not int
                type = self.uconferences[no].type # Exception if not found
                name = self.uconferences[no].name.decode('latin1')
                if (want_pers and type.letterbox) or \
                   (want_confs and (not type.letterbox)):
                    return [(no, name)]
                else:
                    return []
            except:
                return []
        else:
            # Alphabetical case
            matches = self.request(
                Requests.LookupZName, 
                name,
                want_pers = want_pers,
                want_confs = want_confs).response()
            return [(x.conf_no, x.name.decode('latin1')) for x in matches]

    def regexp_lookup(self, regexp, want_pers, want_confs,
                      case_sensitive=0):
        """Lookup name using regular expression"""
        if regexp.startswith("#"):
            return self.lookup_name(regexp, want_pers, want_confs)
        
        if not case_sensitive:
            regexp = self._case_insensitive_regexp(regexp)

        matches = self.request(
            Requests.ReZLookup,
            regexp,
            want_pers = want_pers,
            want_confs = want_confs).response()
        return [(x.conf_no, x.name.decode('latin1')) for x in matches]

    def _case_insensitive_regexp(self, regexp):
        """Make regular expression case insensitive"""
        result = ""
        # FIXME: Cache collate_table
        collate_table = self.request(Requests.GetCollateTable).response()
        inside_brackets = 0
        for c in regexp:
            if c == "[":
                inside_brackets = 1

            if inside_brackets:
                eqv_chars = c
            else:
                eqv_chars = self._equivalent_chars(c, collate_table)
                
            if len(eqv_chars) > 1:
                result += "[%s]" % eqv_chars
            else:
                result += eqv_chars

            if c == "]":
                inside_brackets = 0

        return result

    def _equivalent_chars(self, c, collate_table):
        """Find all chars equivalent to c in collate table"""
        c_ord = ord(c)
        if c_ord >= len(collate_table):
            return c

        result = ""
        norm_char = collate_table[c_ord]
        next_index = 0
        while 1:
            next_index = collate_table.find(norm_char, next_index)
            if next_index == -1:
                break
            result += chr(next_index)
            next_index += 1

        return result

    def read_ranges_to_gaps_and_last(self, read_ranges):
        """Return all texts excluded from read_ranges.
        
        @return: Returns a 2-tuple of a list and the first possibly
        unread text number after the last read range. The text number
        could be larger than the highest local number, if we have read
        everything in the conference. The list contains a 2-tuples for
        each gap in the read ranges, where each tuple is the first
        unread text in the gap and the length of the gap.
        """
        gaps = []
        last = 1
        for read_range in read_ranges:
            gap = read_range.first_read - last
            if gap > 0:
                gaps.append((last, gap))
            last = read_range.last_read + 1
        return gaps, last

    def get_unread_texts_from_membership(self, membership):
        unread = []
        
        more_to_fetch = 1
        gaps, last = self.read_ranges_to_gaps_and_last(membership.read_ranges)
        for first, gap_len in gaps:
            first_local = first
            while gap_len > 0:
                if gap_len > 255:
                    n = 255
                else:
                    n = gap_len
                gap_len -= n
                try:
                    mapping = self.request(
                        Requests.LocalToGlobal, membership.conference, first_local, n).response()
                    unread.extend([e[1] for e in mapping.list if e[1] != 0])
                    first_local = mapping.range_end
                    more_to_fetch = mapping.later_texts_exists
                except kom.NoSuchLocalText:
                    more_to_fetch = 0
        
        # If there are more than 255 after the last read range, we
        # need to continue mapping (the last, if any, previous call
        # will have set later_texts_exists to 1 if so).
        first_local = last
        while more_to_fetch:
            try:
                mapping = self.request(
                    Requests.LocalToGlobal, membership.conference, first_local, 255).response()
                unread.extend([e[1] for e in mapping.list if e[1] != 0])
                first_local = mapping.range_end
                more_to_fetch = mapping.later_texts_exists
            except kom.NoSuchLocalText:
                # No unread texts
                more_to_fetch = 0
        
        # Remove text that don't exist anymore (text_no == 0)
        return [ text_no for text_no in unread if text_no != 0]

    def mark_text(self, text_no, mark_type):
        self.request(Requests.MarkText, text_no, mark_type).response()
        # textstat.misc_info.no_of_marks is now invalid
        self.textstats.invalidate(text_no)

    def unmark_text(self, text_no):
        self.request(Requests.UnmarkText, text_no).response()
        # textstat.misc_info.no_of_marks is now invalid
        self.textstats.invalidate(text_no)


class CachedPersonConnection(CachedConnection):
    def __init__(self, request_factory=default_request_factory):
        CachedConnection.__init__(self, request_factory)

        # Current person number
        self._pers_no = 0
        
        # Current conference (change-conference)
        self._current_conference_no = 0
        
        # Caches
        self._memberships = Cache(self.fetch_membership, "Membership")
        
        # Specific membership cache where the keys are the positions
        # in the membership list for the membership, and the values
        # are the memberships. There is a risk with having this cache
        # - you can modify positions and we currently have no way of
        # detecting that (no async messages).
        self._memberships_by_position = dict()

    def login(self, pers_no, password):
        self.request(Requests.Login, pers_no, password, invisible=0).response()
        # We need to know the current person to be able to have and
        # invalidate caches.
        self._pers_no = pers_no

    def logout(self):
        self.request(Requests.Logout).response()
        # Invalidate caches that are/were for the current person
        self._pers_no = 0
        self._memberships_by_position = dict()
        self._memberships.invalidate_all()

    def get_person_no(self):
        return self._pers_no

    def is_logged_in(self):
        return self._pers_no != 0

    def change_conference(self, conf_no):
        # When changing conference, the lyskom server will update
        # last-time-read for the membership of the *previous*
        # conference. This means that we need to keep track of the
        # current conference to be able to invalidate the membership
        # correctly.
        prev_conf_no = self._current_conference_no
        self.request(Requests.ChangeConference, conf_no).response()
        self._current_conference_no = conf_no
        if prev_conf_no != 0:
            self._invalidate_membership(prev_conf_no)

    def mark_as_read_local(self, conf_no, local_text_no):
        try:
            self.request(Requests.MarkAsRead, conf_no, [local_text_no]).response()
        except kom.NotMember:
            pass

    def mark_as_unread_local(self, conf_no, local_text_no):
        try:
            self.request(Requests.MarkAsUnread, conf_no, local_text_no).response()
        except kom.NotMember:
            pass

    def _get_cached_memberships_by_position(self, first, no_of_confs):
        # Return a list of the cached memberships if we have all of
        # them, otherwise return None. We only return memberships if
        # we had all of them.
        memberships = []
        for pos in range(first, first + no_of_confs):
            if pos not in self._memberships_by_position:
                return None
            memberships.append(self._memberships_by_position[pos])
        return memberships

    def _update_cached_memberships_by_position(self, memberships):
        for m in memberships:
            self._memberships_by_position[m.position] = m
    
    def _invalidate_membership(self, conf_no):
        self._memberships.invalidate(conf_no)
        # Since we only return anything from memberships_by_position
        # if all memberships are found, it means that we can make
        # partial invalidations.
        found_at = None
        for pos in self._memberships_by_position:
            if self._memberships_by_position[pos].conference == conf_no:
                found_at = pos
                break
        if found_at is not None:
            del self._memberships_by_position[found_at]
    
    def get_memberships(self, pers_no, first, no_of_confs, want_read_ranges=False):
        """Get memberships for a person.
        """
        if want_read_ranges:
            return self.request(
                Requests.GetMembership11, pers_no, 0, no_of_confs, 1, 0).response()
        else:
            if pers_no == self._pers_no:
                # We cache the result for the current person and without
                # read ranges, because that is what we can invalidate
                # correctly.
                memberships = self._get_cached_memberships_by_position(first, no_of_confs)
                if memberships is None:
                    memberships = self.request(
                        Requests.GetMembership11,
                        self._pers_no, first, no_of_confs, 0, 0).response()
                    self._update_cached_memberships_by_position(memberships)
                return memberships
            else:
                return self.request(
                    Requests.GetMembership11, pers_no, 0, no_of_confs, 0, 0).response()

    def get_membership(self, pers_no, conf_no, want_read_ranges=False):
        """Get a membership for a person
        """
        if want_read_ranges:
            return self.request(Requests.QueryReadTexts, pers_no, conf_no, 1, 0).response()
        else:
            if pers_no == self._pers_no:
                # If it's a membership for the current person and
                # without read ranges, use the cache.
                return self._memberships[conf_no]
            else:
                return self.request(Requests.QueryReadTexts, pers_no, conf_no, 0, 0).response()

    def fetch_membership(self, conf_no):
        """Fetch the membership for a conf the current person. Does not
        include read ranges.
        """
        # We can only cache memberships for the currently logged in
        # person, because we don't receive async leave/join messages
        # for other persons. We also only cache memberships without
        # read ranges, because it is easier to invalidate correctly.
        return self.request(Requests.QueryReadTexts11, self._pers_no, conf_no, 0, 0).response()
    
    # Handlers for asynchronous messages (internal use)
    def cah_leave_conf(self, msg, c):
        CachedConnection.cah_leave_conf(self, msg, c)
        # Invalidates cached membership
        self._memberships.invalidate(msg.conf_no)
        # We invalidate the entire memberships_by_position because you
        # can change position of memberships.
        self._memberships_by_position = dict()

    def cah_new_membership(self, msg, c):
        CachedConnection.cah_new_membership(self, msg, c)
        # Invalidates self._memberships_by_position
        self._memberships_by_position = dict()
        # The self.memberships cache can only cache actual
        # memberships, and because we get this async messages, we know
        # the current person was not a member before.

    # Report cache usage
    def report_cache_usage(self):
        CachedConnection.report_cache_usage(self)
        self._memberships.report()
        

# Cache class for use internally by CachedConnection
class Cache:
    def __init__(self, fetcher, name = "Unknown"):
        self.dict = {}
        self.fetcher = fetcher
        self.cached = 0
        self.uncached = 0
        self.name = name

    def __getitem__(self, no):
        #print('%s[%d]' % (self.name, no))
        if no in self.dict:
            #print('%s[%d] - cached' % (self.name, no))
            self.cached = self.cached + 1
            return self.dict[no]
        else:
            #print('%s[%d] - not cached' % (self.name, no))
            self.uncached = self.uncached + 1
            self.dict[no] = self.fetcher(no)
            return self.dict[no]

    def __setitem__(self, no, val):
        self.dict[no] = val

    def invalidate(self, no):
        if no in self.dict:
            del self.dict[no]
    
    def invalidate_all(self):
        self.dict = dict()

    def report(self):
        print("Cache %s: %d cached, %d uncached" % (self.name,
                                                    self.cached,
                                                    self.uncached))
        
