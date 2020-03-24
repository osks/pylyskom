# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

from __future__ import absolute_import
from __future__ import print_function
import logging

from six.moves import range

from . import requests, utils
from .asyncmsg import AsyncMessages, async_dict
from .errors import NotMember, NoSuchLocalText, UnimplementedAsync
from .stats import stats


logger = logging.getLogger("pylyskom.cachedconnection")


class Client(object):
    def __init__(self, conn):
        self._conn = conn
        self._ok_queue = {}
        self._error_queue = {}
        self._async_handler_func = None

    def close(self):
        self._conn.close()

    def request(self, request):
        """
        Send an request and return the response.
        """
        logger.debug("sending request: %s" % (request,))
        ref_no = self._conn.send_request(request)
        resp = self._wait_and_dequeue(ref_no)
        logger.debug("returning response for ref_no: %s" % (ref_no, ))
        return resp

    def set_async_handler(self, handler_func):
        """Set the async handler function.

        @param handler_func Function that will be called when an async
        message is received. Will receive the async message as
        argument. If handler_func is None, there will be no handling
        of async messages.
        """
        self._async_handler_func = handler_func

    def _wait_and_dequeue(self, ref_no):
        """Wait for a request to be answered, return response or raise
        error.
        """
        logger.debug("waiting for  response ref_no: %s" % (ref_no,))
        while ref_no not in self._ok_queue and \
              ref_no not in self._error_queue:
            self._read_response()

        if ref_no in self._ok_queue:
            resp = self._ok_queue[ref_no]
            logger.debug("got response %s ref_no: %s" % (resp, ref_no))
            del self._ok_queue[ref_no]
            return resp
        elif ref_no in self._error_queue:
            error = self._error_queue[ref_no]
            logger.debug("got error %s ref_no: %s" % (error, ref_no))
            del self._error_queue[ref_no]
            raise error
        else:
            raise RuntimeError("Got unknown ref-no: %r" % (ref_no,))

    def _read_response(self):
        ref_no, resp, error = self._conn.read_response()
        logger.debug("read response for ref_no: %s" % (ref_no,))
        if ref_no is None:
            # async message
            self._handle_async_message(resp)
        elif error is not None:
            # error reply
            self._error_queue[ref_no] = error
        else:
            # ok reply - resp can be None
            self._ok_queue[ref_no] = resp

    def _handle_async_message(self, msg):
        if self._async_handler_func is not None:
            self._async_handler_func(msg)



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

