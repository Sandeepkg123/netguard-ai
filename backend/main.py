from fastapi import FastAPI

from db.database import engine, Base
from db import models
from api.upload import router as upload_router


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(upload_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}