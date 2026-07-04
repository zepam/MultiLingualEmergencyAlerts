import tenacity
from openai import OpenAI

from clients.client import Client
from clients.translation_map import TRANSLATION_MAP

# Client to interact with the ChatGPT API 
class ChatGPTClient(Client):
    def __init__(self, key, logger):
        super().__init__(key, logger)
        self.model = "gpt-5.4-nano-2026-03-17"

    @tenacity.retry(
            wait=tenacity.wait_exponential(multiplier=1, min=6, max=180),
            stop=tenacity.stop_after_attempt(3),
            reraise=True
        )
    
    def chat(self, 
        prompt_file, 
        disaster, 
        language, 
        sending_agency=None, 
        location=None, 
        time=None, 
        url=None):
        
        prompt = self.gather_prompt(
            prompt_file=prompt_file, 
            disaster=disaster, 
            language=language,
            sending_agency=sending_agency, 
            location=location, 
            time=time, 
            url=url
        )

        client = OpenAI(api_key=self.key)
        
        # response = client.chat.completions.create(
        #     model=self.model,
        #     messages=[
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=self.temperature,
        #     max_tokens=self.max_tokens,
        #     top_p=self.top_p
        # )

        response = client.responses.create(
            model=self.model,
            input=prompt,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )

        return response.output_text

