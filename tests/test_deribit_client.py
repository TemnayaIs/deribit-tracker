from decimal import Decimal

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from app.deribit_client import DeribitClient, DeribitError
from app.tickers import Ticker


class FakeDeribit:
    """A tiny local stand-in for the Deribit public API."""

    def __init__(self) -> None:
        self.status = 200
        self.payload: object = {"jsonrpc": "2.0", "result": {"index_price": 61234.56}}
        self.requested_index_names: list[str] = []

    async def get_index_price(self, request: web.Request) -> web.Response:
        self.requested_index_names.append(request.query["index_name"])
        return web.json_response(self.payload, status=self.status)


@pytest.fixture
async def deribit():
    fake = FakeDeribit()
    app = web.Application()
    app.router.add_get("/api/v2/public/get_index_price", fake.get_index_price)
    server = TestServer(app)
    await server.start_server()
    fake.base_url = str(server.make_url("/api/v2"))
    yield fake
    await server.close()


@pytest.fixture
async def client(deribit):
    async with aiohttp.ClientSession() as session:
        yield DeribitClient(session, deribit.base_url)


async def test_returns_index_price_as_decimal(client, deribit):
    price = await client.get_index_price(Ticker.BTC_USD)

    assert price == Decimal("61234.56")
    assert deribit.requested_index_names == ["btc_usd"]


async def test_asks_for_the_requested_ticker(client, deribit):
    await client.get_index_price(Ticker.ETH_USD)

    assert deribit.requested_index_names == ["eth_usd"]


async def test_deribit_error_payload_is_reported(client, deribit):
    deribit.payload = {"jsonrpc": "2.0", "error": {"code": 10004, "message": "invalid_params"}}

    with pytest.raises(DeribitError, match="invalid_params"):
        await client.get_index_price(Ticker.BTC_USD)


async def test_http_error_is_reported(client, deribit):
    deribit.status = 503

    with pytest.raises(DeribitError):
        await client.get_index_price(Ticker.BTC_USD)


async def test_malformed_payload_is_reported(client, deribit):
    deribit.payload = {"result": {}}

    with pytest.raises(DeribitError, match="unexpected response"):
        await client.get_index_price(Ticker.BTC_USD)


async def test_unreachable_server_is_reported():
    async with aiohttp.ClientSession() as session:
        client = DeribitClient(session, "http://127.0.0.1:1/api/v2")

        with pytest.raises(DeribitError):
            await client.get_index_price(Ticker.BTC_USD)
