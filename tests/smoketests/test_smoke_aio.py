import socket

import trio
import pytest

from pylyskom import requests, asyncmsg
from pylyskom.aio import AioConnection, AioClient, AioKomSession
from pylyskom.komsession import KomText


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
    resp = await conn.read_response()
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


async def test_aioclient_async_send_message():
    conn = AioConnection()
    client = AioClient(conn)
    await client.connect(host, port, user)
    await client.request(requests.ReqLogin(pers_no, password, invisible=0))

    received_async_messages = []
    async def async_handler(msg):
        #print(f"Received async message: MSG_NO={msg.MSG_NO}: {msg}")
        received_async_messages.append(msg)
    client.set_async_handler(async_handler)

    await client.request(requests.ReqSendMessage(0, "test123"))
    # Test test assumes that the server will send back the AsyncSendMessage fast enough.
    # Send any request to trigger receiving and handling of async messages
    await client.request(requests.ReqUserActive())

    await client.request(requests.ReqLogout())
    await client.request(requests.ReqDisconnect(0))
    await client.close()

    def has_received_message():
        received_message = False
        for msg in received_async_messages:
            if msg.MSG_NO == asyncmsg.AsyncMessages.SEND_MESSAGE:
                if msg.recipient == 0 and msg.message == b"test123":
                    received_message = True
        return received_message

    assert has_received_message() == True


async def test_komsession_login_logout():
    ks = AioKomSession()
    await ks.connect(host, port, username, hostname, client_name, client_version)
    await ks.login(pers_no, password)
    await ks.logout()
    await ks.disconnect()
    await ks.close()


async def test_komtext_create_new_text():
    ks = AioKomSession()
    await ks.connect(host, port, username, hostname, client_name, client_version)
    await ks.login(pers_no, password)

    subject = "Hello"
    body = "World"
    content_type = "text/plain"
    recipient_list = [ { "type": "to", "recpt": { "conf_no": ks.get_person_no() } } ]
    new_text = KomText.create_new_text(
        subject, body, content_type,
        recipient_list=recipient_list)

    text_no = await ks.create_text(subject, body, content_type, recipient_list=recipient_list)
    created_text = await ks.get_text(text_no)

    await ks.logout()
    await ks.disconnect()

    #print("OSKAR: ", created_text.text_content_type)
    assert new_text.text == created_text.text
    assert new_text.text_content_type == created_text.text_content_type
    assert new_text.content_type == created_text.content_type
