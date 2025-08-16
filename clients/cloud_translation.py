from google.cloud import translate
from clients.client import Client
from clients.translation_map import TRANSLATION_MAP

# Client to interact with the Google Cloud Translation API (Basic)
class GoogleCloudTranslationClient(Client):
    def __init__(self, logger, key="unused"):
        super().__init__(key, logger)
        # pass the project ID into the constructor
        # This is required for the Google Cloud Translation API to work properly
        # or you can set the GOOGLE_CLOUD_PROJECT environment variable
        self.project_id = "multilingual-alerts-460703"

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompt = self.gather_prompt(prompt_file=prompt_file, disaster=disaster, language=language,
                                    sending_agency=sending_agency, location=location, time=time, url=url)
        translate_client = translate.TranslationServiceClient(
            client_options={"quota_project_id": self.project_id}
        )

        # Map language names to language codes
        target_language_code = TRANSLATION_MAP.get(language, language)

        # Validate if the mapped language code is a valid DeepL target language
        # if target_language_code not in self.supported_target_languages_ids:
        #     self.logger.warning(f"Service does not support target language: '{language}' (resolved code: '{target_language_code}'). Skipping translation.")
        #     return ""

        parent = f"projects/{self.project_id}"

        result = translate_client.translate_text(
            parent = parent,
            contents = [prompt],
            target_language_code=target_language_code
        )

        return result.translations[0].translated_text

    # See https://cloud.google.com/translate/docs/languages
    # def translation_map(self):
    #     return {
    #         "Spanish": "es",
    #         "Arabic": "ar",
    #         "Haitian Creole": "ht",
    #         "Vietnamese": "vi",
    #         # zh-CN was chosed based on the needs of the population of Seattle
    #         "Chinese (Traditional)": "zh-TW",
    #         "Chinese (Simplified)": "zh-CN"
    #     }