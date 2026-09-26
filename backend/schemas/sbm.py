from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UnknownBlock(BaseModel):
    raw_line: str
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class SBM(BaseModel):
    vendor: str = "unknown"
    os: str = "unknown"
    hostname: Optional[str] = None

    security_controls: Dict[str, Any] = {}

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    unknown_blocks: List[UnknownBlock] = []