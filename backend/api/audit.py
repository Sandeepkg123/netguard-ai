import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from core.pdf_generator import PDFReportGenerator

from core.compliance_engine import run_compliance_check
from core.remediation_engine import RemediationEngine
from db.database import SessionLocal
from db.models import (
    Audit,
    ConfigFile,
    Framework,
    FrameworkRule,
    SecurityBaselineModel,
)


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class AuditRequest(BaseModel):
    file_id: int
    framework_id: int


@router.post("/audit")
def run_audit(
    request: AuditRequest,
    db: Session = Depends(get_db),
):

    config_file = (
        db.query(ConfigFile)
        .filter(ConfigFile.id == request.file_id)
        .first()
    )

    if not config_file:
        raise HTTPException(
            status_code=404,
            detail="Configuration file not found",
        )

    framework = (
        db.query(Framework)
        .filter(Framework.id == request.framework_id)
        .first()
    )

    if not framework:
        raise HTTPException(
            status_code=404,
            detail="Framework not found",
        )

    sbm_record = (
        db.query(SecurityBaselineModel)
        .filter(
            SecurityBaselineModel.config_file_id
            == request.file_id
        )
        .first()
    )

    if not sbm_record:
        raise HTTPException(
            status_code=404,
            detail="SBM not found for configuration",
        )

    rules = (
        db.query(FrameworkRule)
        .filter(
            FrameworkRule.framework_id
            == request.framework_id
        )
        .all()
    )

    if not rules:
        raise HTTPException(
            status_code=400,
            detail="Selected framework has no rules",
        )

    security_controls = json.loads(
        sbm_record.sbm_json
    )

    sbm = {
        "vendor": sbm_record.vendor,
        "os": sbm_record.os,
        "hostname": sbm_record.hostname,
        "security_controls": security_controls,
    }

    findings = run_compliance_check(
        sbm,
        rules,
    )

    remediation_engine = RemediationEngine()

    for finding in findings:

        if finding["status"] != "FAIL":
            continue

        remediation = remediation_engine.generate(
            finding=finding,
            vendor=sbm_record.vendor,
            os_version=sbm_record.os,
            db=db,
        )

        finding["remediation"] = (
            remediation.model_dump()
        )

    total_controls = len(findings)

    passed = sum(
        1
        for finding in findings
        if finding["status"] == "PASS"
    )

    failed = total_controls - passed

    score = (
        (passed / total_controls) * 100
        if total_controls > 0
        else 0
    )

    audit = Audit(
        config_file_id=request.file_id,
        framework_id=request.framework_id,
        total_controls=total_controls,
        passed=passed,
        failed=failed,
        score=score,
        findings_json=json.dumps(findings),
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return {
        "audit_id": audit.id,
        "file_id": request.file_id,
        "filename": config_file.filename,
        "framework": {
            "id": framework.id,
            "name": framework.name,
            "version": framework.version,
        },
        "vendor": sbm_record.vendor,
        "os": sbm_record.os,
        "hostname": sbm_record.hostname,
        "total_controls": total_controls,
        "passed": passed,
        "failed": failed,
        "score": round(score, 2),
        "findings": findings,
    }


@router.get("/audit/{audit_id}")
def get_audit(
    audit_id: int,
    db: Session = Depends(get_db),
):

    audit = (
        db.query(Audit)
        .filter(Audit.id == audit_id)
        .first()
    )

    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit not found",
        )

    config_file = (
        db.query(ConfigFile)
        .filter(
            ConfigFile.id == audit.config_file_id
        )
        .first()
    )

    framework = (
        db.query(Framework)
        .filter(
            Framework.id == audit.framework_id
        )
        .first()
    )

    return {
        "audit_id": audit.id,
        "file_id": audit.config_file_id,
        "filename": config_file.filename
        if config_file
        else None,
        "framework": {
            "id": framework.id,
            "name": framework.name,
            "version": framework.version,
        }
        if framework
        else None,
        "total_controls": audit.total_controls,
        "passed": audit.passed,
        "failed": audit.failed,
        "score": audit.score,
        "findings": json.loads(
            audit.findings_json
        ),
        "created_at": audit.created_at,
    }

@router.get("/audit/{audit_id}/pdf")
def get_audit_pdf(
    audit_id: int,
    db: Session = Depends(get_db),
):
    audit = (
        db.query(Audit)
        .filter(Audit.id == audit_id)
        .first()
    )

    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit not found",
        )

    config_file = (
        db.query(ConfigFile)
        .filter(
            ConfigFile.id == audit.config_file_id
        )
        .first()
    )

    framework = (
        db.query(Framework)
        .filter(
            Framework.id == audit.framework_id
        )
        .first()
    )

    if not config_file:
        raise HTTPException(
            status_code=404,
            detail="Configuration file not found",
        )

    if not framework:
        raise HTTPException(
            status_code=404,
            detail="Framework not found",
        )

    audit_data = {
        "audit_id": audit.id,
        "filename": config_file.filename,
        "vendor": None,
        "os": None,
        "hostname": None,
        "framework": {
            "id": framework.id,
            "name": framework.name,
            "version": framework.version,
        },
        "total_controls": audit.total_controls,
        "passed": audit.passed,
        "failed": audit.failed,
        "score": audit.score,
        "findings": json.loads(
            audit.findings_json
        ),
        "created_at": audit.created_at,
    }

    sbm_record = (
        db.query(SecurityBaselineModel)
        .filter(
            SecurityBaselineModel.config_file_id
            == audit.config_file_id
        )
        .first()
    )

    if sbm_record:
        audit_data["vendor"] = sbm_record.vendor
        audit_data["os"] = sbm_record.os
        audit_data["hostname"] = sbm_record.hostname

    generator = PDFReportGenerator()

    filename = f"audit_{audit.id}.pdf"

    pdf_path = generator.generate(
        audit=audit_data,
        filename=filename,
    )

    audit.pdf_path = pdf_path
    db.commit()

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
    )