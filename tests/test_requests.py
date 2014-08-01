# -*- coding: utf-8 -*-
import pytest

from pylyskom.datatypes import PrivBits
from pylyskom import requests


def test_all_requests_has_response_type():
    for k in requests.Requests.__dict__:
        if k.startswith("__"):
            continue
        call_no = getattr(requests.Requests, k)
        assert call_no in requests.response_dict

def test_request_to_string_raises():
    r = requests.Request()
    with pytest.raises(Exception):
        r.to_string()

def test_ReqLogout():
    r = requests.ReqLogout()
    assert r.to_string() == "1\n"

def test_ReqChangeConference():
    r = requests.ReqChangeConference(14506)
    assert r.to_string() == "2 14506\n"
    
def test_ReqChangeName():
    r = requests.ReqChangeName(14506, u'R\xe4ksm\xf6rg\xe5s')
    assert r.to_string() == "3 14506 10HR\xe4ksm\xf6rg\xe5s\n"

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

def test_ReqAcceptAsync():
    r = requests.ReqAcceptAsync([])
    assert r.to_string() == "80 0 {  }\n"


def test_ReqLookupZName_handles_unicode_string():
    name = u'bj\xf6rn'
    r = requests.ReqLookupZName(name)
    assert r.to_string() == '76 5Hbj\xf6rn 0 0\n'

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
