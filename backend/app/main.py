from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from core.exceptions import AppError, app_exceptions_handler
from db.init_db import init_models
from core.config import get_settings
from core.logger import get_logger, setup_logging


setup_logging()
logger = get_logger("app.main")
app = FastAPI()
app.include_router(api_router)
app.add_exception_handler(AppError, app_exceptions_handler)


origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,          
    allow_methods=["*"],              
    allow_headers=["*"],
)

init_models()

settings = get_settings()
logger.info("Application started on %s:%s", settings.APP_HOST, settings.APP_PORT)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
