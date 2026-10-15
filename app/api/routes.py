from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_price_repository
from app.repository import PriceRepository
from app.schemas import PriceOut
from app.tickers import Ticker

router = APIRouter(prefix="/prices", tags=["prices"])

TickerQuery = Annotated[Ticker, Query(description="btc_usd or eth_usd")]
LimitQuery = Annotated[int, Query(ge=1, le=10_000)]
OffsetQuery = Annotated[int, Query(ge=0)]
Repository = Annotated[PriceRepository, Depends(get_price_repository)]


@router.get("", response_model=list[PriceOut], summary="All stored prices for a ticker")
def list_prices(
    ticker: TickerQuery,
    repository: Repository,
    limit: LimitQuery = 1000,
    offset: OffsetQuery = 0,
):
    return repository.list_by_ticker(ticker, limit, offset)


@router.get("/latest", response_model=PriceOut, summary="Latest stored price for a ticker")
def get_latest_price(ticker: TickerQuery, repository: Repository):
    price = repository.get_latest(ticker)
    if price is None:
        raise HTTPException(status_code=404, detail=f"no data for {ticker.value} yet")
    return price


@router.get(
    "/by-date",
    response_model=list[PriceOut],
    summary="Prices for a ticker within a date range (UNIX timestamps, inclusive)",
)
def list_prices_by_date(
    ticker: TickerQuery,
    repository: Repository,
    date_from: Annotated[int | None, Query(ge=0, description="UNIX time, seconds")] = None,
    date_to: Annotated[int | None, Query(ge=0, description="UNIX time, seconds")] = None,
    limit: LimitQuery = 1000,
    offset: OffsetQuery = 0,
):
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from must not be greater than date_to")
    return repository.list_by_date(ticker, date_from, date_to, limit, offset)
