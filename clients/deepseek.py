from openai import OpenAI
from clients.client import Client

# Client to interact with the DeepSeek API via OpenRouter
# 50 free requests per day
# 20 free requests per minute
class DeepSeekClient(Client):
    def __init__(self, key, logger):
        super().__init__(key, logger)
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat-v3-0324:free"

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompt = self.gather_prompt(prompt_file=prompt_file, disaster=disaster, language=language, sending_agency=sending_agency,
                                    location=location, time=time, url=url)
        client = OpenAI(base_url=self.base_url, api_key=self.key)

        completion = client.chat.completions.create(model=self.model,
                                                    messages=[
                                                        {
                                                            "role": "user",
                                                            "content": prompt
                                                        }
                                                    ],
                                                    temperature=self.temperature,
                                                    max_tokens=self.max_tokens,
                                                    top_p=self.top_p)

        return completion.choices[0].message.content

