from openai import OpenAI
from clients.client import Client

# Client to interact with the DeepSeek API via OpenRouter
class DeepSeekClient(Client):
    def __init__(self, key):
        super().__init__(key)
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat-v3-0324:free"

    def chat(self, prompt_files, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompts = self.gather_prompts(prompt_files=prompt_files, disaster=disaster, language=language, sending_agency=sending_agency, location=location, time=time, url=url)
        for prompt in prompts:
            client = OpenAI(
                base_url=self.base_url,
                api_key=self.key,
            )

            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                {
                    "role": "user",
                    "content": prompt
                }
                ]
            )

            print(completion.choices[0].message.content)

