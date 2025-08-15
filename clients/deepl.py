import deepl
from clients.client import Client
import tenacity


# Client to interact with the DeepL API
class DeepLClient(Client):
    """
    A client to interact with the DeepL Translation API.

    This class extends a base 'Client' class (assumed to be defined elsewhere)
    to handle API key management and logging. It provides a method to translate text.
    It also includes a mapping for common language names to DeepL-compatible codes.
    """

    def __init__(self, key: str, logger=None):
        """
        Initializes the DeepLClient.

        Args:
            key (str): Your DeepL API key.
            logger (Logger, optional): A logger instance for logging messages.
                                       Defaults to None.
        """
        super().__init__(key, logger)
        # Initialize the DeepL Translator client.
        # The DeepL library automatically selects the Free or Pro API endpoint
        # based on the provided auth_key.
        self.client = deepl.Translator(auth_key=self.key)
        self.logger.info("DeepLClient initialized.")

        # Fetch and store supported target languages during initialization
        self.supported_target_languages_ids = set()
        try:
            # get_target_languages() returns a list of deepl.Language objects
            for lang in self.client.get_target_languages():
                self.supported_target_languages_ids.add(lang.code) # Store the language code (e.g., 'fr', 'es')
            self.logger.info(f"DeepL supports {len(self.supported_target_languages_ids)} target languages.")
        except Exception as e:
            self.logger.error(f"Failed to fetch supported DeepL target languages: {e}. Translations for unsupported languages might fail later.")
            # In a production setup, you might want to raise this error or handle it more robustly
            # e.g., by disabling DeepL for the session or loading a cached list.

    def chat(self, text: str, target_language: str, source_language: str = None) -> str:
        """
        Translates the given text using the DeepL API.

        Args:
            text (str): The text content to be translated.
            target_language (str): The language name or code for the target language (e.g., 'Spanish', 'en-US').
                                   This will be mapped to DeepL's internal codes using translation_map().
            source_language (str, optional): The language name or code for the source language (e.g., 'English', 'de').
                                             If None, DeepL will auto-detect the source language.
                                             Defaults to None.

        Returns:
            str: The translated text.

        Raises:
            deepl.DeepLError: If the DeepL API call fails for any reason
                              (e.g., invalid key, rate limit, network issues).
            ValueError: If an unsupported language name is provided.
        """
        if not text:
            self.logger.warning("Empty text.")
            return ""
        
        try:
            # Map friendly language name (e.g., "Haitian Creole") to DeepL code (e.g., "fr")
            target_lang_code = self.translation_map().get(target_language, target_language)
            if source_language:
                source_lang_code = self.translation_map().get(source_language, source_language)
            else:
                source_lang_code = None

            # --- CRITICAL NEW CHECK FOR LANGUAGE COVERAGE ---
            # Check if the resolved target language code is actually supported by DeepL
            if target_lang_code not in self.supported_target_languages_ids:
                # Log a warning and raise a ValueError
                self.logger.warning(f"DeepL does not support target language: '{target_language}' (resolved code: '{target_lang_code}'). Skipping translation.")
                raise ValueError(f"Target language '{target_lang_code}' not supported by DeepL.")
            
            # You can add a similar check for source_lang_code if you frequently specify it
            # and want to preemptively catch unsupported source languages.
            # However, DeepL's auto-detection often handles this gracefully.

        except KeyError as e:
            self.logger.error(f"Language mapping error: {e}. Check if the language name is correct.")
            raise ValueError(f"Unsupported language name provided: {e}")

        try:
            self.logger.info(f"Attempting to translate text to {target_lang_code} (source: {source_lang_code or 'auto-detect'})...")
            result = self.client.translate_text(
                text,
                source_lang=source_lang_code,
                target_lang=target_lang_code
            )
            translated_content = result.text
            self.logger.info("Text successfully translated.")
            return translated_content
        except deepl.DeepLException as e:
            self.logger.error(f"DeepL translation failed for target language '{target_lang_code}': {e}")
            raise # Re-raise the exception after logging
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during DeepL translation: {e}")
            raise


        # # Map friendly language names to DeepL language codes

        # target_language_code = self.translation_map().get(target_language, target_language)
        # if source_language:
        #     source_language_code = self.translation_map().get(source_language, source_language)
        # else:
        #     source_language_code = None

        # # Validate if the mapped language code is a valid DeepL target language
        # if target_language_code not in self.translation_map().values() and len(target_language_code) > 2:
        #     self.logger.error(f"Unsupported target language provided: {target_language}")
        #     raise ValueError(f"Unsupported target language: {target_language}. Please use a supported name or exact DeepL code.")
        # if source_language_code and source_language_code not in self.translation_map().values() and len(source_language_code) > 2:
        #         self.logger.error(f"Unsupported source language provided: {source_language}")
        #         raise ValueError(f"Unsupported source language: {source_language}. Please use a supported name or exact DeepL code.")

        # result = self.client.translate_text(
        #     text,
        #     source_language=source_language_code,
        #     target_language=target_language_code
        # )
        # translated_content = result.text

        # return translated_content

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=0.5, min=60, max=180), stop=tenacity.stop_after_attempt(3))
    def translate(self, text: str, target_language: str, source_language: str = None) -> str:
        """
        Translates the given text using the DeepL API.

        Args:
            text (str): The text content to be translated.
            target_language (str): The language name or code for the target language (e.g., 'Spanish', 'en-US').
                                   This will be mapped to DeepL's internal codes using translation_map().
            source_language (str, optional): The language name or code for the source language (e.g., 'English', 'de').
                                             If None, DeepL will auto-detect the source language.
                                             Defaults to None.

        Returns:
            str: The translated text.
        """
        if not text:
            self.logger.warning("Attempted to translate empty text.")
            return ""

        # Map friendly language names to DeepL language codes
        try:
            target_lang_code = self.translation_map().get(target_language, target_language)
            if source_language:
                source_lang_code = self.translation_map().get(source_language, source_language)
            else:
                source_lang_code = None

            # Validate if the mapped language code is a valid DeepL target language
            if target_lang_code not in self.translation_map().values() and len(target_lang_code) > 2:
                self.logger.error(f"Unsupported target language provided: {target_language}")
                raise ValueError(f"Unsupported target language: {target_language}. Please use a supported name or exact DeepL code.")
            if source_lang_code and source_lang_code not in self.translation_map().values() and len(source_lang_code) > 2:
                self.logger.error(f"Unsupported source language provided: {source_language}")
                raise ValueError(f"Unsupported source language: {source_language}. Please use a supported name or exact DeepL code.")

        except KeyError as e:
            self.logger.error(f"Language mapping error: {e}. Check if the language name is correct.")
            raise ValueError(f"Unsupported language name provided: {e}")

        try:
            self.logger.info(f"Attempting to translate text to {target_lang_code} (source: {source_lang_code or 'auto-detect'})...")
            result = self.client.translate_text(
                text,
                source_lang=source_lang_code,
                target_lang=target_lang_code
            )
            translated_content = result.text
            self.logger.info("Text successfully translated.")
            return translated_content
        except deepl.DeepLException as e:
            self.logger.error(f"DeepL translation failed: {e}")
            raise # Re-raise the exception after logging
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during DeepL translation: {e}")
            raise
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
            # Add more languages as needed
        }
