from fastapi import FastAPI
import uvicorn

from app.api.router import api_router
from app.db.init_db import init_models

app = FastAPI()
app.include_router(api_router)
init_models()



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
