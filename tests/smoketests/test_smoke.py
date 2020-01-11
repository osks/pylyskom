import socket

import pytest

from pylyskom import requests
from pylyskom.connection import Connection
from pylyskom.cachedconnection import Client
from pylyskom.komsession import KomSession, KomText


pytestmark = pytest.mark.smoketest

client_name = "pylyskom-smoketest"
client_version = "1.0"
username = "pylyskom-smoketest"
hostname = socket.getfqdn()
host = "localhost"
port = 4894
pers_no = 34
person = "Test User"
password = "testuser123"


def test_client_connect_disconnect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    conn = Connection(s, username)
    client = Client(conn)
    client.request(requests.ReqDisconnect(0)) # 0 means current session
    client.close()


def test_client_login_logout():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    conn = Connection(s, username)
    client = Client(conn)
    client.request(requests.ReqLogin(pers_no, password, invisible=0))
    client.request(requests.ReqLogout())
    client.close()


def test_komsession_connect_disconnect():
    ks = KomSession()
    ks.connect(host, port, username, hostname, client_name, client_version)
    ks.disconnect()


def test_komsession_login_logout():
    ks = KomSession()
    ks.connect(host, port, username, hostname, client_name, client_version)
    ks.login(pers_no, password)
    ks.logout()
    ks.disconnect()


def test_komtext_create_new_text():
    ks = KomSession()
    ks.connect(host, port, username, hostname, client_name, client_version)
    ks.login(pers_no, password)

    subject = "Hello"
    body = "World"
    content_type = "text/plain"
    recipient_list = [ { "type": "to", "recpt": { "conf_no": ks.get_person_no() } } ]
    new_text = KomText.create_new_text(
        subject, body, content_type,
        recipient_list=recipient_list)

    text_no = ks.create_text(subject, body, content_type, recipient_list=recipient_list)
    created_text = ks.get_text(text_no)

    ks.logout()
    ks.disconnect()

    #print("OSKAR: ", created_text.text_content_type)
    assert new_text.text == created_text.text
    assert new_text.text_content_type == created_text.text_content_type
    assert new_text.content_type == created_text.content_type
