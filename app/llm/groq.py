from groq import Groq
from core.config import settings

class GroqLLM:

    def __init__(self, model):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )
        self.model = model

    def invoke(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.choices[0].message.content