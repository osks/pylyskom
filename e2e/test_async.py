import random

import pytest

from pylyskom import requests, asyncmsg
from pylyskom.aio import AioConnection, AioClient, AioKomSession
from pylyskom.errors import UndefinedConference
from pylyskom.komsession import KomText

from conftest import host, port, user, username, hostname, client_name, client_version, person_name, person_password

pytestmark = pytest.mark.asyncio


async def _create_person(name=None, password=None):
    """Create a test person and return (pers_no, password)."""
    name = name or f"{person_name} {random.randint(0, 2**32)}"
    password = password or person_password
    ks = AioKomSession()
    await ks.connect(host, port, username, hostname, client_name, client_version)
    person = await ks.create_person(name, password)
    await ks.disconnect()
    await ks.close()
    return person.pers_no, password


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
    pers_no, passwd = await _create_person()
    conn = AioConnection()
    await conn.connect(host, port, user)
    await conn.send_request(requests.ReqLogin(pers_no, passwd, invisible=0))
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
    pers_no, passwd = await _create_person()
    conn = AioConnection()
    client = AioClient(conn)
    await client.connect(host, port, user)
    await client.request(requests.ReqLogin(pers_no, passwd, invisible=0))
    await client.request(requests.ReqLogout())
    await client.request(requests.ReqDisconnect(0))
    await client.close()


async def test_aioclient_async_send_message():
    pers_no, passwd = await _create_person()
    conn = AioConnection()
    client = AioClient(conn)
    await client.connect(host, port, user)
    await client.request(requests.ReqLogin(pers_no, passwd, invisible=0))

    received_async_messages = []
    async def async_handler(msg):
        received_async_messages.append(msg)
    client.set_async_handler(async_handler)

    await client.request(requests.ReqSendMessage(0, "test123"))
    # Send any request to trigger receiving and handling of async messages
    await client.request(requests.ReqUserActive())

    await client.request(requests.ReqLogout())
    await client.request(requests.ReqDisconnect(0))
    await client.close()

    def has_received_message():
        for msg in received_async_messages:
            if msg.MSG_NO == asyncmsg.AsyncMessages.SEND_MESSAGE:
                if msg.recipient == 0 and msg.message == b"test123":
                    return True
        return False

    assert has_received_message() == True


async def test_aioclient_async_task():
    pers_no, passwd = await _create_person()
    conn = AioConnection()
    client = AioClient(conn)
    await client.connect(host, port, user)
    await client.request(requests.ReqLogin(pers_no, passwd, invisible=0))
    await client.request(requests.ReqLogout())
    await client.request(requests.ReqDisconnect(0))
    await client.close()


async def test_komsession_login_logout():
    pers_no, passwd = await _create_person()
    ks = AioKomSession()
    await ks.connect(host, port, username, hostname, client_name, client_version)
    await ks.login(pers_no=pers_no, passwd=passwd)
    await ks.logout()
    await ks.disconnect()
    await ks.close()


async def test_komtext_create_new_text():
    pers_no, passwd = await _create_person()
    ks = AioKomSession()
    await ks.connect(host, port, username, hostname, client_name, client_version)
    await ks.login(pers_no=pers_no, passwd=passwd)

    subject = "Hello"
    body = "World"
    content_type = "text/plain"
    recipient_list = [{"type": "to", "recpt": {"conf_no": pers_no}}]
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
    nr = random.randint(0, 2**32)
    temp_name = f"Test User Temporary {nr}"

    ks1 = AioKomSession()
    await ks1.connect(host, port, username, hostname, client_name, client_version)
    temp_person = await ks1.create_person(temp_name, person_password)
    temp_pers_no = temp_person.pers_no
    await ks1.login(pers_no=temp_pers_no, passwd=person_password)

    await ks1.delete_conference(temp_pers_no)
    await ks1.logout()
    await ks1.disconnect()

    pers_no, passwd = await _create_person()
    ks2 = AioKomSession()
    await ks2.connect(host, port, username, hostname, client_name, client_version)
    await ks2.login(pers_no=pers_no, passwd=passwd)

    with pytest.raises(UndefinedConference):
        await ks2.get_person(temp_pers_no)

    with pytest.raises(UndefinedConference):
        await ks2.get_conference(temp_pers_no, micro=False)

    with pytest.raises(UndefinedConference):
        await ks2.get_conference(temp_pers_no, micro=True)

    await ks2.logout()
    await ks2.disconnect()


async def test_read_conference_where_author_does_not_exist():
    nr = random.randint(0, 2**32)
    temp_name = f"Test User Temporary {nr}"
    temp_conf_name = f"Test Conf Temporary {nr}"

    ks1 = AioKomSession()
    await ks1.connect(host, port, username, hostname, client_name, client_version)
    temp_person = await ks1.create_person(temp_name, person_password)
    temp_pers_no = temp_person.pers_no
    await ks1.login(pers_no=temp_pers_no, passwd=person_password)
    temp_conf_no = await ks1.create_conference(temp_conf_name)

    await ks1.delete_conference(temp_pers_no)
    await ks1.logout()
    await ks1.disconnect()

    pers_no, passwd = await _create_person()
    ks2 = AioKomSession()
    await ks2.connect(host, port, username, hostname, client_name, client_version)
    await ks2.login(pers_no=pers_no, passwd=passwd)
    await ks2.get_conference(temp_conf_no, micro=False)

    await ks2.logout()
    await ks2.disconnect()


async def test_read_uconference_where_author_does_not_exist():
    nr = random.randint(0, 2**32)
    temp_name = f"Test User Temporary {nr}"
    temp_conf_name = f"Test Conf Temporary {nr}"

    ks1 = AioKomSession()
    await ks1.connect(host, port, username, hostname, client_name, client_version)
    temp_person = await ks1.create_person(temp_name, person_password)
    temp_pers_no = temp_person.pers_no
    await ks1.login(pers_no=temp_pers_no, passwd=person_password)
    temp_conf_no = await ks1.create_conference(temp_conf_name)

    await ks1.delete_conference(temp_pers_no)
    await ks1.logout()
    await ks1.disconnect()

    pers_no, passwd = await _create_person()
    ks2 = AioKomSession()
    await ks2.connect(host, port, username, hostname, client_name, client_version)
    await ks2.login(pers_no=pers_no, passwd=passwd)
    await ks2.get_conference(temp_conf_no, micro=True)

    await ks2.logout()
    await ks2.disconnect()
