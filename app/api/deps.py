from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.repository import PriceRepository


def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


def get_price_repository(session: Annotated[Session, Depends(get_session)]) -> PriceRepository:
    return PriceRepository(session)
