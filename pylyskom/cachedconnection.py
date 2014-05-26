# -*- coding: utf-8 -*-

from . import kom
from .request import Requests, default_request_factory
from .connection import Client


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

class CachingClient(Client):
    def __init__(self, connection, request_factory=default_request_factory):
        Client.__init__(self, connection)
        self._request_factory = request_factory

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
        self.uconferences = Cache(self._fetch_uconference, "UConference")
        self.conferences = Cache(self._fetch_conference, "Conference")
        self.persons = Cache(self._fetch_person, "Person")
        self.textstats = Cache(self._fetch_textstat, "TextStat")

        # Setup up async handlers for invalidating cache entries. Skip
        # sending accept-async until the last call.
        self.add_async_handler(kom.ASYNC_NEW_NAME, self._cah_new_name, True)
        self.add_async_handler(kom.ASYNC_LEAVE_CONF, self._cah_leave_conf, True)
        self.add_async_handler(kom.ASYNC_DELETED_TEXT, self._cah_deleted_text, True)
        self.add_async_handler(kom.ASYNC_NEW_TEXT, self._cah_new_text, True)
        self.add_async_handler(kom.ASYNC_NEW_RECIPIENT, self._cah_new_recipient, True)
        self.add_async_handler(kom.ASYNC_SUB_RECIPIENT, self._cah_sub_recipient, True)
        self.add_async_handler(kom.ASYNC_NEW_MEMBERSHIP, self._cah_new_membership)

    def request(self, request, *args, **kwargs):
        req = self._request_factory.new(request)(*args, **kwargs)
        req_id = self.register_request(req)
        return self.wait_and_dequeue(req_id)

    def add_async_handler(self, msg_no, handler, skip_accept_async=False):
        """Add an async handler and tell the LysKOM sever to
        start sending async messages of that type.
        
        @param skip_accept_async Don't send an AcceptAsync request to
        the LysKOM server now. This is an optimization feature. The
        protocol request registers all async message types at once, so
        this is useful to be able to only have to send one
        request. First register all but the last async handlers with
        skip_accept_async=True, and then register the last one with
        skip_accept_async=False to send the request.
        """
        self.register_async_handler(msg_no, handler)
        if not skip_accept_async:
            self.request(Requests.AcceptAsync, self._async_handlers.keys())


    # Fetching functions (internal use)
    def _fetch_uconference(self, no):
        return self.request(Requests.GetUconfStat, no)

    def _fetch_conference(self, no):
        return self.request(Requests.GetConfStat, no)

    def _fetch_person(self, no):
        return self.request(Requests.GetPersonStat, no)

    def _fetch_textstat(self, no):
        return self.request(Requests.GetTextStat, no)

    # Handlers for asynchronous messages (internal use)
    # FIXME: Most of these handlers should do more clever things than just
    # invalidating. 
    def _cah_new_name(self, msg, c):
        # A new name makes uconferences[].name invalid
        self.uconferences.invalidate(msg.conf_no)
        # A new name makes conferences[].name invalid
        self.conferences.invalidate(msg.conf_no)

    def _cah_leave_conf(self, msg, c):
        # Leaving a conference makes conferences[].no_of_members invalid
        self.conferences.invalidate(msg.conf_no)

    def _cah_deleted_text(self, msg, c):
        # Deletion of a text makes conferences[].no_of_texts invalid
        ts = msg.text_stat
        for rcpt in ts.misc_info.recipient_list:
            self.conferences.invalidate(rcpt.recpt)
            
    def _cah_new_text(self, msg, c):
        # A new text. conferences[].no_of_texts and
        # uconferences[].highest_local_no is invalid. Also invalidates
        # the textstats for the commented texts.
        for rcpt in msg.text_stat.misc_info.recipient_list:
            self.conferences.invalidate(rcpt.recpt)
            self.uconferences.invalidate(rcpt.recpt)
        for ct in msg.text_stat.misc_info.comment_to_list:
            self.textstats.invalidate(ct.text_no)
        # FIXME: A new text makes persons[author].no_of_created_texts invalid

    def _cah_new_recipient(self, msg, c):
        # Just like a new text; conferences[].no_of_texts and
        # uconferences[].highest_local_no gets invalid. 
        self.conferences.invalidate(msg.conf_no)
        self.uconferences.invalidate(msg.conf_no)
        # textstats.misc_info_recipient_list gets invalid as well.
        self.textstats.invalidate(msg.text_no)

    def _cah_sub_recipient(self, msg, c):
        # Invalid conferences[].no_of_texts
        self.conferences.invalidate(msg.conf_no)
        # textstats.misc_info_recipient_list gets invalid as well.
        self.textstats.invalidate(msg.text_no)

    def _cah_new_membership(self, msg, c):
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
                want_confs = want_confs)
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
            want_confs = want_confs)
        return [(x.conf_no, x.name.decode('latin1')) for x in matches]

    def _case_insensitive_regexp(self, regexp):
        """Make regular expression case insensitive"""
        result = ""
        # FIXME: Cache collate_table
        collate_table = self.request(Requests.GetCollateTable)
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
                        Requests.LocalToGlobal, membership.conference, first_local, n)
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
                    Requests.LocalToGlobal, membership.conference, first_local, 255)
                unread.extend([e[1] for e in mapping.list if e[1] != 0])
                first_local = mapping.range_end
                more_to_fetch = mapping.later_texts_exists
            except kom.NoSuchLocalText:
                # No unread texts
                more_to_fetch = 0
        
        # Remove text that don't exist anymore (text_no == 0)
        return [ text_no for text_no in unread if text_no != 0]

    def mark_text(self, text_no, mark_type):
        self.request(Requests.MarkText, text_no, mark_type)
        # textstat.misc_info.no_of_marks is now invalid
        self.textstats.invalidate(text_no)

    def unmark_text(self, text_no):
        self.request(Requests.UnmarkText, text_no)
        # textstat.misc_info.no_of_marks is now invalid
        self.textstats.invalidate(text_no)


