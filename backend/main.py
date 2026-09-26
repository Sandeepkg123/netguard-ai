from fastapi import FastAPI

from db.database import engine

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}