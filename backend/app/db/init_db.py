from db.db_manager import engine, Base

from db.models.user import User
from db.models.session import Session
from db.models.report import Report
from db.models import analysis
from core.logger import get_logger

logger = get_logger("app.db.init")

def init_models() -> None:
    logger.info("event=db.init.start")
    Base.metadata.create_all(engine)
    logger.info("event=db.init.done")

