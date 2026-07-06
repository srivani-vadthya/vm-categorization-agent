L1_KEYWORDS = [

    "vpn",

    "browser",

    "cache",

    "login",

    "access denied",

    "user issue",

    "password",

    "authentication",

    "single user"
]


def is_l1(text):

    text = text.lower()

    for keyword in L1_KEYWORDS:

        if keyword in text:

            return True

    return False