import hashlib

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import ConfigFile


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
async def upload_config(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()

    max_size = 10 * 1024 * 1024

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB limit",
        )

    raw_config = content.decode("utf-8")

    file_hash = hashlib.sha256(content).hexdigest()

    existing_file = (
        db.query(ConfigFile)
        .filter(ConfigFile.file_hash == file_hash)
        .first()
    )

    if existing_file:
        raise HTTPException(
            status_code=409,
            detail="Duplicate configuration file",
        )

    config_file = ConfigFile(
        filename=file.filename,
        file_hash=file_hash,
        raw_config=raw_config,
    )

    db.add(config_file)
    db.commit()
    db.refresh(config_file)

    return {
        "id": config_file.id,
        "filename": config_file.filename,
        "file_hash": config_file.file_hash,
        "message": "Configuration uploaded successfully",
    }