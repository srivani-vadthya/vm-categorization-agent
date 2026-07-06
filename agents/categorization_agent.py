from rules.reject_rules import (
    is_rejected
)

from rules.l1_rules import (
    is_l1
)

from rules.l2_rules import (
    is_l2
)

from rules.l3_rules import (
    is_l3
)

from rules.technology_rules import (
    detect_technology
)

from services.routing_service import (
    determine_route
)


def categorize(payload):

    text = " ".join([

        str(
            payload.get(
                "title",
                ""
            )
        ),

        str(
            payload.get(
                "description",
                ""
            )
        )
    ])

    technology = detect_technology(
        text
    )

    # reject
    if is_rejected(text):

        return {

            "ticket_id":
                payload.get(
                    "ticket_id"
                ),

            "classification":
                "REJECT",

            "support_level":
                "NONE",

            "reject":
                True,

            "confidence":
                0.95,

            "reason":
                "Non-operational request",

            "route_to":
                "reject"
        }

    # l1
    if is_l1(text):

        return {

            "ticket_id":
                payload.get(
                    "ticket_id"
                ),

            "classification":
                "INCIDENT",

            "support_level":
                "L1",

            "team":
                "Support",

            "technology":
                technology,

            "route_to":
                determine_route(
                    "L1",
                    technology
                ),

            "confidence":
                0.90,

            "reject":
                False,

            "reason":
                "Basic support issue"
        }

    # l3
    if is_l3(text):

        return {

            "ticket_id":
                payload.get(
                    "ticket_id"
                ),

            "classification":
                "INCIDENT",

            "support_level":
                "L3",

            "team":
                "Development",

            "technology":
                technology,

            "route_to":
                determine_route(
                    "L3",
                    technology
                ),

            "confidence":
                0.90,

            "reject":
                False,

            "reason":
                "Code level issue"
        }

    # default L2
    return {

        "ticket_id":
            payload.get(
                "ticket_id"
            ),

        "classification":
            "INCIDENT",

        "support_level":
            "L2",

        "team":
            "Operations",

        "technology":
            technology,

        "route_to":
            determine_route(
                "L2",
                technology
            ),

        "confidence":
            0.85,

        "reject":
            False,

        "reason":
            "Operational issue"
    }