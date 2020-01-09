import socket

import pytest

from pylyskom import requests
from pylyskom.connection import Connection
from pylyskom.cachedconnection import Client
from pylyskom.komsession import KomSession


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
