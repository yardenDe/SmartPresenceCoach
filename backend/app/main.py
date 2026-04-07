from fastapi import FastAPI
import uvicorn

from app.api.router import api_router
from app.core.execptions import AppError, app_exceptions_handler
from app.db.init_db import init_models
from app.core.config import get_settings


app = FastAPI()
app.include_router(api_router)
app.add_exception_handler(AppError, app_exceptions_handler)

init_models()

settings = get_settings()


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
