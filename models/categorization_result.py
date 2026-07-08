from typing import List, Optional

from pydantic import BaseModel


class CategorizationResult(BaseModel):

    ticket_id: str

    classification: str

    support_level: str

    technology: str

    team: str

    priority: str

    business_impact: str

    business_criticality: str

    risk: str

    risk_score: int

    duplicate: bool

    duplicate_of: Optional[str]

    confidence: float

    requires_human: bool

    selected_agent: str

    backup_agent: Optional[str]

    available: bool

    reject: bool

    route_to: str

    reason: str

    reasoning: List[str]