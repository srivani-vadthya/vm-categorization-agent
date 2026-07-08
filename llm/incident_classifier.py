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


def classify_incident(payload):

    logger.info(
        "AI Classification Started"
    )

    prompt = load_prompt(
        "incident_classifier.txt"
    )

    prompt = prompt.replace(
        "{title}",
        str(payload.get("title", ""))
    )

    prompt = prompt.replace(
        "{description}",
        str(payload.get("description", ""))
    )

    response = groq_client.chat(
        prompt
    )

    result = parse_response(
        response
    )

    logger.info(result)

    return result