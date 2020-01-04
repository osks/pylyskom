# -*- coding: utf-8 -*-

import pytest

from .mocks import MockSocket

from pylyskom.connection import Connection
from pylyskom.errors import BadInitialResponse, BadRequestId, UndefinedPerson
from pylyskom.datatypes import (
    CookedMiscInfo,
    ExtendedConfType,
    Mark,
    Membership11,
    MembershipType,
    Stats,
    TextStat,
    Time,
    UConference,
    WhoInfo)
from pylyskom.asyncmsg import AsyncMessages
from pylyskom.requests import (
    ReqAcceptAsync,
    ReqGetMarks,
    ReqGetStats,
    ReqGetStatsDescription,
    ReqGetText,
    ReqGetTime,
    ReqGetUnreadConfs,
    ReqGetUconfStat,
    ReqGetVersionInfo,
    ReqQueryAsync,
    ReqQueryReadTexts10,
    ReqQueryReadTexts11)


def test_connection_constructor_raises_if_bad_response():
    s = MockSocket(b"this is not a valid initial response")
    with pytest.raises(BadInitialResponse):
        Connection(s)

def test_connection_constructor_succeeds_if_correct_response():
    s = MockSocket(b"LysKOM\n")
    Connection(s)

def test_connection_constructor_sends_initialization():
    s = MockSocket(b"LysKOM\n")
    Connection(s, user="oskar")
    assert s.send_data == b"A5Hoskar\n"

def test_connection_send_request_sets_ref_no_1_for_first_request():
    s = MockSocket([b"LysKOM\n", b""])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqAcceptAsync([]))
    assert sent_ref_no == 1

def test_connection_send_request_increases_ref_no_for_each_request():
    s = MockSocket([b"LysKOM\n", b""])
    c = Connection(s)
    sent_ref_no_1 = c.send_request(ReqAcceptAsync([]))
    sent_ref_no_2 = c.send_request(ReqAcceptAsync([]))
    assert sent_ref_no_1 == 1
    assert sent_ref_no_2 == 2

def test_connection_send_request_sends_request_to_socket():
    s = MockSocket([b"LysKOM\n"])
    c = Connection(s)
    c.send_request(ReqAcceptAsync([]))
    assert s.send_data == b"A0H\n1 80 0 { }\n"

def test_connection_read_response_raises_bad_request_id_if_there_is_no_outstanding_request():
    s = MockSocket([b"LysKOM\n", b"=1 25HYawn Nothing is happening\n"])
    c = Connection(s)
    with pytest.raises(BadRequestId):
        c.read_response()
    assert s.recv_data == b""

