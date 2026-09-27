from core.remediation_engine import RemediationEngine


class FakeDBQuery:
    def filter(self, *args):
        return self

    def first(self):
        return None


class FakeDB:
    def query(self, model):
        return FakeDBQuery()

    def add(self, record):
        print("CACHE ADD:")
        print(record.vendor)
        print(record.control_id)

    def commit(self):
        print("CACHE COMMIT")


class FakeGemini:
    def generate(self, prompt):
        print("\nGEMINI CALLED\n")

        return """
        {
            "risk_explanation": "Weak SSH configuration can allow insecure remote access.",
            "fix_commands": [
                "configure terminal",
                "ip ssh version 2"
            ],
            "verification_command": "show ip ssh",
            "caveat": null
        }
        """


engine = RemediationEngine()

engine.gemini = FakeGemini()

finding = {
    "control_id": "TEST-SSH-01",
    "title": "SSH version must be 2",
    "sbm_field": "security_controls.ssh.version",
    "actual_value": "1",
    "expected_value": "2",
    "remediation_hint": "Use SSH version 2",
}

db = FakeDB()

result = engine.generate(
    finding=finding,
    vendor="Cisco",
    os_version="IOS",
    db=db,
)

print("\nRESULT:")
print(result.model_dump())