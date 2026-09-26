from fastapi import FastAPI

from api.upload import router as upload_router
from api.sbm import router as sbm_router
from api.frameworks import router as framework_router
from db import models
from db.database import SessionLocal, engine, Base
from db.seed_frameworks import seed_frameworks


app = FastAPI()

Base.metadata.create_all(bind=engine)


db = SessionLocal()

try:
    seed_frameworks(db)
finally:
    db.close()


app.include_router(upload_router, prefix="/api")
app.include_router(framework_router, prefix="/api")
app.include_router(
    sbm_router,
    prefix="/api",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}