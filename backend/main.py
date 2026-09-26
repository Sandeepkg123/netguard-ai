from fastapi import FastAPI

from db.database import engine, Base
from db import models

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}