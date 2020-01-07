import socket

import trio
import pytest

from pylyskom import requests
from pylyskom.aio import AioConnection


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


async def test_aioconnection_connect_close():
    conn = AioConnection(host, port, username)
    await conn.connect()
    await conn.aclose()


async def test_aioconnection_connect_disconnect():
    conn = AioConnection(host, port, username)
    await conn.connect()
    req = requests.ReqDisconnect(0)
    ref_no = await conn.send_request(req)
    print("got ref_no: ", ref_no)
    resp = await conn.read_response()
    print("resp: ", resp)
    await conn.aclose()


async def test_aioconnection_login_logout():
    conn = AioConnection(host, port, username)
    await conn.connect()
    await conn.send_request(requests.ReqLogin(pers_no, password, invisible=0))
    await conn.read_response()
    await conn.send_request(requests.ReqLogout())
    await conn.read_response()
    await conn.send_request(requests.ReqDisconnect(0))
    await conn.read_response()
    await conn.aclose()
