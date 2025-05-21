from google.cloud import translate_v2 as translate
from clients.client import Client

# Client to interact with the Google Cloud Translation API
class GoogleCloudTranslationClient(Client):
    def __init__(self, logger, key="unused"):
        super().__init__(key, logger)

    def chat(self, prompt_file, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompt = self.gather_prompt(prompt_file=prompt_file, disaster=disaster, language=language,
                                    sending_agency=sending_agency, location=location, time=time, url=url)
        translate_client = translate.Client()

        language_code = self.translation_map()[language]
        result = translate_client.translate(prompt, target_language=language_code)

        return result["translatedText"]

    # See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    def translation_map(self):
        return {
            "Spanish": "es",
            "Arabic": "ar",
            "Haitian Creole": "ht",
            "Vietnamese": "vi",
            "Mandarin": "zh"
        }