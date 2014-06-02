# -*- coding: utf-8 -*-
# LysKOM Protocol A version 10/11 client interface for Python
# (C) 1999-2002 Kent Engström. Released under GPL.
# (C) 2008 Henrik Rindlöw. Released under GPL.
# (C) 2012-2014 Oskar Skoog. Released under GPL.

import socket
import errno

from .errors import (
    error_dict,
    BadRequestId,
    ReceiveError,
    BadInitialResponse,
    ProtocolError,
    UnimplementedAsync)

from .protocol import (
    to_hstring,
    read_first_non_ws,
    read_int)

from .requests import response_dict
from .async import async_dict


class ReceiveBuffer(object):
    def __init__(self, socket):
        self._socket = socket

        # Receive buffer
        self._rb = ""    # Buffer for data received from connection
        self._rb_len = 0 # Length of the buffer
        self._rb_pos = 0 # Position of first unread byte in buffer

    def receive_string(self, len):
        """Get a string from the receive buffer (receiving more if
        necessary).
        """
        self._ensure_receive_buffer_size(len)
        res = self._rb[self._rb_pos:self._rb_pos+len]
        self._rb_pos = self._rb_pos + len
        return res

    def receive_char(self):
        """Get a character from the receive buffer (receiving more if
        necessary).
        """
        # FIXME: Optimize for speed
        self._ensure_receive_buffer_size(1)
        res = self._rb[self._rb_pos]
        self._rb_pos = self._rb_pos + 1
        return res

    def _ensure_receive_buffer_size(self, size):
        """Ensure that there are at least N bytes in the receive
        buffer."""
        # FIXME: Rewrite for speed and clarity
        present = self._rb_len - self._rb_pos 
        while present < size:
            needed = size - present
            wanted = max(needed,128) # FIXME: Optimize
            #print "Only %d chars present, need %d: asking for %d" % \
            #      (present, size, wanted)
            data = self._socket.recv(wanted)
            if len(data) == 0:
                raise ReceiveError()
            #print("<<<", data)
            self._rb = self._rb[self._rb_pos:] + data
            self._rb_pos = 0
            self._rb_len = len(self._rb)
            present = self._rb_len
        #print "%d chars present (needed %d)" % \
        #      (present, size)
            

#
#class ResponseType(object):
#    """Used as an enum of reply types.
#    """
#    (OK,
#     ERROR,
#     ASYNC) = range(3)
#
#class Response(object):
#    def __init__(self):
#        pass



class Connection(object):
    def __init__(self, sock, user=None):
        self._socket = sock
        if user is None:
            user = ""

        self._buffer = ReceiveBuffer(self._socket)
        self._ref_no = 0 # Last used ID (i.e. increment before use)
        self._outstanding_requests = {} # Ref-No to Request mapping

        # Send initial string 
        self._send_string(("A%s\n" % (to_hstring(user),)).encode('latin1'))

        # Wait for answer "LysKOM\n"
        resp = self._buffer.receive_string(7) # FIXME: receive line here
        if resp != "LysKOM\n":
            raise BadInitialResponse()

    def send_request(self, req):
        return self._send_request(req)

    def read_response(self):
        return self._parse_response()

    def close(self):
        if self._socket is None:
            return

        try:
            self._socket.close()
        except socket.error as (eno, msg):
            if eno in (107, errno.ENOTCONN):
                # 107: Not connected anymore. Didn't find any errno
                # name, but the exception says "[Errno 107] Transport
                # endpoint is not connected".
                pass
            else:
                raise
        finally:
            self._socket = None

    def _send_string(self, s):
        """Send a raw string."""
        while len(s) > 0:
            done = self._socket.send(s)
            s = s[done:]

    def _send_request(self, req):
        self._ref_no += 1
        ref_no = self._ref_no
        assert ref_no not in self._outstanding_requests
        self._send_string("%d %s" % (ref_no, req.to_string()))
        self._outstanding_requests[ref_no] = req
        return ref_no

    def _parse_response(self):
        ch = read_first_non_ws(self._buffer)
        if ch == "=":
            return self._parse_ok_reply()
        elif ch == "%":
            return self._parse_error_reply()
        elif ch == ":":
            return self._parse_asynchronous_message()
        else:
            raise ProtocolError()

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
