import google.genai as genai
from clients.client import Client
from clients.translation_map import TRANSLATION_MAP

# Client to interact with the Gemini API
# Free tier: 10 requests per minute
class GeminiClient(Client):
    def __init__(self, key, logger):
        super().__init__(key, logger)
        self.model = "gemini-2.5-flash"
        # Initialize the client at instantiation
        self.client = genai.Client(api_key=self.key)

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompt = self.gather_prompt(
            prompt_file=prompt_file, 
            disaster=disaster, 
            language=language, 
            sending_agency=sending_agency,
            location=location,
            time=time,
            url=url
        )

        # disable thinking because it is taking so long, disables the 'thinking' step for models that support it
        thinking_config = genai.types.ThinkingConfig(
            thinking_budget=0
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config = genai.types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                top_p=self.top_p,
                thinking_config=thinking_config 
            )
        )
        
        return response.text

