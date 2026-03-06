from google.cloud import translate
from google.api_core import exceptions  # Add this import for error handling
from clients.client import Client
from clients.translation_map import TRANSLATION_MAP

class GoogleCloudTranslationClient(Client):
    def __init__(self, logger, key="unused"):
        super().__init__(key, logger)
        self.project_id = "multilingual-alerts-460703"

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompt = self.gather_prompt(prompt_file=prompt_file, disaster=disaster, language=language,
                                    sending_agency=sending_agency, location=location, time=time, url=url)
        
        translate_client = translate.TranslationServiceClient(
            client_options={"quota_project_id": self.project_id}
        )

        # Map language names to language codes
        target_language_code = TRANSLATION_MAP.get(language, language)
        parent = f"projects/{self.project_id}"

        try:
            result = translate_client.translate_text(
                parent=parent,
                contents=[prompt],
                target_language_code=target_language_code
            )
            return result.translations[0].translated_text

        except exceptions.InvalidArgument as e:
            # This triggers when the language code is unsupported
            self.logger.error(f"Unsupported language code '{target_language_code}': {e}")
            return ""  # Return empty text as fallback
            
        except Exception as e:
            # Catch-all for other issues (network, quota, etc.)
            self.logger.error(f"Translation failed: {e}")
            return "" # return empty text as fallback