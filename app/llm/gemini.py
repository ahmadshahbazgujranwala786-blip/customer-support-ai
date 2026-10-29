from google import genai
from core.config import settings

class GeminiLLM:

    def __init__(self, model):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = model


    def invoke(self, prompt):

        response = self.client.models.generate_content(

            model=self.model,

            contents=prompt
        )

        return response.text