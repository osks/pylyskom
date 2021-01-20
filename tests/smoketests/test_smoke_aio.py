import random
import socket

import pytest

from pylyskom import requests, asyncmsg
from pylyskom.aio import AioConnection, AioClient, AioKomSession
from pylyskom.errors import UndefinedConference
from pylyskom.komsession import KomText

pytestmark = [pytest.mark.asyncio, pytest.mark.smoketest]

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
    await conn.send_request(req)
    await conn.read_response()
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


async def test_aioclient_async_task():
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


async def test_komtext_create_new_text():
    ks = AioKomSession()
    await ks.connect(host, port, username, hostname, client_name, client_version)
    await ks.login(pers_no, password)

    subject = "Hello"
    body = "World"
    content_type = "text/plain"
    recipient_list = [ { "type": "to", "recpt": { "conf_no": pers_no } } ]
    new_text = KomText.create_new_text(
        subject, body, content_type,
        recipient_list=recipient_list)

    text_no = await ks.create_text(subject, body, content_type, recipient_list=recipient_list)
    created_text = await ks.get_text(text_no)

    await ks.logout()
    await ks.disconnect()

    assert new_text.text == created_text.text
    assert new_text.text_content_type == created_text.text_content_type
    assert new_text.content_type == created_text.content_type


async def test_get_deleted_person():
    #print()
    # random number in case cleanup fails
    nr = random.randint(0, 2**32)
    temp_person = f"Test User Temporary {nr}"
    temp_password = password
    temp_conf_name = f"Test Conf Temporary {nr}"

    # Setup
    ks1 = AioKomSession()
    await ks1.connect(host, port, username, hostname, client_name, client_version)
    temp_person = await ks1.create_person(temp_person, temp_password)
    temp_pers_no = temp_person.pers_no
    #print(f"temp_pers_no: {temp_pers_no}")
    await ks1.login(temp_pers_no, temp_password)

    # Delete temp user
    await ks1.delete_conference(temp_pers_no)
    await ks1.logout()
    await ks1.disconnect()

    # Login with existing user and try to get person. Because of
    # caching of the deleted user, we want to create a new connection.
    ks2 = AioKomSession()
    await ks2.connect(host, port, username, hostname, client_name, client_version)
    await ks2.login(pers_no, password)

    with pytest.raises(UndefinedConference):
        await ks2.get_person(temp_pers_no)

    with pytest.raises(UndefinedConference):
        await ks2.get_conference(temp_pers_no, micro=False)

    with pytest.raises(UndefinedConference):
        await ks2.get_conference(temp_pers_no, micro=True)

    await ks2.logout()
    await ks2.disconnect()


async def test_read_conference_where_author_does_not_exist():
    print()
    # random number in case cleanup fails
    nr = random.randint(0, 2**32)
    temp_person = f"Test User Temporary {nr}"
    temp_password = password
    temp_conf_name = f"Test Conf Temporary {nr}"

    # Setup
    ks1 = AioKomSession()
    await ks1.connect(host, port, username, hostname, client_name, client_version)
    temp_person = await ks1.create_person(temp_person, temp_password)
    temp_pers_no = temp_person.pers_no
    print(f"temp_pers_no: {temp_pers_no}")
    await ks1.login(temp_pers_no, temp_password)
    temp_conf_no = await ks1.create_conference(temp_conf_name)
    print(f"temp_uconf_no: {temp_conf_no}")

    # Delete temp user
    await ks1.delete_conference(temp_pers_no)
    await ks1.logout()
    await ks1.disconnect()

    # Login with existing user and try to get conference. Because of
    # caching of the deleted user, we want to create a new connection.
    ks2 = AioKomSession()
    await ks2.connect(host, port, username, hostname, client_name, client_version)
    await ks2.login(pers_no, password)
    rm_temp_conf = await ks2.get_conference(temp_conf_no, micro=False)
    rm_temp_uconf = await ks2.get_conference(temp_conf_no, micro=True)

    await ks2.logout()
    await ks2.disconnect()


async def test_read_conference_where_author_does_not_exist():
    #print()
    # random number in case cleanup fails
    nr = random.randint(0, 2**32)
    temp_person = f"Test User Temporary {nr}"
    temp_password = password
    temp_conf_name = f"Test Conf Temporary {nr}"

    # Setup
    ks1 = AioKomSession()
    await ks1.connect(host, port, username, hostname, client_name, client_version)
    temp_person = await ks1.create_person(temp_person, temp_password)
    temp_pers_no = temp_person.pers_no
    #print(f"temp_pers_no: {temp_pers_no}")
    await ks1.login(temp_pers_no, temp_password)
    temp_conf_no = await ks1.create_conference(temp_conf_name)
    #print(f"temp_uconf_no: {temp_conf_no}")

    # Delete temp user
    await ks1.delete_conference(temp_pers_no)
    await ks1.logout()
    await ks1.disconnect()

    # Login with existing user and try to get conference. Because of
    # caching of the deleted user, we want to create a new connection.
    ks2 = AioKomSession()
    await ks2.connect(host, port, username, hostname, client_name, client_version)
    await ks2.login(pers_no, password)
    rm_temp_uconf = await ks2.get_conference(temp_conf_no, micro=True)
    rm_temp_conf = await ks2.get_conference(temp_conf_no, micro=False)

    await ks2.logout()
    await ks2.disconnect()
