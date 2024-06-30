from flask import current_app
from functools import cache
from sqlalchemy import create_engine

from db.client import DopBuddyDbClient


@cache
def get_db_client_instance() -> DopBuddyDbClient:
    engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"], echo=False, pool_pre_ping=True)
    return DopBuddyDbClient(engine=engine)
