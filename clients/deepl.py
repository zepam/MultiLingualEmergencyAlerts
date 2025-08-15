import deepl
from clients.client import Client # Assuming 'Client' is your base class

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

        Raises:
            deepl.DeepLError: If the DeepL API call fails for any reason
                              (e.g., invalid key, rate limit, network issues).
            ValueError: If an unsupported language name is provided.
        """
        if not text:
            self.logger.warning("Attempted to translate empty text.")
            return ""

        # Map friendly language names to DeepL language codes

        target_language_code = self.translation_map().get(target_language, target_language)
        if source_language:
            source_language_code = self.translation_map().get(source_language, source_language)
        else:
            source_language_code = None

        # Validate if the mapped language code is a valid DeepL target language
        # This is a basic check; full validation against DeepL's supported list
        # might require fetching supported languages via the API.
        if target_language_code not in self.translation_map().values() and len(target_language_code) > 2:
            # If it's not in our map and not a short code, assume it's an unrecognized name
            # A more robust check would involve `self.client.get_target_languages()`
            # but for simplicity, we rely on the map or direct code.
            self.logger.error(f"Unsupported target language provided: {target_language}")
            raise ValueError(f"Unsupported target language: {target_language}. Please use a supported name or exact DeepL code.")
        if source_language_code and source_language_code not in self.translation_map().values() and len(source_language_code) > 2:
                self.logger.error(f"Unsupported source language provided: {source_language}")
                raise ValueError(f"Unsupported source language: {source_language}. Please use a supported name or exact DeepL code.")

        #try:
            #self.logger.info(f"Attempting to translate text to {target_language_code} (source: {source_language_code or 'auto-detect'})...")
            # Translate the text using the DeepL client
            # The 'source_language' parameter is optional; if not provided, DeepL detects it.
        result = self.client.translate_text(
            text,
            source_language=source_language_code,
            target_language=target_language_code
        )
        translated_content = result.text
            #self.logger.info("Text successfully translated.")
        return translated_content
        # except deepl.DeepLError as e:
        #     self.logger.error(f"DeepL translation failed: {e}")
        #     raise # Re-raise the exception after logging, for external handling
        # except Exception as e:
        #     self.logger.error(f"An unexpected error occurred during DeepL translation: {e}")
        #     raise # Re-raise any other unexpected exceptions

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
            "Haitian Creole": "fr", # DeepL does not directly support Haitian Creole, using French as a fallback
            "Vietnamese": "vi",
            "Chinese (Traditional)": "zh", # DeepL uses 'zh' for both Simplified and Traditional, often defaulting to Simplified
            "Chinese (Simplified)": "zh",
            # Add more languages as needed, checking DeepL's official documentation
        }