class CachingClient(object):
    def __init__(self, client):
        self._client = client

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

        self._async_handlers = {}
        self._client.set_async_handler(self._handle_async_message)

        # Setup up async handlers for invalidating cache entries. Skip
        # sending accept-async until the last call.
        self._add_async_handler(AsyncMessages.NEW_NAME, self._cah_new_name)
        self._add_async_handler(AsyncMessages.LEAVE_CONF, self._cah_leave_conf)
        self._add_async_handler(AsyncMessages.DELETED_TEXT, self._cah_deleted_text)
        self._add_async_handler(AsyncMessages.NEW_TEXT, self._cah_new_text)
        self._add_async_handler(AsyncMessages.NEW_RECIPIENT, self._cah_new_recipient)
        self._add_async_handler(AsyncMessages.SUB_RECIPIENT, self._cah_sub_recipient)
        self._add_async_handler(AsyncMessages.NEW_MEMBERSHIP, self._cah_new_membership)
        self.request(requests.ReqAcceptAsync(list(self._async_handlers.keys())))


    def close(self):
        self._client.close()

    def request(self, request):
        return self._client.request(request)


    # Async handling

    def _handle_async_message(self, msg):
        if msg.MSG_NO in self._async_handlers:
            for handler in self._async_handlers[msg.MSG_NO]:
                handler(msg)

    def _add_async_handler(self, msg_no, handler):
        """Register a handler for a type of async message.

        @param msg_no Type of async message.

        @param handler Function that should be called when an async
        message of the specified type is received.
        """
        if msg_no not in async_dict:
            raise UnimplementedAsync
        if msg_no in self._async_handlers:
            self._async_handlers[msg_no].append(handler)
        else:
            self._async_handlers[msg_no] = [handler]

    def register_async_handler(self, msg_no, handler, skip_accept_async=False):
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
        self._add_async_handler(msg_no, handler)
        if not skip_accept_async:
            self.request(requests.ReqAcceptAsync(list(self._async_handlers.keys())))


    # Handlers for asynchronous messages (internal use) FIXME: Most of
    # these handlers could do more clever things than just
    # invalidating.

    def _cah_new_name(self, msg):
        # A new name makes uconferences[].name invalid
        self.uconferences.invalidate(msg.conf_no)
        # A new name makes conferences[].name invalid
        self.conferences.invalidate(msg.conf_no)

    def _cah_leave_conf(self, msg):
        # Leaving a conference makes conferences[].no_of_members invalid
        self.conferences.invalidate(msg.conf_no)

    def _cah_deleted_text(self, msg):
        # Deletion of a text makes conferences[].no_of_texts invalid
        ts = msg.text_stat
        for rcpt in ts.misc_info.recipient_list:
            self.conferences.invalidate(rcpt.recpt)
            
    def _cah_new_text(self, msg):
        # A new text. conferences[].no_of_texts and
        # uconferences[].highest_local_no is invalid. Also invalidates
        # the textstats for the commented texts.
        for rcpt in msg.text_stat.misc_info.recipient_list:
            self.conferences.invalidate(rcpt.recpt)
            self.uconferences.invalidate(rcpt.recpt)
        for ct in msg.text_stat.misc_info.comment_to_list:
            self.textstats.invalidate(ct.text_no)
        # FIXME: A new text makes persons[author].no_of_created_texts invalid

    def _cah_new_recipient(self, msg):
        # Just like a new text; conferences[].no_of_texts and
        # uconferences[].highest_local_no gets invalid. 
        self.conferences.invalidate(msg.conf_no)
        self.uconferences.invalidate(msg.conf_no)
        # textstats.misc_info_recipient_list gets invalid as well.
        self.textstats.invalidate(msg.text_no)

    def _cah_sub_recipient(self, msg):
        # Invalid conferences[].no_of_texts
        self.conferences.invalidate(msg.conf_no)
        # textstats.misc_info_recipient_list gets invalid as well.
        self.textstats.invalidate(msg.text_no)

    def _cah_new_membership(self, msg):
        # Joining a conference makes conferences[].no_of_members invalid
        self.conferences.invalidate(msg.conf_no)


    # Fetching functions (internal use)
    def _fetch_uconference(self, no):
        return self.request(requests.ReqGetUconfStat(no))

    def _fetch_conference(self, no):
        return self.request(requests.ReqGetConfStat(no))

    def _fetch_person(self, no):
        return self.request(requests.ReqGetPersonStat(no))

    def _fetch_textstat(self, no):
        return self.request(requests.ReqGetTextStat(no))


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
        except Exception:
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
            except Exception:
                return []
        else:
            # Alphabetical case
            matches = self.request(
                requests.ReqLookupZName(
                    name,
                    want_pers=want_pers,
                    want_confs=want_confs))
            return [(x.conf_no, x.name.decode('latin1')) for x in matches]

    def regexp_lookup(self, regexp, want_pers, want_confs,
                      case_sensitive=0):
        """Lookup name using regular expression"""
        if regexp.startswith("#"):
            return self.lookup_name(regexp, want_pers, want_confs)

        if not case_sensitive:
            collate_table = self.request(requests.ReqGetCollateTable())
            regexp = utils.case_insensitive_regexp(regexp, collate_table)

        matches = self.request(
            requests.ReqReZLookup(
                regexp,
                want_persons=want_pers,
                want_confs=want_confs))
        return [(x.conf_no, x.name.decode('latin1')) for x in matches]

    def get_unread_texts_from_membership(self, membership):
        unread = []

        more_to_fetch = 1
        gaps, last = utils.read_ranges_to_gaps_and_last(membership.read_ranges)
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
                        requests.ReqLocalToGlobal(membership.conference, first_local, n))
                    unread.extend([e[1] for e in mapping.list if e[1] != 0])
                    first_local = mapping.range_end
                    more_to_fetch = mapping.later_texts_exists
                except NoSuchLocalText:
                    more_to_fetch = 0

        # If there are more than 255 after the last read range, we
        # need to continue mapping (the last, if any, previous call
        # will have set later_texts_exists to 1 if so).
        first_local = last
        while more_to_fetch:
            try:
                mapping = self.request(
                    requests.ReqLocalToGlobal(membership.conference, first_local, 255))
                unread.extend([e[1] for e in mapping.list if e[1] != 0])
                first_local = mapping.range_end
                more_to_fetch = mapping.later_texts_exists
            except NoSuchLocalText:
                # No unread texts
                more_to_fetch = 0

        # Remove text that don't exist anymore (text_no == 0)
        return [ text_no for text_no in unread if text_no != 0]

    def mark_text(self, text_no, mark_type):
        self.request(requests.ReqMarkText(text_no, mark_type))
        # textstat.misc_info.no_of_marks is now invalid
        self.textstats.invalidate(text_no)

    def unmark_text(self, text_no):
        self.request(requests.ReqUnmarkText(text_no))
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
        self._add_async_handler(AsyncMessages.LEAVE_CONF, self._cpah_leave_conf)
        self._add_async_handler(AsyncMessages.NEW_MEMBERSHIP, self._cpah_new_membership)
        self.request(requests.ReqAcceptAsync(list(self._async_handlers.keys())))

    def login(self, pers_no, password):
        self.request(requests.ReqLogin(pers_no, password, invisible=0))
        # We need to know the current person to be able to have and
        # invalidate caches.
        self._pers_no = pers_no

    def logout(self):
        self.request(requests.ReqLogout())
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
        self.request(requests.ReqChangeConference(conf_no))
        self._current_conference_no = conf_no
        if prev_conf_no != 0:
            self._invalidate_membership(prev_conf_no)

    def mark_as_read_local(self, conf_no, local_text_no):
        try:
            self.request(requests.ReqMarkAsRead(conf_no, [local_text_no]))
        except NotMember:
            pass

    def mark_as_unread_local(self, conf_no, local_text_no):
        try:
            self.request(requests.ReqMarkAsUnread(conf_no, local_text_no))
        except NotMember:
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
                requests.ReqGetMembership11(pers_no, 0, no_of_confs, 1, 0))
        else:
            if pers_no == self._pers_no:
                # We cache the result for the current person and without
                # read ranges, because that is what we can invalidate
                # correctly.
                memberships = self._get_cached_memberships_by_position(first, no_of_confs)
                if memberships is None:
                    memberships = self.request(
                        requests.ReqGetMembership11(
                            self._pers_no, first, no_of_confs, 0, 0))
                    self._update_cached_memberships_by_position(memberships)
                return memberships
            else:
                return self.request(
                    requests.ReqGetMembership11(pers_no, 0, no_of_confs, 0, 0))

    def get_membership(self, pers_no, conf_no, want_read_ranges=False):
        """Get a membership for a person
        """
        if want_read_ranges:
            return self.request(requests.ReqQueryReadTexts(pers_no, conf_no, 1, 0))
        else:
            if pers_no == self._pers_no:
                # If it's a membership for the current person and
                # without read ranges, use the cache.
                return self._memberships[conf_no]
            else:
                return self.request(requests.ReqQueryReadTexts(pers_no, conf_no, 0, 0))

    def _fetch_membership(self, conf_no):
        """Fetch the membership for a conf the current person. Does not
        include read ranges.
        """
        # We can only cache memberships for the currently logged in
        # person, because we don't receive async leave/join messages
        # for other persons. We also only cache memberships without
        # read ranges, because it is easier to invalidate correctly.
        return self.request(requests.ReqQueryReadTexts11(self._pers_no, conf_no, 0, 0))
    
    # Handlers for asynchronous messages (internal use)
    def _cpah_leave_conf(self, msg):
        # Invalidates cached membership
        self._memberships.invalidate(msg.conf_no)
        # We invalidate the entire memberships_by_position because you
        # can change position of memberships.
        self._memberships_by_position = dict()

    def _cpah_new_membership(self, msg):
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
class Cache(object):
    def __init__(self, fetcher, name = "Unknown"):
        self.dict = {}
        self.fetcher = fetcher
        self.cached = 0
        self.uncached = 0
        self.name = name

    def __getitem__(self, no):
        #print('%s[%d]' % (self.name, no))
        stats.set('clients.cache.{}.gets.last'.format(self.name), 1, agg='sum')
        if no in self.dict:
            #print('%s[%d] - cached' % (self.name, no))
            self.cached = self.cached + 1
            stats.set('clients.cache.{}.gets.hits.last'.format(self.name), 1, agg='sum')
            return self.dict[no]
        else:
            #print('%s[%d] - not cached' % (self.name, no))
            self.uncached = self.uncached + 1
            stats.set('clients.cache.{}.gets.misses.last'.format(self.name), 1, agg='sum')
            self[no] = self.fetcher(no)
            return self.dict[no]

    def __setitem__(self, no, val):
        self.dict[no] = val
        stats.set('clients.cache.{}.sets.last'.format(self.name), 1, agg='sum')

    def invalidate(self, no):
        if no in self.dict:
            del self.dict[no]
            stats.set('clients.cache.{}.invalidations.last'.format(self.name), 1, agg='sum')

    def invalidate_all(self):
        self.dict = dict()
        stats.set('clients.cache.{}.invalidate-alls.last'.format(self.name), 1, agg='sum')

    def report(self):
        print(("Cache %s: %d cached, %d uncached" % (self.name,
                                                     self.cached,
                                                     self.uncached)))
