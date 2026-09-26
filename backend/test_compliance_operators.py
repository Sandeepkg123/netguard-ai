import json

from core.compliance_engine import run_compliance_check
from db.database import SessionLocal
from db.models import (
    ConfigFile,
    Framework,
    FrameworkRule,
    SecurityBaselineModel,
)


db = SessionLocal()

try:
    # --------------------------------------------------
    # 1. Get our existing Cisco configuration
    # --------------------------------------------------

    config_file = (
        db.query(ConfigFile)
        .filter(ConfigFile.id == 2)
        .first()
    )

    if not config_file:
        raise RuntimeError(
            "Config file ID 2 not found. "
            "Use the ID of your Cisco configuration."
        )

    sbm_record = (
        db.query(SecurityBaselineModel)
        .filter(
            SecurityBaselineModel.config_file_id
            == config_file.id
        )
        .first()
    )

    if not sbm_record:
        raise RuntimeError(
            "SBM not found for the Cisco configuration."
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

    print("\nCisco SBM loaded successfully.")
    print(
        "SSH version:",
        security_controls["ssh"]["version"],
    )
    print(
        "SSH key modulus:",
        security_controls["ssh"]["key_modulus"],
    )
    print(
        "NTP servers:",
        security_controls["ntp"]["servers"],
    )

    # --------------------------------------------------
    # 2. Create temporary framework
    # --------------------------------------------------

    framework = Framework(
        name="TEMP_OPERATOR_TEST",
        version="1.0",
        source="Temporary automated test",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    # --------------------------------------------------
    # 3. Create rules for all operators
    # --------------------------------------------------

    rules = [
        # EQ - PASS
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-EQ-PASS",
            title="EQ should pass",
            sbm_field_path="security_controls.ssh.version",
            expected_value="2",
            operator="eq",
            severity="LOW",
        ),

        # EQ - FAIL
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-EQ-FAIL",
            title="EQ should fail",
            sbm_field_path="security_controls.ssh.version",
            expected_value="1",
            operator="eq",
            severity="LOW",
        ),

        # NEQ - PASS
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-NEQ",
            title="NEQ should pass",
            sbm_field_path="security_controls.ssh.version",
            expected_value="1",
            operator="neq",
            severity="LOW",
        ),

        # GTE - PASS
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-GTE",
            title="GTE should pass",
            sbm_field_path="security_controls.ssh.key_modulus",
            expected_value="2048",
            operator="gte",
            severity="LOW",
        ),

        # LTE - PASS
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-LTE",
            title="LTE should pass",
            sbm_field_path="security_controls.ssh.key_modulus",
            expected_value="4096",
            operator="lte",
            severity="LOW",
        ),

        # CONTAINS - PASS
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-CONTAINS",
            title="CONTAINS should pass",
            sbm_field_path="security_controls.ntp.servers",
            expected_value="216.239.35.0",
            operator="contains",
            severity="LOW",
        ),

        # NOT_CONTAINS - PASS
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-NOT-CONTAINS",
            title="NOT_CONTAINS should pass",
            sbm_field_path="security_controls.ntp.servers",
            expected_value="1.1.1.1",
            operator="not_contains",
            severity="LOW",
        ),

        # IS_NULL - PASS
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-IS-NULL",
            title="IS_NULL should pass",
            sbm_field_path="security_controls.some_missing_field",
            expected_value=None,
            operator="is_null",
            severity="LOW",
        ),

        # NOT_NULL - PASS
        FrameworkRule(
            framework_id=framework.id,
            control_id="TEST-NOT-NULL",
            title="NOT_NULL should pass",
            sbm_field_path="security_controls.ssh.version",
            expected_value=None,
            operator="not_null",
            severity="LOW",
        ),
    ]

    db.add_all(rules)
    db.commit()

    # --------------------------------------------------
    # 4. Run compliance engine
    # --------------------------------------------------

    print("\nRunning compliance engine...\n")

    findings = run_compliance_check(
        sbm,
        rules,
    )

    # --------------------------------------------------
    # 5. Print results
    # --------------------------------------------------

    for finding in findings:
        print(
            f"{finding['control_id']:25} "
            f"{finding['status']:4} "
            f"actual={finding['actual_value']} "
            f"expected={finding['expected_value']}"
        )

    # --------------------------------------------------
    # 6. Verify expected results
    # --------------------------------------------------

    expected_results = {
        "TEST-EQ-PASS": "PASS",
        "TEST-EQ-FAIL": "FAIL",
        "TEST-NEQ": "PASS",
        "TEST-GTE": "PASS",
        "TEST-LTE": "PASS",
        "TEST-CONTAINS": "PASS",
        "TEST-NOT-CONTAINS": "PASS",
        "TEST-IS-NULL": "PASS",
        "TEST-NOT-NULL": "PASS",
    }

    print("\nVerification:\n")

    all_passed = True

    for finding in findings:
        control_id = finding["control_id"]
        actual_status = finding["status"]
        expected_status = expected_results[control_id]

        if actual_status == expected_status:
            print(
                f"✓ {control_id}: "
                f"expected {expected_status}, "
                f"got {actual_status}"
            )
        else:
            print(
                f"✗ {control_id}: "
                f"expected {expected_status}, "
                f"got {actual_status}"
            )
            all_passed = False

    if all_passed:
        print(
            "\nSUCCESS: All operator tests passed."
        )
    else:
        print(
            "\nFAILURE: One or more operator tests failed."
        )

finally:
    # --------------------------------------------------
    # 7. Delete temporary test framework
    # --------------------------------------------------

    temp_framework = (
        db.query(Framework)
        .filter(
            Framework.name == "TEMP_OPERATOR_TEST"
        )
        .first()
    )

    if temp_framework:
        db.query(FrameworkRule).filter(
            FrameworkRule.framework_id
            == temp_framework.id
        ).delete()

        db.delete(temp_framework)
        db.commit()

    db.close()