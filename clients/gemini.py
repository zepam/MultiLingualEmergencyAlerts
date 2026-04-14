import google.genai as genai
import re, time
from google.genai import errors as genai_errors
from clients.client import Client
from clients.exceptions import QuotaExhaustedError

# Client to interact with the Gemini API
# Free tier: 5/min or 20/day
class GeminiClient(Client):

    # class level variables to track quota exhaustion across all instances
    # the client re-instantiates with each call, so we need a class-level latch
    _quota_exhausted = False   # class-wide latch
    _quota_message = None

    def __init__(self, key, logger):
        super().__init__(key, logger)
        self.model = "gemini-2.5-flash"
        # Initialize the client at instantiation
        self.client = genai.Client(api_key=self.key)

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        # If we already know quota is exhausted, fail fast (no waiting, no API call)
        if GeminiClient._quota_exhausted:
            raise QuotaExhaustedError(GeminiClient._quota_message or "Gemini quota exhausted")
 
        
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
        thinking_config = genai.types.ThinkingConfig(thinking_budget=0)

        try:
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
             
        except genai_errors.ClientError as e:
            if getattr(e, "status_code", None) == 429:
                raise

            msg = str(e)

            # HARD cap: stop retrying for the rest of the run
            if (
                "GenerateRequestsPerDayPerProjectPerModel-FreeTier" in msg or 
                "GenerateRequestsPerDay" in msg
            ):
                GeminiClient._quota_exhausted = True
                GeminiClient._quota_message = msg
                raise QuotaExhaustedError(msg) from e

            # Soft cap (per-minute): wait then retry
            m = re.search(r"Please retry in ([0-9.]+)s", msg)
            if m:
                time.sleep(float(m.group(1)) + 0.25)
            raise

