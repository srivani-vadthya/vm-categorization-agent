from pydantic import BaseModel
from typing import Optional


class CategorizationResult(BaseModel):

    ticket_id: str

    classification: str

    support_level: str

    team: Optional[str] = None

    technology: Optional[str] = None

    route_to: Optional[str] = None

    confidence: float

    reject: bool

    reason: str