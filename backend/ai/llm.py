import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMClient:
    """Client for interacting with the Gemini LLM."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set in the environment."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    def generate(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return the generated text.
        """

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("LLM returned an empty response.")

        return response.text.strip()