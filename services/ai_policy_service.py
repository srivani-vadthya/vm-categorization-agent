import json

from pathlib import Path


CONFIG = Path(
    "config/ai_policy.json"
)


def load_ai_policy():

    with open(CONFIG) as file:

        return json.load(file)


policy = load_ai_policy()