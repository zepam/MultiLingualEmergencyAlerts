import tenacity
import openai
from clients.exceptions import QuotaExhaustedError
from google.genai import errors as genai_errors

# Abstract Client parent
class Client:
    def __init__(self, key, logger):
        self.key = key
        self.temperature = 1.0
        self.max_tokens = 300
        #self.max_tokens = 2048      
        self.top_p = 1.0
        self.logger = logger

    # we aren't actually using these additional arguments for sending_agency, location, url
    def gather_prompt(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        with open(prompt_file, "r") as file:
            prompt_text = file.read()
            prompt_text = prompt_text.replace("{DISASTER}", disaster)
            prompt_text = prompt_text.replace("{LANGUAGE}", language)
            if sending_agency:
                prompt_text = prompt_text.replace("{SENDING_AGENCY}", sending_agency)
            #if sending_agency:
            if location:
                prompt_text = prompt_text.replace("{LOCATION}", location)
            #if sending_agency:
            if time:
                prompt_text = prompt_text.replace("{TIME}", time)

        return prompt_text
    
    @tenacity.retry(
            reraise=True,
            wait=tenacity.wait_exponential(multiplier=2, min=5, max=120), # adjust to model limits
            stop=tenacity.stop_after_attempt(10),
            retry = tenacity.retry_if_not_exception_type(QuotaExhaustedError),
        )
    
    def safe_chat(self, prompt_file, language, disaster):
        # IMPORTANT: don't catch-and-log here unless you re-raise,
        # otherwise Tenacity thinks it succeeded and won't retry.
        return self.chat(prompt_file=prompt_file, language=language, disaster=disaster)