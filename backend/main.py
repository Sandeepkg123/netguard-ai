from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.upload import router as upload_router
from api.sbm import router as sbm_router
from api.frameworks import router as framework_router
from db import models
from db.database import SessionLocal, engine, Base
from db.seed_frameworks import seed_frameworks
from api.audit import router as audit_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
app.include_router(
    audit_router,
    prefix="/api",
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}