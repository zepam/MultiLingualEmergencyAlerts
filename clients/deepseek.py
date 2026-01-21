import time
import tenacity
import httpx
from openai import OpenAI
from clients.client import Client
from clients.translation_map import TRANSLATION_MAP

# Client to interact with the DeepSeek API via OpenRouter
# 50 free requests per day
# 20 free requests per minute

def wait_on_rate_limit(retry_state):
    exception = retry_state.outcome.exception()
    if isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code == 429:
        if reset_ms := exception.response.headers.get("X-RateLimit-Reset"):
        #if reset_ms:
            reset_time = int(reset_ms) / 1000
            now = time.time()
            wait_seconds = max(0, reset_time - now)
            return wait_seconds + 1  # precise wait from header
        # Fallback: we know it's ~20 req/min → wait ~3s
        return 3.5  
    # If it’s another error, backoff more conservatively
    return tenacity.wait_exponential(multiplier=1, min=3, max=60)(retry_state)

class DeepSeekClient(Client):
    def __init__(self, key, logger):
        super().__init__(key, logger)
        # self.base_url = "https://openrouter.ai/api/v1"
        # self.model = "deepseek/deepseek-chat-v3-0324:free" 
        # updated 01/20/26 to below
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat-v3-0324"

    #@tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=6, max=180), stop=tenacity.stop_after_attempt(3))
    @tenacity.retry(wait=wait_on_rate_limit, stop=tenacity.stop_after_attempt(3))
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

