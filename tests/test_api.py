import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_list_prices_returns_only_requested_ticker(client):
    response = client.get("/prices", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    body = response.json()
    assert [row["timestamp"] for row in body] == [1_700_000_000, 1_700_000_060, 1_700_000_120]
    assert {row["ticker"] for row in body} == {"btc_usd"}


def test_list_prices_supports_pagination(client):
    response = client.get("/prices", params={"ticker": "btc_usd", "limit": 1, "offset": 1})

    assert [row["timestamp"] for row in response.json()] == [1_700_000_060]


def test_ticker_is_case_insensitive(client):
    response = client.get("/prices", params={"ticker": "ETH_USD"})

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_latest_price(client):
    response = client.get("/prices/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert response.json() == {"ticker": "btc_usd", "price": 60200.3, "timestamp": 1_700_000_120}


def test_latest_price_is_404_when_nothing_stored(session_factory):
    client = TestClient(create_app(Settings(), session_factory))

    response = client.get("/prices/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 404


def test_by_date_filters_inclusively(client):
    response = client.get(
        "/prices/by-date",
        params={"ticker": "btc_usd", "date_from": 1_700_000_060, "date_to": 1_700_000_120},
    )

    assert [row["timestamp"] for row in response.json()] == [1_700_000_060, 1_700_000_120]


def test_by_date_accepts_open_range(client):
    response = client.get("/prices/by-date", params={"ticker": "btc_usd", "date_from": 1_700_000_100})

    assert [row["timestamp"] for row in response.json()] == [1_700_000_120]


def test_by_date_rejects_reversed_range(client):
    response = client.get(
        "/prices/by-date",
        params={"ticker": "btc_usd", "date_from": 10, "date_to": 5},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("path", ["/prices", "/prices/latest", "/prices/by-date"])
def test_ticker_is_required(client, path):
    assert client.get(path).status_code == 422


@pytest.mark.parametrize("path", ["/prices", "/prices/latest", "/prices/by-date"])
def test_unknown_ticker_is_rejected(client, path):
    assert client.get(path, params={"ticker": "doge_usd"}).status_code == 422


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
