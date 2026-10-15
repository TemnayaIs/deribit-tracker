from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Price
from app.tickers import Ticker


class PriceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_many(self, prices: Sequence[Price]) -> None:
        self._session.add_all(prices)

    def list_by_ticker(self, ticker: Ticker, limit: int, offset: int) -> Sequence[Price]:
        query = (
            select(Price)
            .where(Price.ticker == ticker.value)
            .order_by(Price.timestamp, Price.id)
            .limit(limit)
            .offset(offset)
        )
        return self._session.scalars(query).all()

    def get_latest(self, ticker: Ticker) -> Price | None:
        query = (
            select(Price)
            .where(Price.ticker == ticker.value)
            .order_by(Price.timestamp.desc(), Price.id.desc())
            .limit(1)
        )
        return self._session.scalars(query).first()

    def list_by_date(
        self,
        ticker: Ticker,
        date_from: int | None,
        date_to: int | None,
        limit: int,
        offset: int,
    ) -> Sequence[Price]:
        query = select(Price).where(Price.ticker == ticker.value)
        if date_from is not None:
            query = query.where(Price.timestamp >= date_from)
        if date_to is not None:
            query = query.where(Price.timestamp <= date_to)
        query = query.order_by(Price.timestamp, Price.id).limit(limit).offset(offset)
        return self._session.scalars(query).all()
