import os

from dotenv import load_dotenv

from groq import Groq

load_dotenv()


class GroqClient:

    def __init__(self):

        self.client = Groq(

            api_key=os.getenv(
                "GROQ_API_KEY"
            )

        )

        self.model = os.getenv(

            "GROQ_MODEL",

            "llama-3.3-70b-versatile"

        )

    def chat(

            self,

            prompt,

            temperature=0,

            max_tokens=400

    ):

        response = self.client.chat.completions.create(

            model=self.model,

            temperature=temperature,

            max_tokens=max_tokens,

            messages=[

                {

                    "role": "user",

                    "content": prompt

                }

            ]

        )

        return response.choices[0].message.content


groq_client = GroqClient()