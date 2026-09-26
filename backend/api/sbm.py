import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import (
    ConfigFile,
    SecurityBaselineModel,
)

router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/config/{file_id}/sbm")
def get_sbm(
    file_id: int,
    db: Session = Depends(get_db),
):
    config_file = (
        db.query(ConfigFile)
        .filter(ConfigFile.id == file_id)
        .first()
    )

    if not config_file:
        raise HTTPException(
            status_code=404,
            detail="Configuration file not found",
        )

    sbm = (
        db.query(SecurityBaselineModel)
        .filter(
            SecurityBaselineModel.config_file_id == file_id
        )
        .first()
    )

    if not sbm:
        raise HTTPException(
            status_code=404,
            detail="SBM not found",
        )

    return {
        "file_id": file_id,
        "filename": config_file.filename,
        "vendor": sbm.vendor,
        "os": sbm.os,
        "hostname": sbm.hostname,
        "confidence": sbm.confidence,
        "security_controls": json.loads(
            sbm.sbm_json
        ),
        "unknown_blocks": json.loads(
            sbm.unknown_blocks_json
        ),
    }