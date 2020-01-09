# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 2020 Oskar Skoog. Released under GPL.

import base64
import functools
import json
import logging

import six
import trio

from . import mimeparse

from .errors import (
    error_dict,
    BadRequestId,
    ReceiveError,
    BadInitialResponse,
    NotEnoughDataInBufferError,
    NotMember,
    NoSuchLocalText,
    ProtocolError,
    UnimplementedAsync)

from .protocol import (
    to_hstring,
    read_first_non_ws,
    read_int)

from .asyncmsg import AsyncMessages, async_dict
from .stats import stats
from . import requests, komauxitems, utils
from .datatypes import (
    AuxItemInput,
    ConfType,
    CookedMiscInfo,
    MICommentTo,
    MIRecipient,
    MembershipType,
    PersonalFlags)
from .komsession import (
    AmbiguousName,
    NameNotFound,
    KomSessionException,
    KomSessionNotConnected,
    KomSessionError,
    KomText,
    KomConference,
    KomUConference,
    KomMembership,
    KomMembershipUnread,
    KomPerson,
    MICommentTo_str_to_type,
    MIRecipient_str_to_type,
)


logger = logging.getLogger(__name__)


# The design of the async implementation is pretty ugly. The attempt
# is to get async IO with Trio working without having to redesign
# pylyskom's response parsing right now (and while keeping the
# blocking io implementation working).


class AioReceiveBuffer:
    def __init__(self):
        self._rb = b""    # Buffer for data received from connection
        self._rb_len = 0 # Length of the buffer
        self._rb_pos = 0 # Position of first unread byte in buffer

    def copy(self):
        c = AioReceiveBuffer()
        c._rb = self._rb
        c._rb_len = self._rb_len
        c._rb_pos = self._rb_pos
        return c

    def length(self):
        return self._rb_len

    def append(self, data):
        self._rb = self._rb[self._rb_pos:] + data
        self._rb_pos = 0
        self._rb_len = len(self._rb)

    def receive_string(self, length):
        """Get a string from the receive buffer (receiving more if
        necessary).
        """
        present = self._rb_len - self._rb_pos
        if present < length:
            raise NotEnoughDataInBufferError()
        res = self._rb[self._rb_pos:self._rb_pos+length]
        self._rb_pos = self._rb_pos + length
        return res

    def receive_char(self):
        """Get a character from the receive buffer (receiving more if
        necessary).
        """
        return self.receive_string(1)


