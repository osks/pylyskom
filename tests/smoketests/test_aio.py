import socket

import pytest

from pylyskom import requests
from pylyskom.aio import AioConnection, AioClient, AioKomSession


pytestmark = pytest.mark.smoketest

client_name = "pylyskom-smoketest"
client_version = "1.0"
username = "pylyskom-smoketest"
hostname = socket.getfqdn()
user = username + "%" + hostname
host = "localhost"
port = 4894
pers_no = 34
person = "Test User"
password = "testuser123"


async def test_aioconnection_connect_close():
    conn = AioConnection()
    await conn.connect(host, port, user)
    await conn.close()


async def test_aioconnection_connect_disconnect():
    conn = AioConnection()
    await conn.connect(host, port, user)
    req = requests.ReqDisconnect(0)
    ref_no = await conn.send_request(req)
    print("got ref_no: ", ref_no)
    resp = await conn.read_response()
    print("resp: ", resp)
    await conn.close()


async def test_aioconnection_login_logout():
    conn = AioConnection()
    await conn.connect(host, port, user)
    await conn.send_request(requests.ReqLogin(pers_no, password, invisible=0))
    await conn.read_response()
    await conn.send_request(requests.ReqLogout())
    await conn.read_response()
    await conn.send_request(requests.ReqDisconnect(0))
    await conn.read_response()
    await conn.close()


async def test_aioclient_connect_disconnect():
    conn = AioConnection()
    client = AioClient(conn)
    await client.connect(host, port, user)
    await client.request(requests.ReqDisconnect(0))
    await client.close()


async def test_aioclient_login_logout():
    conn = AioConnection()
    client = AioClient(conn)
    await client.connect(host, port, user)
    await client.request(requests.ReqLogin(pers_no, password, invisible=0))
    await client.request(requests.ReqLogout())
    await client.request(requests.ReqDisconnect(0))
    await client.close()


async def test_komsession_login_logout():
    ks = AioKomSession()
    await ks.connect(host, port, username, hostname, client_name, client_version)
    await ks.login(pers_no, password)
    await ks.logout()
    await ks.disconnect()
    await ks.close()