class CachingPersonClient(CachingClient):
    def __init__(self, connection):
        CachingClient.__init__(self, connection)

#    def connect(self, host, port = 4894, user = "", localbind=None):
#        CachingClient.connect(self, host, port, user, localbind)

        # Current person number
        self._pers_no = 0
        
        # Current conference (change-conference)
        self._current_conference_no = 0
        
        # Caches
        self._memberships = Cache(self._fetch_membership, "Membership")
        
        # Specific membership cache where the keys are the positions
        # in the membership list for the membership, and the values
        # are the memberships. There is a risk with having this cache
        # - you can modify positions and we currently have no way of
        # detecting that (no async messages).
        self._memberships_by_position = dict()

        # Setup up async handlers for invalidating cache entries. Skip
        # sending accept-async until the last call.
        self.add_async_handler(kom.ASYNC_LEAVE_CONF, self._cpah_leave_conf, True)
        self.add_async_handler(kom.ASYNC_NEW_MEMBERSHIP, self._cpah_new_membership)

    def login(self, pers_no, password):
        self.request(Requests.Login, pers_no, password, invisible=0)
        # We need to know the current person to be able to have and
        # invalidate caches.
        self._pers_no = pers_no

    def logout(self):
        self.request(Requests.Logout)
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
        self.request(Requests.ChangeConference, conf_no)
        self._current_conference_no = conf_no
        if prev_conf_no != 0:
            self._invalidate_membership(prev_conf_no)

    def mark_as_read_local(self, conf_no, local_text_no):
        try:
            self.request(Requests.MarkAsRead, conf_no, [local_text_no])
        except kom.NotMember:
            pass

    def mark_as_unread_local(self, conf_no, local_text_no):
        try:
            self.request(Requests.MarkAsUnread, conf_no, local_text_no)
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
                Requests.GetMembership11, pers_no, 0, no_of_confs, 1, 0)
        else:
            if pers_no == self._pers_no:
                # We cache the result for the current person and without
                # read ranges, because that is what we can invalidate
                # correctly.
                memberships = self._get_cached_memberships_by_position(first, no_of_confs)
                if memberships is None:
                    memberships = self.request(
                        Requests.GetMembership11,
                        self._pers_no, first, no_of_confs, 0, 0)
                    self._update_cached_memberships_by_position(memberships)
                return memberships
            else:
                return self.request(
                    Requests.GetMembership11, pers_no, 0, no_of_confs, 0, 0)

    def get_membership(self, pers_no, conf_no, want_read_ranges=False):
        """Get a membership for a person
        """
        if want_read_ranges:
            return self.request(Requests.QueryReadTexts, pers_no, conf_no, 1, 0)
        else:
            if pers_no == self._pers_no:
                # If it's a membership for the current person and
                # without read ranges, use the cache.
                return self._memberships[conf_no]
            else:
                return self.request(Requests.QueryReadTexts, pers_no, conf_no, 0, 0)

    def _fetch_membership(self, conf_no):
        """Fetch the membership for a conf the current person. Does not
        include read ranges.
        """
        # We can only cache memberships for the currently logged in
        # person, because we don't receive async leave/join messages
        # for other persons. We also only cache memberships without
        # read ranges, because it is easier to invalidate correctly.
        return self.request(Requests.QueryReadTexts11, self._pers_no, conf_no, 0, 0)
    
    # Handlers for asynchronous messages (internal use)
    def _cpah_leave_conf(self, msg, c):
        # Invalidates cached membership
        self._memberships.invalidate(msg.conf_no)
        # We invalidate the entire memberships_by_position because you
        # can change position of memberships.
        self._memberships_by_position = dict()

    def _cpah_new_membership(self, msg, c):
        # Invalidates self._memberships_by_position
        self._memberships_by_position = dict()
        # The self.memberships cache can only cache actual
        # memberships, and because we get this async messages, we know
        # the current person was not a member before.

    # Report cache usage
    def report_cache_usage(self):
        CachingClient.report_cache_usage(self)
        self._memberships.report()
        

# Cache class for use internally by CachingClient
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
        
