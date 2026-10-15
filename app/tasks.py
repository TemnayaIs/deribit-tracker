import asyncio
import logging

from celery import Task
from sqlalchemy.orm import Session, sessionmaker

from app.celery_app import celery_app
from app.config import Settings
from app.database import make_engine, make_session_factory
from app.repository import PriceRepository
from app.services import fetch_current_prices

logger = logging.getLogger(__name__)


class CollectPricesTask(Task):
    """Task base class that owns the per-process settings and DB connection pool."""

    abstract = True
    _settings: Settings | None = None
    _session_factory: sessionmaker[Session] | None = None

    @property
    def settings(self) -> Settings:
        if self._settings is None:
            self._settings = Settings()
        return self._settings

    @property
    def session_factory(self) -> sessionmaker[Session]:
        if self._session_factory is None:
            self._session_factory = make_session_factory(make_engine(self.settings.database_url))
        return self._session_factory


@celery_app.task(base=CollectPricesTask, bind=True, name="prices.collect")
def collect_prices_task(self: CollectPricesTask) -> int:
    prices = asyncio.run(fetch_current_prices(self.settings))
    with self.session_factory() as session, session.begin():
        PriceRepository(session).add_many(prices)
    logger.info("stored %d prices", len(prices))
    return len(prices)
