# -*- coding: utf-8 -*-
import pytest

from pylyskom.protocol import MAX_TEXT_SIZE
from pylyskom.datatypes import PrivBits, ConfType, ExtendedConfType, LocalTextNo
from pylyskom import requests


def test_all_requests_has_response_type():
    for k in requests.Requests.__dict__:
        if k.startswith("__"):
            continue
        call_no = getattr(requests.Requests, k)
        assert call_no in requests.response_dict

def test_request_to_string_raises():
    r = requests.OldRequest()
    with pytest.raises(Exception):
        r.to_string()

def test_ReqLogout():
    r = requests.ReqLogout()
    assert r.to_string() == "1\n"

def test_ReqChangeConference():
    r = requests.ReqChangeConference(14506)
    assert r.to_string() == "2 14506\n"

def test_ReqChangeConference_constructor():
    r1 = requests.ReqChangeConference(14506)
    assert r1.to_string() == "2 14506\n"
    assert r1.conf_no == 14506
    r2 = requests.ReqChangeConference(conf_no=14506)
    assert r2.to_string() == "2 14506\n"
    assert r2.conf_no == 14506
    with pytest.raises(TypeError):
        requests.ReqChangeConference()
    with pytest.raises(TypeError):
        requests.ReqChangeConference(14506, conf_no=14506)
    with pytest.raises(TypeError):
        requests.ReqChangeConference(foo=14506)
    
def test_ReqChangeName():
    r = requests.ReqChangeName(14506, u'R\xe4ksm\xf6rg\xe5s')
    assert r.to_string() == "3 14506 10HR\xe4ksm\xf6rg\xe5s\n"

def test_ReqChangeName_constructor():
    r1 = requests.ReqChangeName(14506, "foo")
    assert r1.to_string() == "3 14506 3Hfoo\n"
    assert r1.conf_no == 14506

    r2 = requests.ReqChangeName(conf_no=14506, new_name="foo")
    assert r2.to_string() == "3 14506 3Hfoo\n"
    assert r2.conf_no == 14506

    r3 = requests.ReqChangeName(14506, new_name="foo")
    assert r3.to_string() == "3 14506 3Hfoo\n"
    assert r3.conf_no == 14506

    with pytest.raises(TypeError):
        requests.ReqChangeName()
    with pytest.raises(TypeError):
        requests.ReqChangeName(14506, conf_no=14506)
    with pytest.raises(TypeError):
        requests.ReqChangeName("foo", conf_no=14506)
    with pytest.raises(TypeError):
        requests.ReqChangeName(14506, "foo", conf_no=14506)
    with pytest.raises(TypeError):
        requests.ReqChangeName(14506, "foo", new_name="foo")
    with pytest.raises(TypeError):
        requests.ReqChangeName(14506, "foo", conf_no=14506, new_name="foo")

def test_ReqChangeWhatIAmDoing():
    r = requests.ReqChangeWhatIAmDoing('what')
    assert r.to_string() == "4 4Hwhat\n"

def test_ReqSetPrivBits():
    priv = PrivBits()
    r = requests.ReqSetPrivBits(14506, priv)
    assert r.to_string() == "7 14506 0000000000000000\n"

def test_ReqSetPasswd():
    r = requests.ReqSetPasswd(14506, "oldpwd", "newpassword")
    assert r.to_string() == "8 14506 6Holdpwd 11Hnewpassword\n"

def test_ReqDeleteConf():
    r = requests.ReqDeleteConf(14506)
    assert r.to_string() == "11 14506\n"

def test_ReqSubMember():
    r = requests.ReqSubMember(14506, 14507)
    assert r.to_string() == "15 14506 14507\n"

def test_ReqSetPresentation():
    r = requests.ReqSetPresentation(14506, 4711)
    assert r.to_string() == "16 14506 4711\n"

def test_ReqSetEtcMoTD():
    r = requests.ReqSetEtcMoTD(14506, 4711)
    assert r.to_string() == "17 14506 4711\n"

