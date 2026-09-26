import os
import time

import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core.exceptions import (
    DeadlineExceeded,
    ResourceExhausted,
    ServiceUnavailable,
)

load_dotenv()


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-1.5-flash",
        )

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured"
            )

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            self.model_name
        )

    def generate(
        self,
        prompt: str,
        max_retries: int = 3,
    ) -> str:

        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(prompt)

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response"
                    )

                return response.text

            except (
                ResourceExhausted,
                ServiceUnavailable,
                DeadlineExceeded,
            ) as exc:

                if attempt == max_retries:
                    raise RuntimeError(
                        "Gemini request failed after retries"
                    ) from exc

                delay = 2 ** attempt
                time.sleep(delay)

        raise RuntimeError("Gemini request failed")