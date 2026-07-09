from models.categorization_result import (
    CategorizationResult
)

from utils.logger_config import (
    get_logger
)
from llm.incident_validator import (
    validate_incident
)

from services.ai_policy_service import (
    policy
)

# -----------------------------
# Rules
# -----------------------------
from rules.validation_rules import (
    validate
)

from rules.l1_rules import (
    match as l1_match
)

from rules.l2_rules import (
    match as l2_match
)

from rules.l3_rules import (
    match as l3_match
)

from rules.technology_rules import (
    detect
)

from rules.business_rules import (
    evaluate as evaluate_business
)

from rules.priority_rules import (
    evaluate as evaluate_priority
)

# -----------------------------
# Services
# -----------------------------
from services.business_criticality_service import (
    evaluate_business_criticality
)

from services.risk_service import (
    evaluate_risk
)

from services.duplicate_service import (
    check_duplicate
)

from services.confidence_service import (
    calculate_confidence
)

from services.human_review_service import (
    requires_human_review
)

from services.routing_service import (
    determine_route
)

from services.explanation_service import (
    generate_reasoning
)
from llm.incident_classifier import (
    classify_incident
)

from services.decision_merger import (
    merge_decision
)

logger = get_logger(__name__)


def _first_text(*values):

    for value in values:

        if value is not None and str(value).strip():

            return str(value).strip()

    return ""


def _normalise_priority(priority):

    mapping = {

        "1": "P1",

        "2": "P2",

        "3": "P3",

        "4": "P4",

        "5": "P5",

        "p1": "P1",

        "p2": "P2",

        "p3": "P3",

        "p4": "P4",

        "p5": "P5"
    }

    value = str(priority or "").strip()

    return mapping.get(value.lower(), value)


def _join_text(*values):

    parts = []

    for value in values:

        if isinstance(value, list):

            text = " ".join(str(item) for item in value if item)

        else:

            text = str(value or "")

        if text.strip():

            parts.append(text.strip())

    return "\n".join(parts)


def adapt_normalized_event(payload):

    """
    Accept both the old ticket payload and the AMS normalised ErrorEvent.

    Existing rules operate on ticket_id/title/description. This adapter fills
    those fields from incident_id, short_description, message, traceback and
    other normalised fields while preserving the original event.
    """

    adapted = dict(payload)

    ticket_id = _first_text(

        adapted.get("ticket_id"),

        adapted.get("incident_id"),

        adapted.get("external_id"),

        adapted.get("source_event_id"),

        adapted.get("id")
    )

    title = _first_text(

        adapted.get("title"),

        adapted.get("short_description"),

        adapted.get("message"),

        adapted.get("error_type")
    )

    labels = adapted.get("labels") or []

    components = adapted.get("components") or []

    description = _join_text(

        adapted.get("description"),

        adapted.get("raw_description"),

        adapted.get("traceback"),

        adapted.get("message"),

        adapted.get("error_type"),

        adapted.get("file_path"),

        adapted.get("function_name"),

        labels,

        components
    )

    adapted["ticket_id"] = ticket_id or "unknown"

    adapted["title"] = title

    adapted["description"] = description

    adapted["priority"] = _normalise_priority(adapted.get("priority"))

    adapted["environment"] = _first_text(

        adapted.get("environment"),

        adapted.get("impacted_environment"),

        "production"
    )

    adapted["business_service"] = _first_text(

        adapted.get("business_service"),

        adapted.get("configuration_item"),

        adapted.get("assignment_group"),

        adapted.get("repo_full_name")
    )

    adapted["normalised_event_id"] = adapted.get("id")

    adapted["raw_normalised_event"] = payload

    return adapted


def _category_for(support, technology, payload):

    if support == "L3":

        return "code"

    if support == "L2":

        return technology.lower() if technology else "operations"

    if support == "L1":

        return "support"

    if support == "NONE":

        return "rejected"

    return payload.get("issue_category") or "unknown"


def _recommended_action(support, reject, requires_human):

    if reject:

        return "reject"

    if requires_human:

        return "human_review"

    mapping = {

        "L1": "run_l1_rca",

        "L2": "run_l2_rca",

        "L3": "run_l3_rca"
    }

    return mapping.get(support, "human_review")


