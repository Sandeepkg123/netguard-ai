import json
import re
from typing import Any, Dict, List, Optional

from schemas.sbm import SBM


class AIParser:
    def __init__(self, gemini_client):
        self.gemini = gemini_client

    def build_prompt(
        self,
        raw_config: str,
        training_examples: Optional[List[Dict[str, Any]]] = None,
    ) -> str:

        examples_text = ""

        if training_examples:
            examples_text = """
APPROVED TRAINING EXAMPLES

The following examples were manually approved by an administrator.

Use them as semantic mapping examples.

IMPORTANT:
- The example value is NOT automatically the value for future configurations.
- Determine the value from the actual configuration being analyzed.
- Learn the relationship between the configuration syntax and the SBM field.
- Never invent a value that is not supported by the configuration.

"""

            for index, example in enumerate(
                training_examples,
                start=1,
            ):
                examples_text += f"""
Example {index}:
Raw configuration:
{example["raw_line"]}

SBM field:
{example["sbm_field_path"]}

Example value:
{example["mapped_value"]}

"""

        prompt = f"""
You are a network security configuration parser.

Convert the following network configuration into the
Security Baseline Model (SBM).

RULES:

1. Only extract values explicitly supported by the configuration.
2. NEVER invent configuration values.
3. If a field is absent, use null.
4. Identify vendor and OS only when there is evidence.
5. Otherwise use "unknown".
6. Preserve exact configuration values where appropriate.
7. Put security-related information under security_controls.
8. If a configuration line cannot be understood confidently,
   put it into unknown_blocks.
9. unknown_blocks must contain:
   - raw_line
   - reason
   - confidence from 0.0 to 1.0
10. Overall confidence must be between 0.0 and 1.0.
11. Return ONLY valid JSON.
12. Do NOT return markdown.
13. Do NOT add explanations outside the JSON.

{examples_text}

OUTPUT FORMAT:

{{
  "vendor": "unknown",
  "os": "unknown",
  "hostname": null,
  "security_controls": {{}},
  "confidence": 0.0,
  "unknown_blocks": []
}}

CONFIGURATION:

{raw_config}
"""

        return prompt

    def parse(
        self,
        raw_config: str,
        training_examples: Optional[List[Dict[str, Any]]] = None,
    ) -> SBM:

        prompt = self.build_prompt(
            raw_config,
            training_examples,
        )

        response = self.gemini.generate(prompt)

        response = response.strip()

        # Gemini sometimes returns markdown fences.
        response = re.sub(
            r"^```json\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        response = re.sub(
            r"^```\s*",
            "",
            response,
        )

        response = re.sub(
            r"\s*```$",
            "",
            response,
        )

        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Gemini returned invalid JSON"
            ) from exc

        return SBM.model_validate(data)