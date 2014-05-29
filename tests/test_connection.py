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
    sent_ref_no = c.send_request(kom.ReqAcceptAsync([]))
    assert sent_ref_no == 1

def test_connection_send_request_increases_ref_no_for_each_request():
    s = MockSocket(["LysKOM\n", ""])
    c = Connection(s)
    sent_ref_no_1 = c.send_request(kom.ReqAcceptAsync([]))
    sent_ref_no_2 = c.send_request(kom.ReqAcceptAsync([]))
    assert sent_ref_no_1 == 1
    assert sent_ref_no_2 == 2

def test_connection_send_request_sends_request_to_socket():
    s = MockSocket(["LysKOM\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(kom.ReqAcceptAsync([]))
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
    sent_ref_no = c.send_request(kom.ReqGetText(12345))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == "Yawn Nothing is happening"
    assert error is None

def test_connection_read_response_handles_error_reply():
    s = MockSocket(["LysKOM\n", "%1 10 12345\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(kom.ReqGetUnreadConfs(12345))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp is None
    assert isinstance(error, kom.UndefinedPerson)
    assert error.args == (12345,)

def test_connection_read_response_returns_responses_in_received_order():
    s = MockSocket(["LysKOM\n", "=2 6HText 2\n", "=1 6HText 1\n"])
    c = Connection(s)
    ref1 = c.send_request(kom.ReqGetText(1))
    ref2 = c.send_request(kom.ReqGetText(2))
    resp1 = c.read_response()
    resp2 = c.read_response()
    assert resp1 == (ref2, "Text 2", None)
    assert resp2 == (ref1, "Text 1", None)

def test_connection_read_response_can_parse_version_info():
    s = MockSocket(["LysKOM\n", "=1 9 7Hlyskomd 5H1.9.0\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(kom.ReqGetVersionInfo())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp.protocol_version == 9
    assert resp.server_software == "lyskomd"
    assert resp.software_version == "1.9.0"
    assert error is None

def test_connection_read_response_can_parse_get_marks():
    s = MockSocket(["LysKOM\n", "=1 3 { 13020 100 13043 95 12213 95 }\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(kom.ReqGetMarks())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert len(resp) == 3
    assert resp[0].text_no == 13020
    assert resp[0].type == 100
    assert resp[1].text_no == 13043
    assert resp[1].type == 95
    assert resp[2].text_no == 12213
    assert resp[2].type == 95
    assert error is None

def test_connection_read_response_can_parse_get_time():
    s = MockSocket(["LysKOM\n", "=1 23 47 19 17 6 97 4 197 1\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(kom.ReqGetTime())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp.seconds == 23
    assert resp.minutes == 47
    assert resp.hours == 19
    assert resp.day == 17
    assert resp.month == 6
    assert resp.year == 97
    assert resp.day_of_week == 4
    assert resp.day_of_year == 197
    assert resp.is_dst == 1
    assert error is None

def test_connection_read_response_can_parse_async_logout_msg():
    s = MockSocket(["LysKOM\n", ":2 13 14506 7\n"])
    c = Connection(s)
    ref_no, msg, error = c.read_response()
    assert ref_no == None
    assert msg.person_no == 14506
    assert msg.session_no == 7
    assert error is None

def test_connection_read_response_can_parse_async_send_message():
    s = MockSocket(["LysKOM\n", ":3 12 14506 1234 7Hhej hej\n"])
    c = Connection(s)
    ref_no, msg, error = c.read_response()
    assert ref_no is None
    assert msg.recipient == 14506
    assert msg.sender == 1234
    assert msg.message == "hej hej"
    assert error is None

def test_connection_read_response_can_parse_get_unread_confs():
    s = MockSocket(["LysKOM\n", "=1 3 { 1 6 14506 }\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(kom.ReqGetUnreadConfs(12345))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == [ 1, 6, 14506 ]
    assert error is None

def test_connection_read_response_can_parse_query_async():
    s = MockSocket(["LysKOM\n", "=1 7 { 0 5 7 9 11 12 13 }\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(kom.ReqQueryAsync())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == [ 0, 5, 7, 9, 11, 12, 13 ]
    assert error is None
