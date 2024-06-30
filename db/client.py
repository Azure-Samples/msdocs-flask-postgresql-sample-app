import contextlib
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from db.models.base import Base

log = logging.getLogger(__name__)


class DopBuddyDbClient:
    """
    Exposes methods to deal with SqlAlchemy sessions on the dop-buddy DB.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.session = sessionmaker(bind=self.engine)
        self.scoped_session = scoped_session(sessionmaker(bind=self.engine))
        self.create_all_tables()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Helper method to return a session object that's automatically closed at the end of block
        """
        with contextlib.closing(self.session()) as session:
            yield session

    @contextmanager
    def get_scoped_session(self) -> Generator[Session, None, None]:
        """
        Helper method to get a scoped session with transactional scope around a series of operations
        """
        session = self.scoped_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_all_tables(self) -> None:
        Base.metadata.create_all(self.engine)
