# -*- coding: utf-8 -*-
"""Tests for how the async client behaves when the server drops the
connection. Uses a fake LysKOM server on localhost that closes the
connection at different points.
"""

import asyncio

import pytest

from pylyskom.aio import AioClient, AioConnection
from pylyskom.requests import ReqGetTime


# Fail instead of hanging if a request never gets woken up.
TIMEOUT = 2


async def start_fake_server(on_connected):
    """Start a server that does the initial handshake and then calls
    on_connected(reader, writer). Returns (server, port)."""
    async def handle(reader, writer):
        await reader.readline()  # initial string "A<user>\n"
        writer.write(b"LysKOM\n")
        await writer.drain()
        await on_connected(reader, writer)

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    return server, port


async def close_after_first_request(reader, writer):
    await reader.readline()
    writer.close()


async def close_immediately(reader, writer):
    writer.close()


async def wait_until_disconnected(client):
    while client.is_connected():
        await asyncio.sleep(0.01)


def test_request_in_flight_raises_when_server_closes_connection():
    async def run():
        server, port = await start_fake_server(close_after_first_request)
        client = AioClient(AioConnection())
        try:
            await client.connect("127.0.0.1", port)
            with pytest.raises(ConnectionResetError):
                await asyncio.wait_for(client.request(ReqGetTime()), TIMEOUT)
        finally:
            await client.close()
            server.close()

    asyncio.run(run())


def test_client_is_disconnected_after_server_closes_connection():
    async def run():
        server, port = await start_fake_server(close_immediately)
        client = AioClient(AioConnection())
        try:
            await client.connect("127.0.0.1", port)
            await asyncio.wait_for(wait_until_disconnected(client), TIMEOUT)
        finally:
            await client.close()
            server.close()

    asyncio.run(run())


def test_request_after_connection_lost_raises():
    async def run():
        server, port = await start_fake_server(close_immediately)
        client = AioClient(AioConnection())
        try:
            await client.connect("127.0.0.1", port)
            await asyncio.wait_for(wait_until_disconnected(client), TIMEOUT)
            with pytest.raises(ConnectionResetError):
                await asyncio.wait_for(client.request(ReqGetTime()), TIMEOUT)
        finally:
            await client.close()
            server.close()

    asyncio.run(run())


async def never_reply(reader, writer):
    # Read requests but never answer, like a dead connection
    while await reader.readline():
        pass


def test_close_wakes_waiting_requests():
    async def run():
        server, port = await start_fake_server(never_reply)
        client = AioClient(AioConnection())
        try:
            await client.connect("127.0.0.1", port)
            request = asyncio.ensure_future(client.request(ReqGetTime()))
            await asyncio.sleep(0.1)
            await asyncio.wait_for(client.close(), TIMEOUT)
            with pytest.raises(ConnectionResetError):
                await asyncio.wait_for(request, TIMEOUT)
        finally:
            await client.close()
            server.close()

    asyncio.run(run())
