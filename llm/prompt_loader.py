from pathlib import Path


PROMPT_FOLDER = Path("prompts")


def load_prompt(

        filename: str

):

    path = PROMPT_FOLDER / filename

    with open(

        path,

        encoding="utf-8"

    ) as file:

        return file.read()