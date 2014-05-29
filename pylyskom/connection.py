# -*- coding: utf-8 -*-

import socket
import errno
#from Queue import Queue
#import select

from . import kom
from .request import default_request_factory


#    # Parse all present data
#    def parse_present_data(self):
#        while select.select([self._socket], [], [], 0)[0]:
#            # this seem to be almost the same as what
#            # parse_server_message() does. (There is a difference in
#            # that parse_first_non_ws() loops until it gets a non-ws
#            # char, where the code below instead continues to the
#            # select in the loop. Not sure if it matters.) Therefor it
#            # was replace by calling parse_server_message().
#
#            #ch = self.receive_char()
#            #if ch in kom.WHITESPACE:
#            #    continue
#            #if ch == "=":
#            #    self.parse_ok_reply()
#            #elif ch == "%":
#            #    self.parse_error_reply()
#            #elif ch == ":":
#            #    self.parse_asynchronous_message()
#            #else:
#            #    raise kom.ProtocolError
#            
#            self.parse_server_message()


class BaseConnection(object):
    def __init__(self, sock, user=None):
        """
        @param sock Socket connected to a LysKOM server.
        """
        self._socket = sock
        if user is None:
            user = ""

        # Receive buffer
        self.rb = ""    # Buffer for data received from connection
        self.rb_len = 0 # Length of the buffer
        self.rb_pos = 0 # Position of first unread byte in buffer

        # Send initial string 
        self.send_string(("A%dH%s\n" % (len(user), user)).encode('latin1'))

        # Wait for answer "LysKOM\n"
        resp = self.receive_string(7) # FIXME: receive line here
        if resp != "LysKOM\n":
            raise kom.BadInitialResponse


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


    # PARSING KOM DATA TYPES

    def parse_object(self, cls):
        return cls.parse(self)

    def parse_old_object(self, cls):
        return cls.parse(self, old_format=1)
        
    # PARSING ARRAYS

    def parse_array(self, element_cls):
        len = self.parse_int()
        res = []
        if len > 0:
            left = self.parse_first_non_ws()
            if left == "*":
                # Special case of unwanted data
                return []
            elif left != "{": raise kom.ProtocolError
            for i in range(0, len):
                obj = element_cls.parse(self)
                res.append(obj)
            right = self.parse_first_non_ws()
            if right != "}": raise kom.ProtocolError
        else:
            star = self.parse_first_non_ws()
            if star != "*": raise kom.ProtocolError
        return res

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
            done = self._socket.send(s)
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
            data = self._socket.recv(wanted)
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


class ResponseType(object):
    """Used as an enum of reply types.
    """
    (OK,
     ERROR,
     ASYNC) = range(3)

class Response(object):
    def __init__(self):
        pass


class Connection(BaseConnection):
    def __init__(self, sock, user=None):
        BaseConnection.__init__(self, sock, user)
        self._ref_no = 0 # Last used ID (i.e. increment before use)
        self._outstanding_requests = {} # Ref-No to Request
        
    def send_request(self, req):
        self._ref_no += 1
        ref_no = self._ref_no
        assert ref_no not in self._outstanding_requests
        self.send_string("%d %s" % (ref_no, req.to_string()))
        self._outstanding_requests[ref_no] = req
        return ref_no

    def read_response(self):
        ch = self.parse_first_non_ws()
        if ch == "=":
            return self._parse_ok_reply()
        elif ch == "%":
            return self._parse_error_reply()
        elif ch == ":":
            return self._parse_asynchronous_message()
        else:
            raise kom.ProtocolError()

    def _parse_ok_reply(self):
        ref_no = self.parse_int()
        if ref_no not in self._outstanding_requests:
            raise kom.BadRequestId(ref_no)
        req = self._outstanding_requests[ref_no]
        resp = kom.response_dict[req.CALL_NO].parse(self)
        del self._outstanding_requests[ref_no]
        return ref_no, resp, None

    def _parse_error_reply(self):
        ref_no = self.parse_int()
        if ref_no not in self._outstanding_requests:
            raise kom.BadRequestId(ref_no)
        error_no = self.parse_int()
        error_status = self.parse_int()
        error = kom.error_dict[error_no](error_status)
        del self._outstanding_requests[ref_no]
        return ref_no, None, error

    def _parse_asynchronous_message(self):
        self.parse_int() # read number of arguments (but we don't need it)
        msg_no = self.parse_int()
        if msg_no not in kom.async_dict:
            raise kom.UnimplementedAsync(msg_no)
        msg = kom.async_dict[msg_no].parse(self)
        return None, msg, None
        

class Client(object):
    def __init__(self, conn, request_factory=default_request_factory):
        self._conn = conn
        self._request_factory = request_factory

        self._ok_queue = {}  # Answers received from the server
        self._error_queue = {} # Errors received from the server
        #self._async_queue = Queue()
        self._async_handlers = {}

    def close(self):
        self._conn.close()

    def register_async_handler(self, msg_no, handler):
        """Register a handler for a type of async message.

        @param msg_no Type of async message.

        @param handler Function that should be called when an async
        message of the specified type is received.

        Important: Does not tell the LysKOM server to start sending
        async messages.
        """
        if msg_no not in kom.async_dict:
            raise kom.UnimplementedAsync
        if msg_no in self._async_handlers:
            self._async_handlers[msg_no].append(handler)
        else:
            self._async_handlers[msg_no] = [handler]

    def request(self, request, *args, **kwargs):
        req = self._request_factory.new(request)(*args, **kwargs)
        req_id = self.register_request(req)
        return self.wait_and_dequeue(req_id)

    def register_request(self, req):
        """Register a request to be sent.
        """
        ref_no = self._conn.send_request(req)
        return ref_no

    def wait_and_dequeue(self, ref_no):
        """Wait for a request to be answered, return response or raise
        error.
        """
        while ref_no not in self._ok_queue and \
              ref_no not in self._error_queue:
            self._read_response()

        if ref_no in self._ok_queue:
            resp = self._ok_queue[ref_no]
            del self._ok_queue[ref_no]
            return resp
        elif ref_no in self._error_queue:
            error = self._error_queue[ref_no]
            del self._error_queue[ref_no]
            raise error
        else:
            raise RuntimeError("Got unknown ref-no: %r" % (ref_no,))

    def _read_response(self):
        ref_no, resp, error = self._conn.read_response()
        if ref_no is None:
            # async message

            # TODO: queue or handle?
            #self._async_queue.put(resp)
            self._handle_async_message(resp)
        elif error is not None:
            # error reply
            self._error_queue[ref_no] = error
        else:
            # ok reply - resp can be None
            self._ok_queue[ref_no] = resp

    def _handle_async_message(self, msg):
        if msg.MSG_NO in self._async_handlers:
            for handler in self._async_handlers[msg.MSG_NO]:
                handler(msg, self)
