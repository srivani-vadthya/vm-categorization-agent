from fastapi import APIRouter
from typing import Dict

from agents.categorization_agent import (
    categorize
)

router = APIRouter()


@router.post(
    "/categorize"
)
def categorize_event(
        payload: Dict):

    return categorize(
        payload
    )