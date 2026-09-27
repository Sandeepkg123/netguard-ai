import json

from core.gemini_client import GeminiClient
from db.models import RemediationCache
from schemas.remediation import Remediation


class RemediationEngine:
    def __init__(self):
        self.gemini = GeminiClient()

    def generate(
        self,
        finding: dict,
        vendor: str,
        os_version: str,
        db,
    ) -> Remediation:

        control_id = finding["control_id"]

        # -----------------------------------------
        # 1. Check cache
        # -----------------------------------------

        cached = (
            db.query(RemediationCache)
            .filter(
                RemediationCache.vendor == vendor,
                RemediationCache.control_id == control_id,
            )
            .first()
        )

        if cached:
            return Remediation.model_validate(
                json.loads(cached.remediation_json)
            )

        # -----------------------------------------
        # 2. Build Gemini prompt
        # -----------------------------------------

        remediation_hint = finding.get(
            "remediation_hint"
        )

        prompt = f"""
You are a network security hardening expert.

Generate remediation for a failed network security
compliance control.

Device information:
- Vendor: {vendor}
- OS/Version: {os_version}

Failed compliance control:
- Control ID: {control_id}
- Title: {finding["title"]}
- Issue: Field '{finding["sbm_field"]}' has value
  '{finding["actual_value"]}', but expected
  '{finding["expected_value"]}'
- Framework remediation hint: {remediation_hint}

Requirements:

1. Explain the security risk in exactly one sentence.

2. Provide the EXACT CLI commands required to fix
   this issue for the specified vendor and OS.

3. Provide one verification command that confirms
   the fix was applied.

4. Do not invent configuration values.

5. If the vendor is unknown, provide the nearest
   equivalent command and clearly explain in the
   caveat that the command may need adaptation.

6. Return ONLY valid JSON.

Return exactly this structure:

{{
    "risk_explanation": "one sentence",
    "fix_commands": [
        "command 1",
        "command 2"
    ],
    "verification_command": "verification command",
    "caveat": null
}}
"""

        # -----------------------------------------
        # 3. Call Gemini
        # -----------------------------------------

        response = self.gemini.generate(prompt)

        data = self._extract_json(response)

        remediation = Remediation.model_validate(data)

        # -----------------------------------------
        # 4. Save to cache
        # -----------------------------------------

        cache_record = RemediationCache(
            vendor=vendor,
            control_id=control_id,
            remediation_json=json.dumps(
                remediation.model_dump()
            ),
        )

        db.add(cache_record)
        db.commit()

        return remediation

    @staticmethod
    def _extract_json(response: str) -> dict:

        response = response.strip()

        if response.startswith("```"):
            lines = response.splitlines()

            if lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response = "\n".join(lines).strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini returned invalid remediation JSON"
            ) from exc