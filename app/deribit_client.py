import asyncio
from decimal import Decimal, InvalidOperation
from typing import Any

import aiohttp

from app.tickers import Ticker


class DeribitError(Exception):
    """Deribit is unreachable or answered with something we cannot use."""


class DeribitClient:
    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")

    async def get_index_price(self, ticker: Ticker) -> Decimal:
        url = f"{self._base_url}/public/get_index_price"
        try:
            async with self._session.get(url, params={"index_name": ticker.value}) as response:
                response.raise_for_status()
                payload = await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
            raise DeribitError(f"request for {ticker.value} failed: {exc}") from exc
        return self._parse_index_price(ticker, payload)

    @staticmethod
    def _parse_index_price(ticker: Ticker, payload: Any) -> Decimal:
        if isinstance(payload, dict) and "error" in payload:
            raise DeribitError(f"Deribit returned an error for {ticker.value}: {payload['error']}")
        try:
            # str() first: Decimal(float) would drag binary rounding noise into the DB
            return Decimal(str(payload["result"]["index_price"]))
        except (KeyError, TypeError, InvalidOperation) as exc:
            raise DeribitError(f"unexpected response for {ticker.value}: {payload!r}") from exc
