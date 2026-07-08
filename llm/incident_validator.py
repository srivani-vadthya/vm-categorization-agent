from llm.prompt_loader import (

    load_prompt

)

from llm.groq_client import (

    groq_client

)

from llm.response_parser import (

    parse_response

)

from utils.logger_config import (

    get_logger

)

logger = get_logger(__name__)


def validate_incident(

        payload

):

    logger.info(

        "AI Incident Validation Started"

    )

    prompt = load_prompt(

        "incident_validator.txt"

    )

    prompt = prompt.replace(

        "{title}",

        str(

            payload.get(

                "title",

                ""

            )

        )

    )

    prompt = prompt.replace(

        "{description}",

        str(

            payload.get(

                "description",

                ""

            )

        )

    )

    logger.info(

        "Calling Groq..."

    )

    response = groq_client.chat(

        prompt

    )

    logger.info(

        "Groq Response Received."

    )

    result = parse_response(

        response

    )

    logger.info(

        result

    )

    return result