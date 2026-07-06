L2_KEYWORDS = [

    "cpu",

    "memory",

    "database",

    "timeout",

    "application",

    "server",

    "kubernetes",

    "pod",

    "cluster",

    "api",

    "gateway",

    "service unavailable",

    "disk",

    "job failed",

    "latency",

    "performance"
]


def is_l2(text):

    text = text.lower()

    for keyword in L2_KEYWORDS:

        if keyword in text:

            return True

    return False