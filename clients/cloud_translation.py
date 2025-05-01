from google.cloud import translate_v2 as translate
from clients.client import Client

# Client to interact with the Google Cloud Translation API
class GoogleCloudTranslationClient(Client):
    def __init__(self, key="blah"):
        super().__init__(key)

    def chat(self, prompt_files, disaster, language, sending_agency=None, location=None, time=None, url=None):
        prompts = self.gather_prompts(prompt_files=prompt_files, disaster=disaster, language=language, sending_agency=sending_agency, location=location, time=time, url=url)
        for prompt in prompts:
            translate_client = translate.Client()

            # Text can also be a sequence of strings, in which case this method
            # will return a sequence of results for each text.
            # See https://g.co/cloud/translate/v2/translate-reference#supported_languages
            result = translate_client.translate(prompt, target_language=language)

            print("Translation: {}".format(result["translatedText"]))
