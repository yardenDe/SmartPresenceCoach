from db.db_manager import engine, Base

from models.user import User
from models.session import Session
from models.report import Report
from models.snapshot import Snapshot

def init_models() -> None:
    Base.metadata.create_all(engine)
