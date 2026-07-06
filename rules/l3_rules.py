L3_KEYWORDS = [

    "exception",

    "stacktrace",

    "nullpointer",

    "segmentation fault",

    "code defect",

    "deployment bug",

    "regression",

    "compile",

    "java",

    "python",

    "traceback",

    "syntax error"
]


def is_l3(text):

    text = text.lower()

    for keyword in L3_KEYWORDS:

        if keyword in text:

            return True

    return False