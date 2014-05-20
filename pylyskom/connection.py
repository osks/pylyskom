# -*- coding: utf-8 -*-

import socket
import errno
import select

from . import kom
from .request import Requests, default_request_factory


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

    def close(self):
        if self.socket is None:
            return

        try:
            self.socket.close()
        except socket.error as (eno, msg):
            if eno in (107, errno.ENOTCONN):
                # 107: Not connected anymore. Didn't find any errno
                # name, but the exception says "[Errno 107] Transport
                # endpoint is not connected".
                pass
            else:
                raise
        finally:
            self.socket = None


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
