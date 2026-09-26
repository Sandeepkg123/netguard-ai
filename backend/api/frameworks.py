from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.models import Framework, FrameworkRule


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/frameworks")
def get_frameworks(
    db: Session = Depends(get_db),
):
    frameworks = db.query(Framework).all()

    result = []

    for framework in frameworks:
        rule_count = (
            db.query(FrameworkRule)
            .filter(
                FrameworkRule.framework_id == framework.id
            )
            .count()
        )

        result.append(
            {
                "id": framework.id,
                "name": framework.name,
                "version": framework.version,
                "source": framework.source,
                "rule_count": rule_count,
            }
        )

    return result