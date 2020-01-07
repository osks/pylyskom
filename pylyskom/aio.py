# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 2020 Oskar Skoog. Released under GPL.

from __future__ import absolute_import
import errno

import trio

from .errors import (
    error_dict,
    BadRequestId,
    ReceiveError,
    BadInitialResponse,
    NotEnoughDataInBufferError,
    ProtocolError,
    UnimplementedAsync)

from .protocol import (
    to_hstring,
    read_first_non_ws,
    read_int)

from .requests import response_dict
from .asyncmsg import async_dict
from .stats import stats


# The design of this is pretty ugly. The attempt is to get async io
# with Trio working without having to redesign pylyskom's response
# parsing right now (and while keeping the blocking io implementation
# working).


class AioReceiveBuffer(object):
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
        print("AioReceiveBuffer receive_string: present: {}, length: {}".format(present, length))
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


async def create_connection(host, port, user):
    conn = AioConnection(host, port, user)
    await conn.connect()
    #client = Client(conn)
    #return CachingPersonClient(client)
    # TODO: return ...


class AioConnection(object):
    def __init__(self, host, port, user=None):
        """

        @param user: See Protocol A spec.
        """
        self._host = host
        self._port = port
        if user is None:
            user = ""
        assert isinstance(user, str) # Do we want user to be str or bytes?
        self._user = user

        self._tcp_stream = None
        self._buffer = AioReceiveBuffer()
        self._ref_no = 0 # Last used ID (i.e. increment before use)
        self._outstanding_requests = {} # Ref-No to Request mapping

    async def connect(self):
        print("AioConnection: connecting to {}:{}".format(self._host, self._port))
        self._tcp_stream = await trio.open_tcp_stream(self._host, self._port)

        # Send initial string
        await self._tcp_stream.send_all(b"A%s\n" % (to_hstring(self._user.encode('latin1')),))

        # Wait for answer "LysKOM\n"
        await self._ensure_receive_buffer_size(7)
        resp = self._buffer.receive_string(7)
        if resp != b"LysKOM\n":
            raise BadInitialResponse()
        stats.set('connections.opened.last', 1, agg='sum')

    async def aclose(self):
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
        print("AioConnection: sending data {!r}", request_string)
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
        print("AioConnection: got data {!r}".format(data))
        self._buffer.append(data)

    async def read_response(self):
        while True:
            # Trying to parse a response will consume from the buffer,
            # and to be able to try again we need to keep all of the
            # buffer until we can parse a response.
            buffer_copy = self._buffer.copy()
            try:
                print("AioConnection: Try to parse response from buffer")
                return self._parse_response()
            except NotEnoughDataInBufferError:
                # Continue reading data from stream
                print("AioConnection: NotEnoughDataInBufferError")
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
        resp = response_dict[req.CALL_NO].parse(self._buffer)
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
