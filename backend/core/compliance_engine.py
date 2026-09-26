from typing import Any


SUPPORTED_OPERATORS = {
    "eq",
    "neq",
    "gte",
    "lte",
    "contains",
    "not_contains",
    "is_null",
    "not_null",
}


def get_nested(data: dict, field_path: str) -> Any:
    """
    Resolve a dot-notation field path.

    Example:
        security_controls.ssh.version

    Returns:
        The value if found.
        None if the path does not exist.
    """

    current = data

    for part in field_path.split("."):
        if not isinstance(current, dict):
            return None

        if part not in current:
            return None

        current = current[part]

    return current


def normalize_value(value: Any) -> Any:
    """
    Convert framework expected values from strings
    into comparable Python values when possible.
    """

    if not isinstance(value, str):
        return value

    value = value.strip()

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    if value.lower() == "null":
        return None

    try:
        if "." in value:
            return float(value)

        return int(value)

    except ValueError:
        return value


def evaluate(
    actual_value: Any,
    expected_value: Any,
    operator: str,
) -> bool:

    if operator not in SUPPORTED_OPERATORS:
        raise ValueError(
            f"Unsupported compliance operator: {operator}"
        )

    expected = normalize_value(expected_value)

    if operator == "eq":
        return normalize_value(actual_value) == expected

    if operator == "neq":
        return normalize_value(actual_value) != expected

    if operator == "gte":
        try:
            return actual_value >= expected
        except (TypeError, ValueError):
            return False

    if operator == "lte":
        try:
            return actual_value <= expected
        except (TypeError, ValueError):
            return False

    if operator == "contains":
        if actual_value is None:
            return False

        if isinstance(actual_value, (list, tuple, set, str)):
            return expected in actual_value

        return False

    if operator == "not_contains":
        if actual_value is None:
            return True

        if isinstance(actual_value, (list, tuple, set, str)):
            return expected not in actual_value

        return False

    if operator == "is_null":
        return actual_value is None

    if operator == "not_null":
        return actual_value is not None

    return False


def run_compliance_check(
    sbm: dict,
    rules: list,
) -> list[dict]:

    findings = []

    for rule in rules:

        actual_value = get_nested(
            sbm,
            rule.sbm_field_path,
        )

        passed = evaluate(
            actual_value,
            rule.expected_value,
            rule.operator,
        )

        findings.append(
            {
                "control_id": rule.control_id,
                "title": rule.title,
                "status": "PASS" if passed else "FAIL",
                "severity": rule.severity,
                "actual_value": actual_value,
                "expected_value": rule.expected_value,
                "sbm_field": rule.sbm_field_path,
                "category": rule.category,
                "description": rule.description,
                "remediation_hint": rule.remediation_hint,
            }
        )

    return findings