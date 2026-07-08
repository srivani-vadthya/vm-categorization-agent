import json

from pathlib import Path

from utils.logger_config import get_logger

logger = get_logger(__name__)

CONFIG = Path("config/routing_rules.json")

with open(CONFIG) as f:

    ROUTES = json.load(f)


def select_agent(

        support_level,

        technology

):

    if support_level == "REJECT":

        return {

            "selected_agent":

                ROUTES[
                    "REJECT"
                ]["default"],

            "available": True,

            "backup_agent": None
        }

    if support_level == "L1":

        return {

            "selected_agent":

                ROUTES[
                    "L1"
                ]["default"],

            "available": True,

            "backup_agent": None
        }

    selected = (

        ROUTES

        .get(

            support_level,

            {}

        )

        .get(

            technology,

            ROUTES[
                support_level
            ]["General"]

        )

    )

    logger.info(

        f"Selected Agent : {selected}"

    )

    return {

        "selected_agent":

            selected,

        "available":

            True,

        "backup_agent":

            "generic_support_agent"
    }