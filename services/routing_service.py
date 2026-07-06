def determine_route(
        support_level,
        technology):

    if support_level == "L1":

        return "l1_support_agent"

    if support_level == "L2":

        if technology == "Guidewire":

            return "l2_guidewire_agent"

        if technology == "Infrastructure":

            return "l2_infrastructure_agent"

        if technology == "Database":

            return "l2_database_agent"

        return "l2_application_agent"

    if support_level == "L3":

        return "l3_development_agent"

    return "reject"