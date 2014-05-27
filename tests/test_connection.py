import pytest
from mock import MagicMock

from pylyskom import kom
from pylyskom.connection import Connection


class MockSocket():
    def __init__(self, recv_data=None):
        self.send_data = ""
        if recv_data is None:
            recv_data = ""
        if isinstance(recv_data, str):
            self.recv_data = recv_data
        else:
            self.recv_data = "".join(recv_data)

    def send(self, s):
        self.send_data += s
        return len(s)

    def recv(self, bufsize):
        i = max(len(self.recv_data), bufsize)
        r = self.recv_data[:i]
        self.recv_data = self.recv_data[i:]
        return r

    def close(self):
        pass


def test_connection_constructor_raises_if_bad_response():
    s = MockSocket("this is not a valid initial response")
    with pytest.raises(kom.BadInitialResponse):
        c = Connection(s)

def test_connection_constructor_succeeds_if_correct_response():
    s = MockSocket("LysKOM\n")
    c = Connection(s)

def test_connection_constructor_sends_initialization():
    s = MockSocket("LysKOM\n")
    c = Connection(s, user="oskar")
    assert s.send_data == "A5Hoskar\n"

def test_connection_send_request_returns_ref_no_1_for_first_request():
    s = MockSocket(["LysKOM\n", ""])
    c = Connection(s)
    ref_no = c.send_request(kom.ReqAcceptAsync([]))
    assert ref_no == 1

def test_connection_send_request_sends_request_to_socket():
    s = MockSocket(["LysKOM\n", ""])
    c = Connection(s)
    ref_no = c.send_request(kom.ReqAcceptAsync([]))
    assert s.send_data == "A0H\n1 80 0 {  }\n"
