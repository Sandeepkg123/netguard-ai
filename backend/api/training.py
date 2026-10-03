import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import (
    ConfigFile,
    SecurityBaselineModel,
    TrainingLabel,
)
from core.ai_parser import AIParser
from core.gemini_client import GeminiClient


router = APIRouter(
    prefix="/training",
    tags=["training"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class TrainingLabelRequest(BaseModel):
    config_file_id: int

    raw_line: str = Field(
        min_length=1,
    )

    sbm_field_path: str = Field(
        min_length=1,
    )

    mapped_value: str = Field(
        min_length=1,
    )


@router.get("/pending")
def get_pending_training(
    db: Session = Depends(get_db),
):
    models = (
        db.query(SecurityBaselineModel)
        .all()
    )

    result = []

    for sbm_model in models:

        unknown_blocks = json.loads(
            sbm_model.unknown_blocks_json
        )

        config = (
            db.query(ConfigFile)
            .filter(
                ConfigFile.id
                == sbm_model.config_file_id
            )
            .first()
        )

        if not config:
            continue

        for block in unknown_blocks:

            if block.get("confidence", 1.0) >= 0.7:
                continue

            result.append(
                {
                    "config_file_id": config.id,
                    "filename": config.filename,
                    "vendor": sbm_model.vendor,
                    "os": sbm_model.os,
                    "raw_line": block.get(
                        "raw_line",
                        "",
                    ),
                    "reason": block.get(
                        "reason",
                        "Unknown configuration",
                    ),
                    "confidence": block.get(
                        "confidence",
                        0.0,
                    ),
                }
            )

    return {
        "count": len(result),
        "items": result,
    }


@router.post("/label")
def create_training_label(
    payload: TrainingLabelRequest,
    db: Session = Depends(get_db),
):
    config = (
        db.query(ConfigFile)
        .filter(
            ConfigFile.id
            == payload.config_file_id
        )
        .first()
    )

    if not config:
        raise HTTPException(
            status_code=404,
            detail="Configuration file not found",
        )

    sbm_model = (
        db.query(SecurityBaselineModel)
        .filter(
            SecurityBaselineModel.config_file_id
            == payload.config_file_id
        )
        .first()
    )

    if not sbm_model:
        raise HTTPException(
            status_code=404,
            detail="SBM not found",
        )

    training_label = TrainingLabel(
        config_file_id=payload.config_file_id,
        vendor=sbm_model.vendor,
        os=sbm_model.os,
        raw_line=payload.raw_line,
        sbm_field_path=payload.sbm_field_path,
        mapped_value=payload.mapped_value,
        status="approved",
    )

    db.add(training_label)
    db.commit()
    db.refresh(training_label)

    return {
        "id": training_label.id,
        "message": "Training mapping saved successfully",
        "mapping": {
            "raw_line": training_label.raw_line,
            "sbm_field_path": training_label.sbm_field_path,
            "mapped_value": training_label.mapped_value,
        },
    }


@router.post("/reanalyze/{config_file_id}")
def reanalyze_configuration(
    config_file_id: int,
    db: Session = Depends(get_db),
):
    config = (
        db.query(ConfigFile)
        .filter(
            ConfigFile.id == config_file_id
        )
        .first()
    )

    if not config:
        raise HTTPException(
            status_code=404,
            detail="Configuration file not found",
        )

    sbm_model = (
        db.query(SecurityBaselineModel)
        .filter(
            SecurityBaselineModel.config_file_id
            == config_file_id
        )
        .first()
    )

    if not sbm_model:
        raise HTTPException(
            status_code=404,
            detail="SBM not found",
        )

    labels = (
        db.query(TrainingLabel)
        .filter(
            TrainingLabel.status == "approved"
        )
        .all()
    )

    training_examples = []

    for label in labels:
        training_examples.append(
            {
                "raw_line": label.raw_line,
                "sbm_field_path": label.sbm_field_path,
                "mapped_value": label.mapped_value,
                "vendor": label.vendor,
                "os": label.os,
            }
        )

    gemini = GeminiClient()
    parser = AIParser(gemini)

    sbm = parser.parse(
        config.raw_config,
        training_examples=training_examples,
    )

    sbm_model.vendor = sbm.vendor
    sbm_model.os = sbm.os
    sbm_model.hostname = sbm.hostname
    sbm_model.sbm_json = json.dumps(
        sbm.model_dump()
    )
    sbm_model.confidence = sbm.confidence
    sbm_model.unknown_blocks_json = json.dumps(
        [
            block.model_dump()
            for block in sbm.unknown_blocks
        ]
    )

    db.commit()
    db.refresh(sbm_model)

    return {
        "config_file_id": config.id,
        "filename": config.filename,
        "message": "Configuration re-analyzed successfully",
        "sbm": sbm.model_dump(),
    }


@router.get("/labels")
def get_training_labels(
    db: Session = Depends(get_db),
):
    labels = (
        db.query(TrainingLabel)
        .order_by(
            TrainingLabel.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": label.id,
            "config_file_id": label.config_file_id,
            "vendor": label.vendor,
            "os": label.os,
            "raw_line": label.raw_line,
            "sbm_field_path": label.sbm_field_path,
            "mapped_value": label.mapped_value,
            "status": label.status,
        }
        for label in labels
    ]