from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from core.dependencies import close_mp_detector
from core.exceptions import AppError, app_exceptions_handler, unhandled_exceptions_handler
from db.init_db import init_models
from core.config import get_settings
from core.logger import get_logger, setup_logging


setup_logging()
logger = get_logger("app.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("event=app.start host=%s port=%s", settings.APP_HOST, settings.APP_PORT)
    
    init_models()
    yield
    close_mp_detector()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.add_exception_handler(AppError, app_exceptions_handler)
app.add_exception_handler(Exception, unhandled_exceptions_handler)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[settings.FRONTEND_ORIGIN],          
    allow_methods=["*"],              
    allow_headers=["*"],
)



if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=settings.RELOAD)
