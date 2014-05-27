# -*- coding: utf-8 -*-
import pytest

from pylyskom import kom


def test_to_hstring():
    kom.to_hstring('foobar') == '6Hfoobar'

def test_to_hstring__encodes_unicode_to_latin1_by_default():
    hs = kom.to_hstring(u'R\xe4ksm\xf6rg\xe5s')
    assert type(hs) == str
    assert hs == u'10HR\xe4ksm\xf6rg\xe5s'.encode('latin1')

def test_to_hstring__encodes_before_calculating_length():
    hs = kom.to_hstring(u'R\xe4ksm\xf6rg\xe5s', encoding='utf8')
    assert type(hs) == str
    assert hs == '13HR\xc3\xa4ksm\xc3\xb6rg\xc3\xa5s'

def test_request_to_string_raises():
    r = kom.Request()
    with pytest.raises(Exception):
        r.to_string()

def test_ReqLogout():
    r = kom.ReqLogout()
    assert r.to_string() == "1\n"

def test_ReqChangeConference():
    r = kom.ReqChangeConference(14506)
    assert r.to_string() == "2 14506\n"
    
def test_ReqChangeName():
    r = kom.ReqChangeName(14506, u'R\xe4ksm\xf6rg\xe5s')
    assert r.to_string() == "3 14506 10HR\xe4ksm\xf6rg\xe5s\n"

def test_ReqChangeWhatIAmDoing():
    r = kom.ReqChangeWhatIAmDoing('what')
    assert r.to_string() == "4 4Hwhat\n"

def test_ReqSetPrivBits():
    priv = kom.PrivBits()
    r = kom.ReqSetPrivBits(14506, priv)
    assert r.to_string() == "7 14506 0000000000000000\n"

def test_ReqSetPasswd():
    r = kom.ReqSetPasswd(14506, "oldpwd", "newpassword")
    assert r.to_string() == "8 14506 6Holdpwd 11Hnewpassword\n"

def test_ReqDeleteConf():
    r = kom.ReqDeleteConf(14506)
    assert r.to_string() == "11 14506\n"

def test_ReqSubMember():
    r = kom.ReqSubMember(14506, 14507)
    assert r.to_string() == "15 14506 14507\n"

def test_ReqSetPresentation():
    r = kom.ReqSetPresentation(14506, 4711)
    assert r.to_string() == "16 14506 4711\n"

def test_ReqSetEtcMoTD():
    r = kom.ReqSetEtcMoTD(14506, 4711)
    assert r.to_string() == "17 14506 4711\n"

def test_ReqSetSupervisor():
    r = kom.ReqSetSupervisor(6, 14506)
    assert r.to_string() == "18 6 14506\n"

def test_ReqSetPermittedSubmitters():
    r = kom.ReqSetPermittedSubmitters(123, 456)
    assert r.to_string() == "19 123 456\n"

def test_ReqSetSuperConf():
    r = kom.ReqSetSuperConf(14506, 6)
    assert r.to_string() == "20 14506 6\n"

def test_ReqSetSuperConf():
    r = kom.ReqAcceptAsync([])
    assert r.to_string() == "80 0 {  }\n"
