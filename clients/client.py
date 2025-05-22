import tenacity
from google import genai
import openai

# Abstract Client parent
class Client:
    def __init__(self, key, logger):
        self.key = key
        self.temperature = 1.0
        self.max_tokens = 2048
        self.top_p = 1.0
        self.logger = logger

    def gather_prompt(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        with open(prompt_file, "r") as file:
            prompt_text = file.read()
            prompt_text = prompt_text.replace("{DISASTER}", disaster)
            prompt_text = prompt_text.replace("{LANGUAGE}", language)
            if sending_agency:
                prompt_text = prompt_text.replace("{SENDING_AGENCY}", sending_agency)
            if sending_agency:
                prompt_text = prompt_text.replace("{LOCATION}", location)
            if sending_agency:
                prompt_text = prompt_text.replace("{TIME}", time)

        return prompt_text
    
    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=0.5, min=60, max=180), stop=tenacity.stop_after_attempt(3))
    def safe_chat(self, prompt_file, language, disaster):
        try:
            return self.chat(prompt_file=prompt_file, language=language, disaster=disaster)
        except (openai.RateLimitError, tenacity.RetryError) as e:
            self.logger.info(f"Error: {e.message}")
