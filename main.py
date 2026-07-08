from fastapi import FastAPI

from api.categorization_api import (
    router
)

app = FastAPI(

    title="Enterprise Categorization Agent",

    version="1.0.0"
)


@app.get("/")
def home():

    return {

        "application":
            "Enterprise Categorization Agent",

        "status":
            "Running"
    }


@app.get("/health")
def health():

    return {

        "status":
            "UP"
    }


app.include_router(
    router
)