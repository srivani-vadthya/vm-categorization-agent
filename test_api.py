from llm.incident_validator import (

    validate_incident

)

payload = {

"title":

"Oracle Database Down",

"description":

"Production Database unavailable."

}

print(

    validate_incident(

        payload

    )

)