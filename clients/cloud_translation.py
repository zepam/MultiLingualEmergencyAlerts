from google.cloud import translate
from google.api_core import exceptions
from clients.client import Client
from clients.translation_map import TRANSLATION_MAP

class GoogleCloudTranslationClient(Client):
    # Trackers for the session
    _error_counts = {}
    _DISABLED_LANGUAGES = set()
    _SERVICE_QUOTA_EXCEEDED = False  # Global kill-switch

    def __init__(self, logger, key="unused"):
        super().__init__(key, logger)
        self.project_id = "multilingual-alerts-460703"

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompt = self.gather_prompt(prompt_file=prompt_file, disaster=disaster, language=language,
                                    sending_agency=sending_agency, location=location, time=time, url=url)
        
        # 1. Stop immediately if the global quota was hit earlier
        if self._SERVICE_QUOTA_EXCEEDED:
            return prompt

        target_language_code = TRANSLATION_MAP.get(language, language)

        # 2. Stop if this specific language is blacklisted
        if target_language_code in self._DISABLED_LANGUAGES:
            return prompt

        translate_client = translate.TranslationServiceClient(
            client_options={"quota_project_id": self.project_id}
        )
        parent = f"projects/{self.project_id}"

        try:
            result = translate_client.translate_text(
                parent=parent,
                contents=[prompt],
                target_language_code=target_language_code
            )
            return result.translations[0].translated_text

        except exceptions.ResourceExhausted as e:
            # This is the "Quota Exceeded" 429 error
            self._SERVICE_QUOTA_EXCEEDED = True
            self.logger.critical(f"GLOBAL QUOTA EXCEEDED: Stopping all translations. Error: {e}")
            return prompt

        except exceptions.TooManyRequests as e:
            # This is the "Too Fast" 429 error (Rate Limit)
            current_count = self._error_counts.get(target_language_code, 0) + 1
            self._error_counts[target_language_code] = current_count
            
            if current_count >= 10:
                self._DISABLED_LANGUAGES.add(target_language_code)
                self.logger.error(f"Language {target_language_code} disabled after 10 rate-limit strikes.")
            return prompt

        except exceptions.InvalidArgument as e:
            self.logger.error(f"Unsupported language code '{target_language_code}': {e}")
            return prompt
            
        except Exception as e:
            self.logger.error(f"Unexpected translation error: {e}")
            return prompt