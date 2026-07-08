from typing import Dict

from fastapi import APIRouter

from agents.categorization_agent import (
    categorize
)

from utils.logger_config import (
    get_logger
)

logger = get_logger(__name__)

router = APIRouter()


@router.post("/categorize")
def categorize_event(payload: Dict):

    logger.info(
        "Received normalized event."
    )

    result = categorize(
        payload
    )

    logger.info(
        "Returning categorization."
    )

    return result