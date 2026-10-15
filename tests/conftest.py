from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.database import Base, make_session_factory
from app.main import create_app
from app.models import Price


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield make_session_factory(engine)
    engine.dispose()


@pytest.fixture
def seeded(session_factory):
    rows = [
        Price(ticker="btc_usd", price=Decimal("60000.10"), timestamp=1_700_000_000),
        Price(ticker="btc_usd", price=Decimal("60100.20"), timestamp=1_700_000_060),
        Price(ticker="btc_usd", price=Decimal("60200.30"), timestamp=1_700_000_120),
        Price(ticker="eth_usd", price=Decimal("3000.50"), timestamp=1_700_000_060),
    ]
    with session_factory() as session, session.begin():
        session.add_all(rows)
    return session_factory


@pytest.fixture
def client(seeded):
    return TestClient(create_app(Settings(), seeded))
