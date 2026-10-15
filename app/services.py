import asyncio
import logging
import time
from collections.abc import Callable, Sequence

import aiohttp

from app.config import Settings
from app.deribit_client import DeribitClient, DeribitError
from app.models import Price
from app.tickers import Ticker

logger = logging.getLogger(__name__)


async def collect_prices(
    client: DeribitClient,
    tickers: Sequence[Ticker],
    clock: Callable[[], float] = time.time,
) -> list[Price]:
    """Fetch every ticker concurrently and return rows ready to be stored.

    A failure of one ticker does not discard the others; it is logged and skipped.
    """
    results = await asyncio.gather(
        *(client.get_index_price(ticker) for ticker in tickers),
        return_exceptions=True,
    )
    now = int(clock())  # one timestamp per run, so tickers of the same minute line up
    prices: list[Price] = []
    for ticker, result in zip(tickers, results):
        if isinstance(result, DeribitError):
            logger.warning("skipping %s: %s", ticker.value, result)
        elif isinstance(result, BaseException):
            raise result
        else:
            prices.append(Price(ticker=ticker.value, price=result, timestamp=now))
    if not prices:
        raise DeribitError("no prices could be fetched")
    return prices


async def fetch_current_prices(settings: Settings) -> list[Price]:
    timeout = aiohttp.ClientTimeout(total=settings.request_timeout_seconds)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        client = DeribitClient(session, settings.deribit_base_url)
        return await collect_prices(client, list(Ticker))
