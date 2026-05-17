from db.db_manager import engine, Base

from models.user import User
from models.session import Session
from models.report import Report
from models.snapshot import Snapshot
from core.logger import get_logger

logger = get_logger("app.db.init")

def init_models() -> None:
    logger.info("event=db.init.start")
    Base.metadata.create_all(engine)
   
    logger.info("event=db.init.done")

