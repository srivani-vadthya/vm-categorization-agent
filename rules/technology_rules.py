def detect_technology(text):

    text = text.lower()

    if "policycenter" in text:

        return "Guidewire"

    if "claimcenter" in text:

        return "Guidewire"

    if "servicenow" in text:

        return "ServiceNow"

    if "kubernetes" in text:

        return "Kubernetes"

    if "database" in text:

        return "Database"

    if "api" in text:

        return "Application"

    if "cpu" in text:

        return "Infrastructure"

    return "General"