class AioConnection:
    def __init__(self):
        self._tcp_stream = None
        self._buffer = AioReceiveBuffer()
        self._ref_no = 0 # Last used ID (i.e. increment before use)
        self._outstanding_requests = {} # Ref-No to Request mapping

    async def connect(self, host, port, user=None):
        """

        @param user: See Protocol A spec.
        """
        if user is None:
            user = ""
        assert isinstance(user, str) # Do we want user to be str or bytes?
        self._tcp_stream = await trio.open_tcp_stream(host, port)

        # Send initial string
        await self._tcp_stream.send_all(b"A%s\n" % (to_hstring(user.encode('latin1')),))

        # Wait for answer "LysKOM\n"
        await self._ensure_receive_buffer_size(7)
        resp = self._buffer.receive_string(7)
        if resp != b"LysKOM\n":
            raise BadInitialResponse()
        stats.set('connections.opened.last', 1, agg='sum')

    def is_connected(self):
        return self._tcp_stream is not None

    async def close(self):
        if self._tcp_stream is None:
            return
        try:
            await self._tcp_stream.aclose()
        finally:
            self._tcp_stream = None
            stats.set('connections.closed.last', 1, agg='sum')

    async def send_request(self, req):
        self._ref_no += 1
        ref_no = self._ref_no
        assert ref_no not in self._outstanding_requests
        request_string = b"%d %s" % (ref_no, req.to_string())
        await self._tcp_stream.send_all(request_string)
        self._outstanding_requests[ref_no] = req
        stats.set('connections.requests.sent.last', 1, agg='sum')
        return ref_no

    async def _ensure_receive_buffer_size(self, size):
        while self._buffer.length() < size:
            await self._receive_some_to_buffer()

    async def _receive_some_to_buffer(self):
        data = await self._tcp_stream.receive_some()
        if len(data) == 0:
            raise ReceiveError("End of stream")
        self._buffer.append(data)

    async def read_response(self):
        while True:
            # Trying to parse a response will consume from the buffer,
            # and to be able to try again we need to keep all of the
            # buffer until we can parse a response.
            buffer_copy = self._buffer.copy()
            try:
                return self._parse_response()
            except NotEnoughDataInBufferError:
                # Continue reading data from stream
                # Restore buffer
                self._buffer = buffer_copy
                # We couldn't parse a response, receive some more data
                # and try again
                await self._receive_some_to_buffer()

    def _parse_response(self):
        ch = read_first_non_ws(self._buffer)
        if ch == b"=":
            ref_no, resp, error = self._parse_ok_reply()
            stats.set('connections.responses.received.ok.last', 1, agg='sum')
        elif ch == b"%":
            ref_no, resp, error = self._parse_error_reply()
            stats.set('connections.responses.received.error.last', 1, agg='sum')
        elif ch == b":":
            ref_no, resp, error = self._parse_asynchronous_message()
            stats.set('connections.responses.received.async.last', 1, agg='sum')
        else:
            stats.set('connections.responses.received.protocolerror.last', 1, agg='sum')
            raise ProtocolError("Got unexpected: %s" % (ch,))
        stats.set('connections.responses.received.last', 1, agg='sum')
        return ref_no, resp, error

    def _parse_ok_reply(self):
        ref_no = read_int(self._buffer)
        if ref_no not in self._outstanding_requests:
            raise BadRequestId(ref_no)
        req = self._outstanding_requests[ref_no]
        resp = requests.response_dict[req.CALL_NO].parse(self._buffer)
        del self._outstanding_requests[ref_no]
        return ref_no, resp, None

    def _parse_error_reply(self):
        ref_no = read_int(self._buffer)
        if ref_no not in self._outstanding_requests:
            raise BadRequestId(ref_no)
        error_no = read_int(self._buffer)
        error_status = read_int(self._buffer)
        error = error_dict[error_no](error_status)
        del self._outstanding_requests[ref_no]
        return ref_no, None, error

    def _parse_asynchronous_message(self):
        read_int(self._buffer) # read number of arguments (but we don't need it)
        msg_no = read_int(self._buffer)
        if msg_no not in async_dict:
            raise UnimplementedAsync(msg_no)
        msg = async_dict[msg_no].parse(self._buffer)
        return None, msg, None


class AioClient:
    def __init__(self, conn):
        self._conn = conn
        self._ok_queue = {}
        self._error_queue = {}
        self._async_handler_func = None

    async def connect(self, host, port, user=None):
        await self._conn.connect(host, port, user=user)

    def is_connected(self):
        return self._conn.is_connected()

    async def close(self):
        await self._conn.close()

    async def request(self, request):
        """
        Send an request and return the response.
        """
        logger.debug("sending request: %s" % (request,))
        ref_no = await self._conn.send_request(request)
        resp = await self._wait_and_dequeue(ref_no)
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

    async def _wait_and_dequeue(self, ref_no):
        """Wait for a request to be answered, return response or raise
        error.
        """
        logger.debug("waiting for  response ref_no: %s" % (ref_no,))
        while ref_no not in self._ok_queue and \
              ref_no not in self._error_queue:
            await self._read_response()

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

    async def _read_response(self):
        ref_no, resp, error = await self._conn.read_response()
        logger.debug("read response for ref_no: %s" % (ref_no,))
        if ref_no is None:
            # async message
            await self._handle_async_message(resp)
        elif error is not None:
            # error reply
            self._error_queue[ref_no] = error
        else:
            # ok reply - resp can be None
            self._ok_queue[ref_no] = resp

    async def _handle_async_message(self, msg):
        if self._async_handler_func is not None:
            await self._async_handler_func(msg)


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

