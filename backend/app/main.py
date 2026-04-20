from fastapi import FastAPI
import uvicorn

from api.router import api_router
from core.excptions import AppError, app_exceptions_handler
from db.init_db import init_models
from core.config import get_settings


app = FastAPI()
app.include_router(api_router)
app.add_exception_handler(AppError, app_exceptions_handler)

init_models()

settings = get_settings()


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
