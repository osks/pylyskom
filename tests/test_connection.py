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

def test_connection_send_request_sets_ref_no_1_for_first_request():
    s = MockSocket(["LysKOM\n", ""])
    c = Connection(s)
    ref_no = c.send_request(kom.ReqAcceptAsync([]))
    assert ref_no == 1

def test_connection_send_request_increases_ref_no_for_each_request():
    s = MockSocket(["LysKOM\n", ""])
    c = Connection(s)
    ref_no_1 = c.send_request(kom.ReqAcceptAsync([]))
    ref_no_2 = c.send_request(kom.ReqAcceptAsync([]))
    assert ref_no_1 == 1
    assert ref_no_2 == 2

def test_connection_send_request_sends_request_to_socket():
    s = MockSocket(["LysKOM\n"])
    c = Connection(s)
    ref_no = c.send_request(kom.ReqAcceptAsync([]))
    assert s.send_data == "A0H\n1 80 0 {  }\n"

def test_connection_read_response_raises_bad_request_id_if_there_is_no_outstanding_request():
    s = MockSocket(["LysKOM\n", "=1 25HYawn Nothing is happening\n"])
    c = Connection(s)
    with pytest.raises(kom.BadRequestId):
        c.read_response()
    assert s.recv_data == ""

def test_connection_read_response_handles_ok_reply():
    s = MockSocket(["LysKOM\n", "=1 25HYawn Nothing is happening\n"])
    c = Connection(s)
    ref_no = c.send_request(kom.ReqGetText(12345))
    resp = c.read_response()
    assert resp == (ref_no, "Yawn Nothing is happening", None)
    assert s.recv_data == ""

def test_connection_read_response_handles_error_reply():
    s = MockSocket(["LysKOM\n", "%1 10 12345\n"])
    c = Connection(s)
    ref_no = c.send_request(kom.ReqGetUnreadConfs(12345))
    resp = c.read_response()
    assert len(resp) == 3
    assert resp[0] == ref_no
    assert resp[1] is None
    assert isinstance(resp[2], kom.UndefinedPerson)
    assert resp[2].args == (12345,)

def test_connection_read_response_handles_async_msg():
    s = MockSocket(["LysKOM\n", ":2 13 14506 7\n"])
    c = Connection(s)
    resp = c.read_response()
    assert len(resp) == 3
    assert resp[0] == None
    assert isinstance(resp[1], kom.AsyncLogout)
    assert resp[1].person_no == 14506
    assert resp[1].session_no == 7
    assert resp[2] is None

def test_connection_read_response_returns_responses_in_received_order():
    s = MockSocket(["LysKOM\n", "=2 6HText 2\n", "=1 6HText 1\n"])
    c = Connection(s)
    ref1 = c.send_request(kom.ReqGetText(1))
    ref2 = c.send_request(kom.ReqGetText(2))
    resp1 = c.read_response()
    resp2 = c.read_response()
    assert resp1 == (ref2, "Text 2", None)
    assert resp2 == (ref1, "Text 1", None)
