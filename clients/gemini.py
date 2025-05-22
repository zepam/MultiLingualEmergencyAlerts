from google import genai
from google.genai import types
from clients.client import Client

# Client to interact with the Gemini API
# Free tier: 10 requests per minute
class GeminiClient(Client):
    def __init__(self, key, logger):
        super().__init__(key, logger)
        self.model = "gemini-2.0-flash"

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompt = self.gather_prompt(prompt_file=prompt_file, disaster=disaster, language=language, sending_agency=sending_agency,
                                    location=location, time=time, url=url)
        client = genai.Client(api_key=self.key)

        response = client.models.generate_content(model=self.model, contents=prompt,
                                                  config=types.GenerateContentConfig(temperature=self.temperature,
                                                                                     max_output_tokens=self.max_tokens,
                                                                                     top_p=self.top_p))
        
        return response.text

