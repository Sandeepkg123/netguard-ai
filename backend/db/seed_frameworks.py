import json
from pathlib import Path

from sqlalchemy.orm import Session

from db.models import Framework, FrameworkRule


FRAMEWORKS_DIR = (
    Path(__file__).resolve().parent.parent / "frameworks"
)


def seed_frameworks(db: Session):
    json_files = [
        "cis_benchmark.json",
        "nist_sp800_53.json",
        "disa_stigs.json",
        "iso_27001.json",
    ]

    for filename in json_files:
        file_path = FRAMEWORKS_DIR / filename

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        existing = (
            db.query(Framework)
            .filter(
                Framework.name == data["name"],
                Framework.version == data["version"],
            )
            .first()
        )

        if existing:
            continue

        framework = Framework(
            name=data["name"],
            version=data["version"],
            source=data["source"],
        )

        db.add(framework)
        db.flush()

        for rule_data in data["rules"]:
            rule = FrameworkRule(
                framework_id=framework.id,
                control_id=rule_data["control_id"],
                category=rule_data.get("category"),
                title=rule_data["title"],
                description=rule_data.get("description"),
                sbm_field_path=rule_data["sbm_field_path"],
                expected_value=rule_data.get("expected_value"),
                operator=rule_data.get("operator", "eq"),
                severity=rule_data.get("severity", "HIGH"),
                remediation_hint=rule_data.get(
                    "remediation_hint"
                ),
            )

            db.add(rule)

        db.commit()