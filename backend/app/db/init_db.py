from app.db.db_manager import engine, Base

from app.models.user import User
from app.models.session import Session
from app.models.report import Report


def init_models():
    Base.metadata.create_all(engine)
