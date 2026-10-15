from decimal import Decimal

import pytest

from app.deribit_client import DeribitError
from app.services import collect_prices
from app.tickers import Ticker


class FakeClient:
    def __init__(self, prices: dict[Ticker, Decimal | Exception]) -> None:
        self._prices = prices

    async def get_index_price(self, ticker: Ticker) -> Decimal:
        value = self._prices[ticker]
        if isinstance(value, Exception):
            raise value
        return value


async def test_every_ticker_gets_the_same_timestamp():
    client = FakeClient({Ticker.BTC_USD: Decimal("60000"), Ticker.ETH_USD: Decimal("3000")})

    prices = await collect_prices(client, list(Ticker), clock=lambda: 1_700_000_000.9)

    assert [(p.ticker, p.price, p.timestamp) for p in prices] == [
        ("btc_usd", Decimal("60000"), 1_700_000_000),
        ("eth_usd", Decimal("3000"), 1_700_000_000),
    ]


async def test_a_failing_ticker_does_not_lose_the_others():
    client = FakeClient({Ticker.BTC_USD: DeribitError("down"), Ticker.ETH_USD: Decimal("3000")})

    prices = await collect_prices(client, list(Ticker), clock=lambda: 1)

    assert [p.ticker for p in prices] == ["eth_usd"]


async def test_raises_when_nothing_could_be_fetched():
    client = FakeClient({Ticker.BTC_USD: DeribitError("down"), Ticker.ETH_USD: DeribitError("down")})

    with pytest.raises(DeribitError):
        await collect_prices(client, list(Ticker), clock=lambda: 1)