def _has_code_evidence(payload):

    return bool(

        payload.get("traceback")

        or payload.get("file_path")

        or payload.get("function_name")

        or payload.get("line_number")

        or payload.get("is_code_issue") is True
    )


def categorize(payload):

    logger.info("=" * 60)
    logger.info("CATEGORIZATION STARTED")
    logger.info("=" * 60)

    payload = adapt_normalized_event(payload)

    # ======================================================
    # Validation
    # ======================================================

    validation = validate(payload)

    if not validation["valid"]:

       logger.info("Validation Failed")

       return CategorizationResult(

        ticket_id=payload.get("ticket_id"),

        classification="REJECT",

        support_level="NONE",

        technology="General",

        team="",

        priority="",

        business_impact="LOW",

        business_criticality="LOW",

        risk="LOW",

        risk_score=0,

        duplicate=False,

        duplicate_of=None,

        confidence=validation["confidence"],

        requires_human=False,

        selected_agent="reject_agent",

        backup_agent=None,

        available=True,

        reject=True,

        route_to="reject_agent",

        reason=validation["reason"],

        reasoning=validation["reasoning"],

        is_valid_incident=False,

        category="rejected",

        rca_level="reject",

        needs_human_review=False,

        recommended_next_action="reject",

        source_event_id=payload.get("source_event_id"),

        normalised_event_id=payload.get("normalised_event_id")
    )

    # ======================================================
    # L1 / L2 / L3 Classification
    # ======================================================

    l1_score, l1_rules = l1_match(
        payload
    )

    l2_score, l2_rules = l2_match(
        payload
    )

    l3_score, l3_rules = l3_match(
        payload
    )

    if _has_code_evidence(payload):

        l3_score += 3

        l3_rules = list(l3_rules)

        l3_rules.append(
            "normalised code evidence"
        )

    if l1_score >= l2_score and l1_score >= l3_score:

        support = "L1"

        matched_rules = l1_rules

    elif l2_score >= l3_score:

        support = "L2"

        matched_rules = l2_rules

    else:

        support = "L3"

        matched_rules = l3_rules

    logger.info(
        f"Support Level : {support}"
    )

    # ======================================================
    # Technology Detection
    # ======================================================

    technology, _ = detect(
        payload
    )

    logger.info(
        f"Technology : {technology}"
    )

    # ======================================================
    # Business Impact
    # ======================================================

    business_impact = evaluate_business(
        payload
    )

    logger.info(
        f"Business Impact : {business_impact}"
    )

    # ======================================================
    # Priority
    # ======================================================

    priority = evaluate_priority(
        payload
    )

    logger.info(
        f"Priority : {priority}"
    )

    # ======================================================
    # Business Criticality
    # ======================================================

    criticality = evaluate_business_criticality(
        payload
    )

    logger.info(
        f"Criticality : {criticality['criticality']}"
    )

    # ======================================================
    # Risk Assessment
    # ======================================================

    risk = evaluate_risk(

        payload,

        technology,

        criticality[
            "criticality"
        ]
    )

    logger.info(
        f"Risk : {risk['risk']}"
    )

    # ======================================================
    # Duplicate Detection
    # ======================================================

    duplicate = check_duplicate({

        "ticket_id":

            payload.get(
                "ticket_id"
            ),

        "title":

            payload.get(
                "title"
            ),

        "technology":

            technology
    })

    logger.info(
        f"Duplicate : {duplicate['duplicate']}"
    )

    # ======================================================
    # Confidence
    # ======================================================

    confidence = calculate_confidence(

        validation[
            "confidence"
        ],

        max(

            l1_score,

            l2_score,

            l3_score
        ),

        technology != "General",

        business_impact
    )

    logger.info(
        f"Confidence : {confidence}"
    )
    
    # ======================================================
    # AI Validation + AI Classification
    # ======================================================

    if policy["enable_ai_validation"]:

       if confidence < policy["confidence_threshold"]:

        logger.info("=" * 60)
        logger.info("LOW CONFIDENCE - INVOKING AI")
        logger.info("=" * 60)

        # -----------------------------
        # AI Validation
        # -----------------------------
        logger.info("Calling AI Validator...")
        validation_result = validate_incident(
            payload
        )

        logger.info(validation_result)

        if not validation_result["is_incident"]:

            logger.info("Rejected by AI Validator")

            return CategorizationResult(

                ticket_id=payload.get("ticket_id"),

                classification="REJECT",

                support_level="NONE",

                technology="General",

                team="",

                priority="",

                business_impact="LOW",

                business_criticality="LOW",

                risk="LOW",

                risk_score=0,

                duplicate=False,

                duplicate_of=None,

                confidence=validation_result["confidence"],

                requires_human=False,

                selected_agent="reject_agent",

                backup_agent=None,

                available=True,

                reject=True,

                route_to="reject_agent",

                reason=validation_result["reason"],

                reasoning=[
                    "Rejected by AI Validator."
                ],

                is_valid_incident=False,

                category="rejected",

                rca_level="reject",

                needs_human_review=False,

                recommended_next_action="reject",

                source_event_id=payload.get("source_event_id"),

                normalised_event_id=payload.get("normalised_event_id")
            )

        logger.info("AI confirmed valid incident.")
        logger.info("Calling AI Classifier...")
        # -----------------------------
        # AI Classification
        # -----------------------------

        ai_result = classify_incident(
            payload
        )

        logger.info(ai_result)

        rule_result = {

           "support_level": support,

           "technology": technology,

            "business_impact": business_impact,

            "priority": priority,

            "criticality": criticality["criticality"],

            "risk": risk["risk"],

            "confidence": confidence
       }

        merged = merge_decision(

            rule_result,

            ai_result

        )

        support = merged["support_level"]

        technology = merged["technology"]

        business_impact = merged["business_impact"]

        confidence = merged["confidence"]
    # ======================================================
    # Human Review
    # ======================================================

    review = requires_human_review(

        confidence,

        criticality[
            "criticality"
        ],

        risk[
            "risk"
        ],

        duplicate[
            "duplicate"
        ],

        support
    )

    logger.info(
        f"Human Review : {review['requires_review']}"
    )

    # ======================================================
    # Routing
    # ======================================================

    route = determine_route(

        support,

        technology
    )

    selected_agent = route[
        "selected_agent"
    ]

    backup_agent = route[
        "backup_agent"
    ]

    available = route[
        "available"
    ]

    logger.info(
        f"Selected Agent : {selected_agent}"
    )

    # ======================================================
    # Explanation
    # ======================================================

    reasoning = generate_reasoning(

        validation,

        support,

        technology,

        business_impact,

        matched_rules
    )

    logger.info("=" * 60)
    logger.info("CATEGORIZATION COMPLETED")
    logger.info("=" * 60)

    recommended_next_action = _recommended_action(

        support,

        False,

        review[
            "requires_review"
        ]
    )

    return CategorizationResult(

        ticket_id=payload.get(
            "ticket_id"
        ),

        classification="INCIDENT",

        support_level=support,

        technology=technology,

        team=technology,

        priority=priority,

        business_impact=business_impact,

        business_criticality=criticality[
            "criticality"
        ],

        risk=risk[
            "risk"
        ],

        risk_score=risk[
            "risk_score"
        ],

        duplicate=duplicate[
            "duplicate"
        ],

        duplicate_of=duplicate[
            "duplicate_of"
        ],

        confidence=confidence,

        requires_human=review[
            "requires_review"
        ],

        selected_agent=selected_agent,

        backup_agent=backup_agent,

        available=available,

        reject=False,

        route_to=selected_agent,

        reason="Incident Categorized",

        reasoning=reasoning,

        is_valid_incident=True,

        category=_category_for(

            support,

            technology,

            payload
        ),

        rca_level=support,

        needs_human_review=review[
            "requires_review"
        ],

        recommended_next_action=recommended_next_action,

        source_event_id=payload.get("source_event_id"),

        normalised_event_id=payload.get("normalised_event_id")
    )
