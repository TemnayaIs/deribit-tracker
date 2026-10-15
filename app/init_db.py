"""Create the tables. Run once before the API and the worker start."""

from app import models
from app.config import Settings
from app.database import Base, make_engine


def main() -> None:
    engine = make_engine(Settings().database_url)
    Base.metadata.create_all(engine)
    engine.dispose()


if __name__ == "__main__":
    main()
