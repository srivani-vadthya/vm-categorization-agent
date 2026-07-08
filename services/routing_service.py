from services.agent_capability_service import (
    select_agent
)

from utils.logger_config import (
    get_logger
)

logger = get_logger(__name__)


def determine_route(

        support_level,

        technology

):

    logger.info(
        "Determining routing."
    )

    agent = select_agent(

        support_level,

        technology

    )

    logger.info(

        f"Selected Agent : {agent['selected_agent']}"

    )

    return agent