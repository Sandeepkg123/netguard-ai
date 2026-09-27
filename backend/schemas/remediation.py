from typing import List, Optional

from pydantic import BaseModel


class Remediation(BaseModel):
    risk_explanation: str
    fix_commands: List[str]
    verification_command: str
    caveat: Optional[str] = None