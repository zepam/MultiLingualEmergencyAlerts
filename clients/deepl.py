import deepl
from clients.client import Client
import tenacity


# Client to interact with the DeepL API
class DeepLClient(Client):
    def __init__(self, key: str, logger=None):

        super().__init__(key, logger)
        self.client = deepl.Translator(auth_key=self.key)   # deepL library selects the Free or Pro API endpoint based on key
        #self.logger.info("DeepLClient initialized.")

        # Fetch and store supported target languages during initialization
        self.supported_target_languages_ids = set()
        try:
            # get_target_languages() returns a list of deepl.Language objects
            for lang in self.client.get_target_languages():
                self.supported_target_languages_ids.add(lang.code)
            #self.logger.info(f"DeepL supports {len(self.supported_target_languages_ids)} target languages.")
        except Exception as e:
            self.logger.error(f"Failed to fetch supported DeepL target languages: {e}.")

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=0.5, min=3, max=180), stop=tenacity.stop_after_attempt(3))
    def translate(self, text: str, target_language: str, source_language: str = None) -> str:

        if not text.strip():
            self.logger.warning("Text was empty.")
            return ""

        # Map language names to DeepL language codes
        try:
            target_lang_code = self.translation_map().get(target_language, target_language)
            if source_language:
                source_lang_code = self.translation_map().get(source_language, source_language)
            else:
                source_lang_code = None

            # Validate if the mapped language code is a valid DeepL target language
            if target_lang_code not in self.supported_target_languages_ids:
                self.logger.warning(f"DeepL does not support target language: '{target_language}' (resolved code: '{target_lang_code}'). Skipping translation.")
                return ""
                #raise ValueError(f"Target language '{target_lang_code}' not supported by DeepL.")

        except KeyError as e:
            self.logger.error(f"Language mapping error: {e}. Check if the language name is correct.")
            #raise ValueError(f"Unsupported language name provided: {e}")
            return ""
        
        # translate things
        try:
            self.logger.info(f"Attempting to translate text to {target_lang_code} (source: {source_lang_code or 'auto-detect'})...")
            result = self.client.translate_text(
                text,
                source_lang=source_lang_code,
                target_lang=target_lang_code
            )
            translated_content = result.text
            self.logger.info(f"Successfully translated {target_lang_code}.")
            return translated_content
        except deepl.DeepLException as e:
            self.logger.error(f"DeepL translation failed '{target_language}': {e}")
            #raise # Re-raise the exception after logging
            return ""
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during DeepL translation: {e}")
            return ""
    # See https://support.deepl.com/hc/en-us/articles/360019925219-DeepL-Translator-languages
    def translation_map(self) -> dict[str, str]:
        """
        Provides a mapping from common language names to DeepL-compatible language codes.
        Refer to DeepL API documentation for the most up-to-date list of supported codes.

        Returns:
            dict: A dictionary mapping language names (keys) to DeepL codes (values).
        """
        return {
            "English": "en-US", 
            "Spanish": "es",
            "Arabic": "ar",
            "Haitian Creole": "ht", 
            "Vietnamese": "vi",
            "Chinese (Traditional)": "zh", # DeepL uses 'zh' for both Simplified and Traditional, often defaulting to Simplified
            "Chinese (Simplified)": "zh",
        }
