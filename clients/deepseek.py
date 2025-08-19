from openai import OpenAI
from clients.client import Client
import httpx
from clients.translation_map import TRANSLATION_MAP

# Client to interact with the DeepSeek API via OpenRouter
# 50 free requests per day
# 20 free requests per minute
class DeepSeekClient(Client):
    def __init__(self, key, logger):
        super().__init__(key, logger)
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "deepseek/deepseek-chat-v3-0324:free"

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        # Get language code from translation map or use language as is if not found
        language_code = TRANSLATION_MAP.get(language, language)
        
        prompt = self.gather_prompt(
            prompt_file=prompt_file,
            disaster=disaster,
            language=language_code,
            sending_agency=sending_agency,
            location=location,
            time=time,
            url=url
        )
        
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.key,
            http_client=httpx.Client(
                headers={
                    "HTTP-Referer": "http://localhost",
                    "User-Agent": "OpenAI-Python"
                }
            )
        )

        try:
            completion = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                extra_body={}
            )
        except Exception as e:
            self.logger.error(f"DeepSeek API request failed: {e}")
            return None

        # Guard against None or unexpected shape
        if not completion or not hasattr(completion, "choices") or len(completion.choices) == 0:
            self.logger.error(f"DeepSeek returned invalid response: {completion}")
            return None

        return completion.choices[0].message.content

