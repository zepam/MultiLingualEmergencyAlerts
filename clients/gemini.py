from google import genai
from clients.client import Client

# Client to interact with the Gemini API
class GeminiClient(Client):
    def __init__(self, key):
        super().__init__(key)
        self.model = "gemini-2.0-flash"

    def chat(self, prompt_files, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompts = self.gather_prompts(prompt_files=prompt_files, disaster=disaster, language=language, sending_agency=sending_agency, location=location, time=time, url=url)
        for prompt in prompts:
            client = genai.Client(api_key=self.key)
            response = client.models.generate_content(
                model=self.model, contents=prompt
            )
            print(response.text)

