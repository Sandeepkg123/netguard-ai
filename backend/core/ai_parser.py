import json

from core.gemini_client import GeminiClient
from schemas.sbm import SBM


class AIParser:
    def __init__(self):
        self.gemini = GeminiClient()

    def parse(self, raw_config: str) -> SBM:

        prompt = f"""
You are a network security configuration parser.

Convert the following network device configuration
into the Security Baseline Model (SBM).

IMPORTANT RULES:

1. Extract only values explicitly present in the configuration.
2. Never invent or assume a value.
3. If a value is absent, use null where appropriate.
4. Identify vendor and operating system only when supported
   by evidence in the configuration.
5. If vendor or OS cannot be identified, use "unknown".
6. Preserve exact configuration values.
7. Put security-related normalized information inside
   security_controls.
8. Every unrecognized or uncertain configuration line must
   be added to unknown_blocks.
9. Each unknown block must contain:
   - raw_line
   - reason
   - confidence between 0 and 1.
10. Overall confidence must be between 0 and 1.
11. Return ONLY valid JSON.
12. Do not wrap the JSON in markdown code fences.

Expected JSON structure:

{{
  "vendor": "string",
  "os": "string",
  "hostname": "string or null",
  "security_controls": {{}},
  "confidence": 0.0,
  "unknown_blocks": []
}}

Configuration:

---BEGIN CONFIG---
{raw_config}
---END CONFIG---
"""

        response = self.gemini.generate(prompt)

        data = self._extract_json(response)

        return SBM.model_validate(data)

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
                "Gemini returned invalid JSON"
            ) from exc