def test_ReqSetSupervisor():
    r = requests.ReqSetSupervisor(6, 14506)
    assert r.to_string() == "18 6 14506\n"

def test_ReqSetPermittedSubmitters():
    r = requests.ReqSetPermittedSubmitters(123, 456)
    assert r.to_string() == "19 123 456\n"

def test_ReqSetSuperConf():
    r = requests.ReqSetSuperConf(14506, 6)
    assert r.to_string() == "20 14506 6\n"

def test_ReqSetConfType():
    conf_type = ConfType([1, 1, 1, 1])
    r1 = requests.ReqSetConfType(14506, conf_type)
    assert r1.to_string() == "21 14506 11110000\n"

    ext_conf_type = ExtendedConfType()
    r2 = requests.ReqSetConfType(14506, ext_conf_type)
    assert r2.to_string() == "21 14506 00000000\n"

def test_ReqGetText():
    r = requests.ReqGetText(123, 17, 65535)
    assert r.to_string() == "25 123 17 65535\n"

def test_ReqGetText_with_defaults():
    r = requests.ReqGetText(123)
    assert r.to_string() == "25 123 0 %d\n" % MAX_TEXT_SIZE

def test_ReqGetText_with_default_endchar():
    r = requests.ReqGetText(123, 0)
    assert r.to_string() == "25 123 0 %d\n" % MAX_TEXT_SIZE

def test_ReqGetText_with_default_start_char():
    r = requests.ReqGetText(123, start_char=17)
    assert r.to_string() == "25 123 17 %d\n" % MAX_TEXT_SIZE

def test_ReqMarkAsRead():
    r = requests.ReqMarkAsRead(14506, [])
    assert r.to_string() == "27 14506 0 {  }\n"

    r = requests.ReqMarkAsRead(14506, [LocalTextNo(17), LocalTextNo(4711)])
    assert r.to_string() == "27 14506 2 { 17 4711 }\n"

    r = requests.ReqMarkAsRead(14506, [17, 4711])
    assert r.to_string() == "27 14506 2 { 17 4711 }\n"

def test_ReqAddRecipient():
    r = requests.ReqAddRecipient(1, 5)
    assert r.to_string() == "30 1 5 0\n"

    r = requests.ReqAddRecipient(1, 5, 0)
    assert r.to_string() == "30 1 5 0\n"

    r = requests.ReqAddRecipient(1, 5, 1)
    assert r.to_string() == "30 1 5 1\n"
    

def test_ReqAcceptAsync():
    r1 = requests.ReqAcceptAsync([])
    assert r1.to_string() == "80 0 {  }\n"
    assert repr(r1) == "ReqAcceptAsync(request_list=[])"

    r2 = requests.ReqAcceptAsync([1, 3])
    assert r2.to_string() == "80 2 { 1 3 }\n"
    assert repr(r2) == "ReqAcceptAsync(request_list=[1, 3])"

def test_ReqLookupZName_handles_unicode_string():
    name = u'bj\xf6rn'
    r = requests.ReqLookupZName(name, 1, 0)
    assert r.to_string() == '76 5Hbj\xf6rn 1 0\n'

def test_ReqSendMessage_handles_unicode_string():
    msg = u'hej bj\xf6rn'
    r = requests.ReqSendMessage(123, msg)
    assert r.to_string() == '53 123 9Hhej bj\xf6rn\n'

def test_ReqLogin_handles_unicode_string():
    pwd = u'xyz123bj\xf6rn'
    r = requests.ReqLogin(123, pwd)
    assert r.to_string() == '62 123 11Hxyz123bj\xf6rn 1\n'

def test_ReqSetClientVersion_handles_unicode_string():
    name = u'bj\xf6rn'
    version = u'123.bj\xf6rn'
    r = requests.ReqSetClientVersion(name, version)
    assert r.to_string() == '69 5Hbj\xf6rn 9H123.bj\xf6rn\n'
