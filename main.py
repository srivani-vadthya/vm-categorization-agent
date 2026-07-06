from fastapi import FastAPI

from api.categorization_api import (
    router
)

app = FastAPI(

    title=
        "Categorization Agent"
)


@app.get("/")
def home():

    return {

        "message":
            "Categorization Agent Running"
    }


app.include_router(
    router
)