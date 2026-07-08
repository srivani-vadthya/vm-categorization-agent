from utils.logger_config import get_logger

logger = get_logger(__name__)


def calculate_confidence(

        validation_confidence,

        support_score,

        technology_found,

        business_impact

):

    confidence = validation_confidence

    # -------------------------
    # Positive Signals
    # -------------------------

    if support_score >= 3:

        confidence += 0.20

    elif support_score == 2:

        confidence += 0.10

    elif support_score == 1:

        confidence += 0.05

    if technology_found:

        confidence += 0.10

    if business_impact == "HIGH":

        confidence += 0.05

    elif business_impact == "CRITICAL":

        confidence += 0.10

    # -------------------------
    # Negative Signals
    # -------------------------

    if not technology_found:

        confidence -= 0.20

    if business_impact == "UNKNOWN":

        confidence -= 0.15

    if support_score == 0:

        confidence -= 0.20

    # -------------------------
    # Clamp
    # -------------------------

    confidence = max(0.0, min(confidence, 1.0))

    logger.info(
        f"Confidence : {confidence}"
    )

    return round(
        confidence,
        2
    )