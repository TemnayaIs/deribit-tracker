from fastapi import FastAPI
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes import router
from app.config import Settings
from app.database import make_engine, make_session_factory


def create_app(
    settings: Settings | None = None,
    session_factory: sessionmaker[Session] | None = None,
) -> FastAPI:
    settings = settings or Settings()
    if session_factory is None:
        session_factory = make_session_factory(make_engine(settings.database_url))

    app = FastAPI(title="Deribit price tracker", version="1.0.0")
    app.state.session_factory = session_factory
    app.include_router(router)

    @app.get("/health", tags=["service"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
