import random
import socket

from pylyskom import requests
from pylyskom.connection import Connection
from pylyskom.cachedconnection import Client
from pylyskom.komsession import KomSession, KomText

from conftest import host, port, username, hostname, client_name, client_version, person_name, person_password


def _create_person():
    """Create a test person with a unique name and return pers_no."""
    name = f"{person_name} {random.randint(0, 2**32)}"
    ks = KomSession()
    ks.connect(host, port, username, hostname, client_name, client_version)
    person = ks.create_person(name, person_password)
    ks.disconnect()
    return person.pers_no


def test_client_connect_disconnect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    conn = Connection(s, username)
    client = Client(conn)
    client.request(requests.ReqDisconnect(0))
    client.close()


def test_client_login_logout():
    pers_no = _create_person()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    conn = Connection(s, username)
    client = Client(conn)
    client.request(requests.ReqLogin(pers_no, person_password, invisible=0))
    client.request(requests.ReqLogout())
    client.close()


def test_komsession_connect_disconnect():
    ks = KomSession()
    ks.connect(host, port, username, hostname, client_name, client_version)
    ks.disconnect()


def test_komsession_login_logout():
    pers_no = _create_person()
    ks = KomSession()
    ks.connect(host, port, username, hostname, client_name, client_version)
    ks.login(pers_no, person_password)
    ks.logout()
    ks.disconnect()


def test_komtext_create_new_text():
    pers_no = _create_person()
    ks = KomSession()
    ks.connect(host, port, username, hostname, client_name, client_version)
    ks.login(pers_no, person_password)

    subject = "Hello"
    body = "World"
    content_type = "text/plain"
    recipient_list = [{"type": "to", "recpt": {"conf_no": pers_no}}]
    new_text = KomText.create_new_text(
        subject, body, content_type,
        recipient_list=recipient_list)

    text_no = ks.create_text(subject, body, content_type, recipient_list=recipient_list)
    created_text = ks.get_text(text_no)

    ks.logout()
    ks.disconnect()

    assert new_text.text == created_text.text
    assert new_text.text_content_type == created_text.text_content_type
    assert new_text.content_type == created_text.content_type