class AioCachingClient:
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
        self.uconferences = AioCache(self._fetch_uconference, "UConference")
        self.conferences = AioCache(self._fetch_conference, "Conference")
        self.persons = AioCache(self._fetch_person, "Person")
        self.textstats = AioCache(self._fetch_textstat, "TextStat")

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


    async def connect(self, host, port, user=None):
        await self._client.connect(host, port, user=user)
        await self.request(requests.ReqAcceptAsync(list(self._async_handlers.keys())))

    def is_connected(self):
        return self._client.is_connected()

    async def close(self):
        await self._client.close()

    async def request(self, request):
        return await self._client.request(request)


    # Protocol A async message handling

    async def _handle_async_message(self, msg):
        if msg.MSG_NO in self._async_handlers:
            for handler in self._async_handlers[msg.MSG_NO]:
                await handler(msg)

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

    async def register_async_handler(self, msg_no, handler, skip_accept_async=False):
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
            await self.request(requests.ReqAcceptAsync(list(self._async_handlers.keys())))


    # Handlers for asynchronous messages (internal use) FIXME: Most of
    # these handlers could do more clever things than just
    # invalidating.

    async def _cah_new_name(self, msg):
        # A new name makes uconferences[].name invalid
        self.uconferences.invalidate(msg.conf_no)
        # A new name makes conferences[].name invalid
        self.conferences.invalidate(msg.conf_no)

    async def _cah_leave_conf(self, msg):
        # Leaving a conference makes conferences[].no_of_members invalid
        self.conferences.invalidate(msg.conf_no)

    async def _cah_deleted_text(self, msg):
        # Deletion of a text makes conferences[].no_of_texts invalid
        ts = msg.text_stat
        for rcpt in ts.misc_info.recipient_list:
            self.conferences.invalidate(rcpt.recpt)

    async def _cah_new_text(self, msg):
        # A new text. conferences[].no_of_texts and
        # uconferences[].highest_local_no is invalid. Also invalidates
        # the textstats for the commented texts.
        for rcpt in msg.text_stat.misc_info.recipient_list:
            self.conferences.invalidate(rcpt.recpt)
            self.uconferences.invalidate(rcpt.recpt)
        for ct in msg.text_stat.misc_info.comment_to_list:
            self.textstats.invalidate(ct.text_no)
        # FIXME: A new text makes persons[author].no_of_created_texts invalid

    async def _cah_new_recipient(self, msg):
        # Just like a new text; conferences[].no_of_texts and
        # uconferences[].highest_local_no gets invalid. 
        self.conferences.invalidate(msg.conf_no)
        self.uconferences.invalidate(msg.conf_no)
        # textstats.misc_info_recipient_list gets invalid as well.
        self.textstats.invalidate(msg.text_no)

    async def _cah_sub_recipient(self, msg):
        # Invalid conferences[].no_of_texts
        self.conferences.invalidate(msg.conf_no)
        # textstats.misc_info_recipient_list gets invalid as well.
        self.textstats.invalidate(msg.text_no)

    async def _cah_new_membership(self, msg):
        # Joining a conference makes conferences[].no_of_members invalid
        self.conferences.invalidate(msg.conf_no)


    # Fetching functions (internal use)
    async def _fetch_uconference(self, no):
        return await self.request(requests.ReqGetUconfStat(no))

    async def _fetch_conference(self, no):
        return await self.request(requests.ReqGetConfStat(no))

    async def _fetch_person(self, no):
        return await self.request(requests.ReqGetPersonStat(no))

    async def _fetch_textstat(self, no):
        return await self.request(requests.ReqGetTextStat(no))


    # Report cache usage
    def report_cache_usage(self):
        self.uconferences.report()
        self.conferences.report()
        self.persons.report()
        self.textstats.report()

    # Common operation: get name of conference (via uconference)
    async def conf_name(self, conf_no, default = "", include_no = 0):
        try:
            conf_name = (await self.uconferences.get(conf_no)).name.decode('latin1')
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
    async def lookup_name(self, name, want_pers, want_confs):
        if name[:1] == "#":
            # Numerical case
            try:
                no = int(name[1:]) # Exception if not int
                type = (await self.uconferences.get(no)).type # Exception if not found
                name = (await self.uconferences.get(no)).name.decode('latin1')
                if (want_pers and type.letterbox) or \
                   (want_confs and (not type.letterbox)):
                    return [(no, name)]
                else:
                    return []
            except Exception:
                return []
        else:
            # Alphabetical case
            matches = await self.request(
                requests.ReqLookupZName(
                    name,
                    want_pers=want_pers,
                    want_confs=want_confs))
            return [(x.conf_no, x.name.decode('latin1')) for x in matches]

    async def regexp_lookup(self, regexp, want_pers, want_confs,
                      case_sensitive=0):
        """Lookup name using regular expression"""
        if regexp.startswith("#"):
            return await self.lookup_name(regexp, want_pers, want_confs)

        if not case_sensitive:
            regexp = await self._case_insensitive_regexp(regexp)

        matches = await self.request(
            requests.ReqReZLookup(
                regexp,
                want_persons=want_pers,
                want_confs=want_confs))
        return [(x.conf_no, x.name.decode('latin1')) for x in matches]

    async def _case_insensitive_regexp(self, regexp):
        """Make regular expression case insensitive"""
        result = ""
        # FIXME: Cache collate_table
        collate_table = await self.request(requests.ReqGetCollateTable())
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

    async def get_unread_texts_from_membership(self, membership):
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
                    mapping = await self.request(
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
                mapping = await self.request(
                    requests.ReqLocalToGlobal(membership.conference, first_local, 255))
                unread.extend([e[1] for e in mapping.list if e[1] != 0])
                first_local = mapping.range_end
                more_to_fetch = mapping.later_texts_exists
            except NoSuchLocalText:
                # No unread texts
                more_to_fetch = 0

        # Remove text that don't exist anymore (text_no == 0)
        return [ text_no for text_no in unread if text_no != 0]

    async def mark_text(self, text_no, mark_type):
        await self.request(requests.ReqMarkText(text_no, mark_type))
        # textstat.misc_info.no_of_marks is now invalid
        self.textstats.invalidate(text_no)

    async def unmark_text(self, text_no):
        await self.request(requests.ReqUnmarkText(text_no))
        # textstat.misc_info.no_of_marks is now invalid
        self.textstats.invalidate(text_no)


class AioCachingPersonClient(AioCachingClient):
    def __init__(self, connection):
        AioCachingClient.__init__(self, connection)

        # Current person number
        self._pers_no = 0

        # Current conference (change-conference)
        self._current_conference_no = 0

        # Caches
        self._memberships = AioCache(self._fetch_membership, "Membership")

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

    async def login(self, pers_no, password):
        await self.request(requests.ReqLogin(pers_no, password, invisible=0))
        # We need to know the current person to be able to have and
        # invalidate caches.
        self._pers_no = pers_no

    async def logout(self):
        await self.request(requests.ReqLogout())
        # Invalidate caches that are/were for the current person
        self._pers_no = 0
        self._memberships_by_position = dict()
        self._memberships.invalidate_all()

    def get_person_no(self):
        return self._pers_no

    def is_logged_in(self):
        return self._pers_no != 0

    async def change_conference(self, conf_no):
        # When changing conference, the lyskom server will update
        # last-time-read for the membership of the *previous*
        # conference. This means that we need to keep track of the
        # current conference to be able to invalidate the membership
        # correctly.
        prev_conf_no = self._current_conference_no
        await self.request(requests.ReqChangeConference(conf_no))
        self._current_conference_no = conf_no
        if prev_conf_no != 0:
            self._invalidate_membership(prev_conf_no)

    async def mark_as_read_local(self, conf_no, local_text_no):
        try:
            await self.request(requests.ReqMarkAsRead(conf_no, [local_text_no]))
        except NotMember:
            pass

    async def mark_as_unread_local(self, conf_no, local_text_no):
        try:
            await self.request(requests.ReqMarkAsUnread(conf_no, local_text_no))
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

    async def get_memberships(self, pers_no, first, no_of_confs, want_read_ranges=False):
        """Get memberships for a person.
        """
        if want_read_ranges:
            return await self.request(
                requests.ReqGetMembership11(pers_no, 0, no_of_confs, 1, 0))
        else:
            if pers_no == self._pers_no:
                # We cache the result for the current person and without
                # read ranges, because that is what we can invalidate
                # correctly.
                memberships = self._get_cached_memberships_by_position(first, no_of_confs)
                if memberships is None:
                    memberships = await self.request(
                        requests.ReqGetMembership11(
                            self._pers_no, first, no_of_confs, 0, 0))
                    self._update_cached_memberships_by_position(memberships)
                return memberships
            else:
                return await self.request(
                    requests.ReqGetMembership11(pers_no, 0, no_of_confs, 0, 0))

    async def get_membership(self, pers_no, conf_no, want_read_ranges=False):
        """Get a membership for a person
        """
        if want_read_ranges:
            return await self.request(requests.ReqQueryReadTexts(pers_no, conf_no, 1, 0))
        else:
            if pers_no == self._pers_no:
                # If it's a membership for the current person and
                # without read ranges, use the cache.
                return await self._memberships.get(conf_no)
            else:
                return await self.request(requests.ReqQueryReadTexts(pers_no, conf_no, 0, 0))

    async def _fetch_membership(self, conf_no):
        """Fetch the membership for a conf the current person. Does not
        include read ranges.
        """
        # We can only cache memberships for the currently logged in
        # person, because we don't receive async leave/join messages
        # for other persons. We also only cache memberships without
        # read ranges, because it is easier to invalidate correctly.
        return await self.request(requests.ReqQueryReadTexts11(self._pers_no, conf_no, 0, 0))

    # Handlers for asynchronous messages (internal use)
    async def _cpah_leave_conf(self, msg):
        # Invalidates cached membership
        self._memberships.invalidate(msg.conf_no)
        # We invalidate the entire memberships_by_position because you
        # can change position of memberships.
        self._memberships_by_position = dict()

    async def _cpah_new_membership(self, msg):
        # Invalidates self._memberships_by_position
        self._memberships_by_position = dict()
        # The self.memberships cache can only cache actual
        # memberships, and because we get this async messages, we know
        # the current person was not a member before.

    # Report cache usage
    def report_cache_usage(self):
        AioCachingClient.report_cache_usage(self)
        self._memberships.report()


# Cache class for use internally by AioCachingClient
class AioCache(object):
    def __init__(self, fetcher, name = "Unknown"):
        self.dict = {}
        self.fetcher = fetcher
        self.cached = 0
        self.uncached = 0
        self.name = name

    async def get(self, no):
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
            self.dict[no] = await self.fetcher(no)
            stats.set('clients.cache.{}.sets.last'.format(self.name), 1, agg='sum')
            return self.dict[no]

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


def create_client():
    conn = AioConnection()
    client = AioClient(conn)
    caching_client = AioCachingPersonClient(client)
    return caching_client


def check_connection(f):
    @functools.wraps(f)
    async def decorated(komsession, *args, **kwargs):
        if not komsession.is_connected():
            raise KomSessionNotConnected()
        try:
            return await f(komsession, *args, **kwargs)
        except (trio.BrokenResourceError, trio.ClosedResourceError) as te:
            # We got an error that indicates that the connection has
            # failed, then close and raise.
            await komsession.close()
            raise KomSessionNotConnected(te)
        except Exception as e:
            raise KomSessionException(e)

    return decorated


# Idea: rename KomSession to KomClient?
class AioKomSession(object):
    """ A LysKom session.

    Should handle either unicode strings or utf-8 encoded strings. (FIXME)

    TODO[Python3]: Only handle (unicode) strings, not bytes, in the
    external interfaces for things that are real strings. ??? (Or only
    bytes? Seems inconvient at this level.)

    """
    def __init__(self, client_factory=create_client):
        # TODO: We actually require the API of a
        # CachingPersonClient. We should enhance the Connection
        # class and make CachingPersonClient have the same API as
        # Connection.
        self._client_factory = client_factory
        self._client = None
        self._session_no = None
        self._client_name = None
        self._client_version = None

    async def connect(self, host, port, username, hostname, client_name, client_version):
        assert not self.is_connected() # todo: raise better exception
        # decode if not already unicode (assuming utf-8)
        if isinstance(client_name, six.binary_type):
            client_name = client_name.decode('utf-8')
        if isinstance(client_version, six.binary_type):
            client_version = client_version.decode('utf-8')

        self._client = self._client_factory()
        await self._client.connect(host, port, user=username + "%" + hostname)

        # todo: we shouldn't require client name/version. specify in
        # constructor instead (because I don't think it should be
        # possible to change after connecting) - but send the request
        # here (if they are set).
        await self._client.request(requests.ReqSetClientVersion(client_name, client_version))
        self._client_name = client_name
        self._client_version = client_version

        self._session_no = await self.who_am_i()
        await self._client.request(requests.ReqSetConnectionTimeFormat(use_utc=1))

    def is_connected(self):
        return self._client is not None

    async def close(self):
        """Immediately close the connection, without sending a Disconnect request.
        """
        try:
            if self._client is not None:
                await self._client.close()
        finally:
            self._client = None
            self._client_name = None
            self._client_version = None
            self._session_no = None

    @check_connection
    async def disconnect(self, session_no=0):
        """Session number 0 means this session (a logged in user can
        disconnect its other sessions).
        """
        await self._client.request(requests.ReqDisconnect(session_no))

        # Check if we disconnected our own session or not (you can
        # disconnect another LysKOM session that the logged in user is
        # a supervisor of).
        if session_no == 0 or session_no == self._session_no:
            await self.close()

    @check_connection
    async def login(self, pers_no, password):
        if isinstance(password, six.binary_type):
            password = password.decode('utf-8')
        pers_no = int(pers_no)
        await self._client.login(pers_no, password)
        person_stat = await self._client.request(requests.ReqGetPersonStat(pers_no))
        return KomPerson(pers_no, person_stat)

    @check_connection
    async def logout(self):
        await self._client.logout()

    def get_person_no(self):
        return self._client.get_person_no()

    @check_connection
    async def who_am_i(self):
        return await self._client.request(requests.ReqWhoAmI())

    @check_connection
    async def user_is_active(self):
        await self._client.request(requests.ReqUserActive())

    def is_logged_in(self):
        return self._client.is_logged_in()

    @check_connection
    async def change_conference(self, conf_no):
        await self._client.change_conference(conf_no)

    @check_connection
    async def create_person(self, name, passwd):
        # decode if not already unicode (assuming utf-8)
        if isinstance(name, six.binary_type):
            name = name.decode('utf-8')
        if isinstance(passwd, six.binary_type):
            passwd = passwd.decode('utf-8')

        flags = PersonalFlags()
        aux_items = []
        pers_no = await self._client.request(
            requests.ReqCreatePerson(name, passwd, flags, aux_items))
        stats.set('komsession.persons.created.last', 1, agg='sum')
        return KomPerson(pers_no)

    @check_connection
    async def create_conference(self, name, aux_items=None):
        # decode if not already unicode (assuming utf-8)
        if isinstance(name, six.binary_type):
            name = name.decode('utf-8')

        conf_type = ConfType()
        if aux_items is None:
            aux_items = []
        conf_no = await self._client.request(
            requests.ReqCreateConf(name.encode('latin1'), conf_type, aux_items))
        stats.set('komsession.conferences.created.last', 1, agg='sum')
        return conf_no

    @check_connection
    async def lookup_name(self, name, want_pers, want_confs):
        if isinstance(name, six.binary_type):
            name = name.decode('utf-8')
        return await self._client.lookup_name(name, want_pers, want_confs)

    async def lookup_name_exact(self, name, want_pers, want_confs):
        matches = await self.lookup_name(name, want_pers, want_confs)
        return self._exact_lookup_match(name, matches)

    @check_connection
    async def re_lookup_name(self, regexp, want_pers, want_confs):
        # The LysKOM server is always case sensitive, and it's kom.py
        # that tries to create a case-insensitive regexp. Doesn't seem
        # to work that well.
        return await self._client.regexp_lookup(regexp, want_pers, want_confs, case_sensitive=1)

    async def re_lookup_name_exact(self, regexp, want_pers, want_confs):
        matches = await self.re_lookup_name(regexp, want_pers, want_confs)
        return self._exact_lookup_match(regexp, matches)

    @staticmethod
    def _exact_lookup_match(lookup, matches):
        if len(matches) == 0:
            raise NameNotFound("recipient not found: %s" % lookup)
        elif len(matches) != 1:
            raise AmbiguousName("ambiguous recipient: %s" % lookup)
        return matches[0][0]

    @check_connection
    async def get_text_stat(self, text_no):
        return await self._client.textstats.get(text_no)

    @check_connection
    async def add_membership(self, pers_no, conf_no, priority, where):
        mtype = MembershipType()
        await self._client.request(requests.ReqAddMember(conf_no, pers_no, priority, where, mtype))

    @check_connection
    async def delete_membership(self, pers_no, conf_no):
        await self._client.request(requests.ReqSubMember(conf_no, pers_no))

    @check_connection
    async def get_membership(self, pers_no, conf_no):
        membership = await self._client.get_membership(pers_no, conf_no, want_read_ranges=False)
        return KomMembership(pers_no, membership)

    @check_connection
    async def get_membership_unread(self, pers_no, conf_no):
        membership = await self._client.get_membership(pers_no, conf_no, want_read_ranges=True)
        unread_texts = await self._client.get_unread_texts_from_membership(membership)
        return KomMembershipUnread(pers_no, conf_no, len(unread_texts), unread_texts)

    @check_connection
    async def get_memberships(self, pers_no, first, no_of_confs, unread=False, passive=False):
        if unread:
            # RegGetUnreadConfs never returns passive memberships so
            # that combination is not valid.
            assert passive == False
            conf_nos = await self._client.request(requests.ReqGetUnreadConfs(pers_no))
            # This may return conferences that don't have any unread
            # texts in them. We have to live with this, because we
            # don't want to get the unread texts in this case. It's
            # possible that we need to change this, which means that
            # unread=True may be a slower call.
            memberships = [ await self.get_membership(pers_no, conf_no) for conf_no in conf_nos ]
            has_more = False
        else:
            ms_list = await self._client.get_memberships(pers_no, first, no_of_confs,
                                                         want_read_ranges=False)

            # We need to check if there are more memberships to get
            # before we filter out the passive memberships.
            if len(ms_list) < no_of_confs:
                has_more = False
            else:
                has_more = True

            memberships = []
            for membership in ms_list:
                if (not passive) and membership.type.passive:
                    continue
                memberships.append(KomMembership(pers_no, membership))

        return memberships, has_more

    @check_connection
    async def get_membership_unreads(self, pers_no):
        conf_nos = await self._client.request(requests.ReqGetUnreadConfs(pers_no))
        memberships = [ await self.get_membership_unread(pers_no, conf_no)
                        for conf_no in conf_nos ]
        return [ m for m in memberships if m.no_of_unread > 0 ]

    @check_connection
    async def get_conf_name(self, conf_no):
        return await self._client.conf_name(conf_no)

    @check_connection
    async def get_conference(self, conf_no, micro=True):
        conf_no = int(conf_no)
        if micro:
            return KomUConference(conf_no, await self._client.uconferences.get(conf_no))
        else:
            return KomConference(conf_no, await self._client.conferences.get(conf_no))

    @check_connection
    async def get_text(self, text_no):
        text_stat = await self.get_text_stat(text_no)
        text = await self._client.request(requests.ReqGetText(text_no))
        return KomText(text_no=text_no, text=text, text_stat=text_stat)

    # TODO: offset/start number, so we can paginate. we probably need
    # to return the local text number for that.
    @check_connection
    async def get_last_texts(self, conf_no, no_of_texts, offset=0, full_text=False):
        """Get the {no_of_texts} last texts in conference {conf_no},
        starting from {offset}.
        """
        #local_no_ceiling = 0 # means the higest numbered texts (i.e. the last)
        text_mapping = await self._client.request(
            requests.ReqLocalToGlobalReverse(conf_no, 0, no_of_texts))
        texts = [ KomText(text_no=m[1], text=None, text_stat=await self.get_text_stat(m[1]))
                  for m in text_mapping.list if m[1] != 0 ]
        texts.reverse()
        return texts

    @check_connection
    async def create_text(self, subject, body, content_type, content_encoding=None,
                    recipient_list=None, comment_to_list=None):
        # decode if not already unicode (assuming utf-8)
        if isinstance(subject, six.binary_type):
            subject = subject.decode('utf-8')
        if isinstance(body, six.binary_type):
            body = body.decode('utf-8')
        if isinstance(content_type, six.binary_type):
            content_type = content_type.decode('utf-8')

        if content_encoding is not None:
            if content_encoding == "base64":
                body = base64.b64decode(body)
            else:
               raise ValueError("Invalid content_encoding: %s", content_encoding)

        # wtf are we doing here?
        mime_type, _ = utils.parse_content_type(content_type)
        content_type = utils.mime_type_tuple_to_str(mime_type)
        mime_type = mimeparse.parse_mime_type(content_type)

        if mime_type[0] == 'text':
            # We hard code utf-8 because it is The Correct Encoding. :)
            mime_type[2]['charset'] = 'utf-8'
            fulltext = subject + "\n" + body
            fulltext = fulltext.encode('utf-8')
        elif mime_type[0] == 'x-kom' and mime_type[1] == 'user-area':
            # Charset doesn't seem to be specified for user areas, but
            # in reality they contain Latin 1 text.
            fulltext = body.encode('latin-1')
        elif mime_type[0] == 'image':
            # We handle images in the same way as AndroKOM. That means
            # that the subject is encoded with latin-1, and the stored
            # text is latin-1-subject + "\n" + binary-body. Content
            # type is "image/jpeg; name=image:<???>". Note that there
            # is no information regarding how subjects are encoded.
            #
            # TODO: What do we do if we can't encode the subject with
            # latin-1?
            fulltext = subject.encode('latin-1') + b"\n" + body
        else:
            raise KomSessionError("Unhandled content type: %s" % (mime_type,))


        misc_info = CookedMiscInfo()

        if recipient_list is not None:
            for r in recipient_list:
                misc_info.recipient_list.append(
                    MIRecipient(type=MIRecipient_str_to_type[r['type']],
                                recpt=r['recpt']['conf_no']))

        if comment_to_list is not None:
            for ct in comment_to_list:
                misc_info.comment_to_list.append(
                    MICommentTo(type=MICommentTo_str_to_type[ct['type']],
                                text_no=ct['text_no']))

        aux_items = []

        # We need to make sure all aux items are encoded.
        creating_software = "%s %s" % (self._client_name, self._client_version)
        aux_items.append(AuxItemInput(tag=komauxitems.AI_CREATING_SOFTWARE,
                                      data=creating_software.encode('utf-8')))
        aux_items.append(AuxItemInput(tag=komauxitems.AI_CONTENT_TYPE,
                                 data=utils.mime_type_tuple_to_str(mime_type).encode('utf-8')))

        text_no = await self._client.request(
            requests.ReqCreateText(fulltext, misc_info, aux_items))
        stats.set('komsession.texts.created.last', 1, agg='sum')
        return text_no

    @check_connection
    async def mark_as_read(self, text_no):
        text_stat = await self.get_text_stat(text_no)
        for mi in text_stat.misc_info.recipient_list:
            await self._client.mark_as_read_local(mi.recpt, mi.loc_no)

    @check_connection
    async def mark_as_unread(self, text_no):
        text_stat = await self.get_text_stat(text_no)
        for mi in text_stat.misc_info.recipient_list:
            await self._client.mark_as_unread_local(mi.recpt, mi.loc_no)

    @check_connection
    async def set_unread(self, conf_no, no_of_unread):
        await self._client.request(requests.ReqSetUnread(conf_no, no_of_unread))

    @check_connection
    async def get_marks(self):
        return await self._client.request(requests.ReqGetMarks())

    @check_connection
    async def mark_text(self, text_no, mark_type):
        await self._client.mark_text(text_no, mark_type)

    @check_connection
    async def unmark_text(self, text_no):
        await self._client.unmark_text(text_no)

    @check_connection
    async def get_user_area_block(self, pers_no, block_name, json_decode=True):
        """Get the block with the given block name from the user area
        for the given person. If there is no user area for the person,
        or if there is no block with the given name, None will be
        returned.

        If json_decode is True (default), the stored block will be
        passed to json.loads() before it is returned.

        If json_decode is False, then the block will be returned as a
        string.
        """
        person_stat = await self._client.request(requests.ReqGetPersonStat(pers_no))

        if person_stat.user_area == 0:
            # No user area
            return None

        # TODO: don't use external get_text method here - it should decode the body,
        # but we don't want to do that.
        text = await self.get_text(person_stat.user_area)
        if text.content_type != 'x-kom/user-area':
            raise KomSessionError(
                "Unknown content type for user area text: %s" % (text.content_type,))

        blocks = utils.decode_user_area(text.body.encode('latin1')) #HACK
        block = blocks.get(block_name, None)
        if block is not None and json_decode:
            block = json.loads(block.decode('latin1')) #HACK

        return block

    @check_connection
    async def set_user_area_block(self, pers_no, block_name, block, json_encode=True):
        """Set the block with the given block name in the user area
        for the given person. Will create a new text and set as the
        new user area for the person. If there already is a block with
        the given name, it will be over-written. The other blocks in
        the user area will copied to the new user area.

        If json_encode is True (default), the block will be passed to
        json.dumps() before it is saved.

        If json_encode is False, then the block should be a string
        that can be hollerith encoded.
        """
        person_stat = await self._client.request(requests.ReqGetPersonStat(pers_no))

        if person_stat.user_area == 0:
            # No existing user area, initiate a new dictionary of
            # blocks.
            blocks = dict()
        else:
            # TODO: don't use external get_text method here - it
            # should decode the body, but we don't want to do that.
            user_area = await self.get_text(person_stat.user_area)
            if user_area.content_type != 'x-kom/user-area':
                raise KomSessionError(
                    "Unknown content type for user area text: %s" % (user_area.content_type,))

            blocks = utils.decode_user_area(user_area.body.encode('latin1')) # HACK

        if json_encode:
            blocks[block_name] = json.dumps(block).encode('latin1') # HACK
        else:
            blocks[block_name] = block

        new_user_area_text_no = await self.create_text(
            subject=None,
            body=utils.encode_user_area(blocks),
            content_type='x-kom/user-area')
        await self._client.request(requests.ReqSetUserArea(pers_no, new_user_area_text_no))
        # TODO: Should it remove the old user area?