def test_connection_read_response_handles_ok_reply():
    s = MockSocket([b"LysKOM\n", b"=1 25HYawn Nothing is happening\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqGetText(12345))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == b"Yawn Nothing is happening"
    assert error is None

def test_connection_read_response_handles_error_reply():
    s = MockSocket([b"LysKOM\n", b"%1 10 12345\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqGetUnreadConfs(12345))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp is None
    assert isinstance(error, UndefinedPerson)
    assert error.args == (12345,)

def test_connection_read_response_returns_responses_in_received_order():
    s = MockSocket([b"LysKOM\n", b"=2 6HText 2\n", b"=1 6HText 1\n"])
    c = Connection(s)
    ref1 = c.send_request(ReqGetText(1))
    ref2 = c.send_request(ReqGetText(2))
    resp1 = c.read_response()
    resp2 = c.read_response()
    assert resp1 == (ref2, b"Text 2", None)
    assert resp2 == (ref1, b"Text 1", None)


def test_connection_read_response_can_parse_version_info():
    s = MockSocket([b"LysKOM\n", b"=1 9 7Hlyskomd 5H1.9.0\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqGetVersionInfo())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp.protocol_version == 9
    assert resp.server_software == b"lyskomd"
    assert resp.software_version == b"1.9.0"
    assert error is None

def test_connection_read_response_can_parse_get_marks():
    s = MockSocket([b"LysKOM\n", b"=1 3 { 13020 100 13043 95 12213 95 }\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqGetMarks())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == [ Mark(13020, 100), Mark(13043, 95), Mark(12213, 95) ]
    assert error is None

def test_connection_read_response_can_parse_get_time():
    s = MockSocket([b"LysKOM\n", b"=1 23 47 19 17 6 97 4 197 1\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqGetTime())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == Time(23, 47, 19, 17, 6, 97, 4, 197, 1)
    assert error is None

def test_connection_read_response_can_parse_async_logout_message():
    s = MockSocket([b"LysKOM\n", b":2 13 14506 7\n"])
    c = Connection(s)
    ref_no, msg, error = c.read_response()
    assert ref_no == None
    assert msg.MSG_NO == AsyncMessages.LOGOUT
    assert msg.person_no == 14506
    assert msg.session_no == 7
    assert error is None

def test_connection_read_response_can_parse_async_IAmOn_message():
    s = MockSocket([b"LysKOM\n", b":5 6 14506 6 123 7Hnothing 5Hoskar\n"])
    c = Connection(s)
    ref_no, msg, error = c.read_response()
    assert ref_no is None
    assert msg.MSG_NO == AsyncMessages.I_AM_ON
    assert msg.info == WhoInfo(14506, 6, 123, b"nothing", b"oskar")
    assert error is None

def test_connection_read_response_can_parse_async_DeletedText_message():
    # TODO: Unsure of how the "number of parameters" argument is
    # specified by the server. This works because it is ignored in the
    # Connection class.
    s = MockSocket([b"LysKOM\n",
                    b":2", # uncertain if this is correct
                    b" 14 ", # msg no
                    b" 12345",
                    b" 32 5 11 12 7 93 1 193 1", # text-stat creation time
                    b" 14506", # text-stat author
                    b" 100", # text-stat no of lines
                    b" 4711", # text-stat no of chars
                    b" 4", # text-stat no of marks
                    b" 0 *", # text-stat misc-info array
                    b" 0 *", # text-stat aux-items array
                    b"\n"])
    c = Connection(s)
    ref_no, msg, error = c.read_response()
    assert ref_no is None
    assert msg.MSG_NO == AsyncMessages.DELETED_TEXT
    assert msg.text_no == 12345
    expected_text_stat = TextStat(
        creation_time=Time(32, 5, 11, 12, 7, 93, 1, 193, 1),
        author=14506, no_of_lines=100, no_of_chars=4711, no_of_marks=4,
        misc_info=CookedMiscInfo(), aux_items=[])
    assert msg.text_stat == expected_text_stat
    assert error is None

def test_connection_read_response_can_parse_async_send_message():
    s = MockSocket([b"LysKOM\n", b":3 12 14506 1234 7Hhej hej\n"])
    c = Connection(s)
    ref_no, msg, error = c.read_response()
    assert ref_no is None
    assert msg.MSG_NO == AsyncMessages.SEND_MESSAGE
    assert msg.recipient == 14506
    assert msg.sender == 1234
    assert msg.message == b"hej hej"
    assert error is None

def test_connection_read_response_can_parse_get_unread_confs():
    s = MockSocket([b"LysKOM\n", b"=1 3 { 1 6 14506 }\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqGetUnreadConfs(12345))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == [ 1, 6, 14506 ]
    assert error is None

def test_connection_read_response_can_parse_query_async():
    s = MockSocket([b"LysKOM\n", b"=1 7 { 0 5 7 9 11 12 13 }\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqQueryAsync())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == [ 0, 5, 7, 9, 11, 12, 13 ]
    assert error is None

def test_connection_read_response_can_parse_query_read_texts_10():
    s = MockSocket([b"LysKOM\n",
                    b"=1",
                    b" 4", # position
                    b" 32 5 11 12 7 93 1 193 1", # last time read
                    b" 1 20 133", # conference, priority, last read text
                    b" 3 { 135 136 137 }", # read texts
                    b" 5", # added by
                    b" 43 8 3 12 7 93 1 193 1", # added at
                    b" 01000000", # membership type
                    b"\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqQueryReadTexts10(6, 1))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp.position == 4
    assert resp.last_time_read == Time(32, 5, 11, 12, 7, 93, 1, 193, 1)
    assert resp.conference == 1
    assert resp.priority == 20
    assert resp.last_text_read == 133
    assert resp.read_texts == [ 135, 136, 137 ]
    assert resp.added_by == 5
    assert resp.added_at == Time(43, 8, 3, 12, 7, 93, 1, 193, 1)
    assert resp.type == MembershipType([0, 1, 0, 0, 0, 0, 0, 0])
    assert error is None


def test_connection_read_response_can_parse_get_stats_description_response():
    s = MockSocket([b"LysKOM\n", b"=1 2 { 3HX-a 3HX-b } 4 { 0 60 300 900 }\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqGetStatsDescription())
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp.what == [ b"X-a", b"X-b" ]
    assert resp.when == [ 0, 60, 300, 900 ]
    assert error is None


def test_connection_read_response_can_parse_get_stats():
    s = MockSocket([b"LysKOM\n", b"=1 2 { 20 0 0 16.11 1.2 1.2e-02 }\n"])
    c = Connection(s)
    sent_ref_no = c.send_request(ReqGetStats("clients"))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert resp == [ Stats(20.0, 0.0, 0.0), Stats(16.11, 1.2, 1.2e-02) ]
    assert error is None

def test_connection_try_to_reproduce_error():
    s = MockSocket([ b'LysKOM\n',
                     b'=1 8 38 33 20 15 4 112 2 135 0 9700 100 0 * 14506 38 33 20 15 4 112 2 135 0 00000000\n', 
                     b'=2 32HAndrokom - Komklient f\xf6r Android 00001000 921 13337\n'])
    c = Connection(s)

    sent_ref_no = c.send_request(ReqQueryReadTexts11(14506, 9700, 0, 0))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert error is None
    expected = Membership11(
        position=8,
        last_time_read=Time(38, 33, 20, 15, 4, 112, 2, 135, 0),
        conference=9700,
        priority=100,
        added_by=14506,
        added_at=Time(38, 33, 20, 15, 4, 112, 2, 135, 0),
        membership_type=[0, 0, 0, 0, 0, 0, 0, 0])
    #print "resp: ", repr(resp)
    #print "expected: ", repr(expected)
    assert resp == expected

    sent_ref_no = c.send_request(ReqGetUconfStat(14391))
    ref_no, resp, error = c.read_response()
    assert ref_no == sent_ref_no
    assert error is None
    expected = UConference(
        name=b"Androkom - Komklient f\xf6r Android",
        conf_type=ExtendedConfType([0, 0, 0, 0, 1, 0, 0, 0]),
        highest_local_no=921,
        nice=13337)
    #print "resp: ", repr(resp)
    #print "expected: ", repr(expected)
    assert resp == expected
    assert s.recv_data == b""
