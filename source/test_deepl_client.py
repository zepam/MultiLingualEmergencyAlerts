import sys
import os
import unittest
# We no longer need 'patch' or 'MagicMock' for live API calls,
# but keep 'deepl' for the actual client.
import deepl

# --- Import and load dotenv ---
# This line imports the load_dotenv function.
from dotenv import load_dotenv
# This line loads environment variables from a .env file into the script's environment.
load_dotenv()

# Ensure your DeepLClient and Client base class are imported correctly
# from clients.deepl_client import DeepLClient # If in a separate file
# from clients.client import Client # If Client is in a separate file

# --- Mocking the Client base class and logger for testing purposes ---
# We still need these simple mocks as the DeepLClient depends on them,
# but they don't interfere with actual DeepL API calls.
class MockClient:
    def __init__(self, key, logger):
        self.key = key
        self.logger = logger
        self.temperature = 0.7
        self.max_tokens = 100
        self.top_p = 0.9

class MockLogger:
    def info(self, message):
        print(f"INFO: {message}")
    def warning(self, message):
        print(f"WARNING: {message}")
    def error(self, message):
        print(f"ERROR: {message}")
    def debug(self, message):
        print(f"DEBUG: {message}")

# --- DeepLClient (copied from your Canvas for self-containment) ---
# In a real project, replace this with: from clients.deepl_client import DeepLClient
class Client(MockClient):
    pass

class DeepLClient(Client):
    """
    A client to interact with the DeepL Translation API.
    """
    def __init__(self, key: str, logger=None):
        super().__init__(key, logger)
        # Initialize the DeepL Translator client for actual API calls
        self.client = deepl.Translator(auth_key=self.key)
        self.logger.info("DeepLClient initialized for live API calls.")

    def translate(self, text: str, target_language: str, source_language: str = None) -> str:
        if not text:
            self.logger.warning("Attempted to translate empty text.")
            return ""

        try:
            target_lang_code = self.translation_map().get(target_language, target_language)
            if source_language:
                source_lang_code = self.translation_map().get(source_language, source_language)
            else:
                source_lang_code = None

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
        except deepl.DeepLError as e:
            self.logger.error(f"DeepL translation failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during DeepL translation: {e}")
            raise

    def translation_map(self) -> dict[str, str]:
        return {
            "English": "en-US",
            "Spanish": "es",
            "Arabic": "ar",
            "Haitian Creole": "fr",
            "Vietnamese": "vi",
            "Chinese (Traditional)": "zh",
            "Chinese (Simplified)": "zh",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Japanese": "ja",
            "Korean": "ko",
            "Portuguese": "pt-PT",
            "Russian": "ru",
            "Turkish": "tr",
            "Ukrainian": "uk",
            "Polish": "pl",
            "Dutch": "nl",
            "Indonesian": "id"
        }

# --- Test Cases using unittest framework for Live API Calls ---
class TestDeepLClientLive(unittest.TestCase):

    def setUp(self):
        """Set up for each test method for live API calls."""
        self.mock_logger = MockLogger()
        # Retrieve DeepL API Key from environment variable
        self.api_key = os.getenv("DEEPL_API_KEY")

        if not self.api_key:
            self.fail("DEEPL_API_KEY environment variable not set. Please set it in your .env file or directly.")

        self.client = DeepLClient(key=self.api_key, logger=self.mock_logger)

    def test_translate_english_to_spanish(self):
        """Test actual translation from English to Spanish."""
        input_text = "Hello, world!"
        target_lang = "Spanish"
        # DeepL's free tier can sometimes return different casing or punctuation.
        # We'll include the common variations for "Hello, world!" in Spanish.
        expected_options = ["Hola, mundo!", "Hola, Mundo!", "¡Hola, mundo!", "¡Hola, Mundo!"]

        translated_text = self.client.translate(input_text, target_lang)
        self.assertIsNotNone(translated_text)
        self.assertIn(translated_text, expected_options)
        print(f"Translated '{input_text}' to '{translated_text}' (Spanish)")


    def test_translate_french_to_german_with_codes(self):
        """Test actual translation from French to German using language codes."""
        input_text = "Bonjour le monde!"
        target_lang = "de"
        source_lang = "fr"
        expected_translation_prefix = "Hallo Welt" # DeepL often translates this as "Hallo Welt!" or "Hallo, Welt!"

        translated_text = self.client.translate(input_text, target_lang, source_lang)
        self.assertIsNotNone(translated_text)
        self.assertTrue(translated_text.startswith(expected_translation_prefix),
                        f"Expected '{expected_translation_prefix}' but got '{translated_text}'")
        print(f"Translated '{input_text}' to '{translated_text}' (German)")

    def test_translate_empty_text(self):
        """Test translation with empty input text (should return empty string)."""
        input_text = ""
        target_lang = "German"

        translated_text = self.client.translate(input_text, target_lang)
        self.assertEqual(translated_text, "")
        print("Tested empty text translation: returned empty string as expected.")

    def test_translate_unsupported_language_name_raises_error(self):
        """Test that an unsupported language name raises ValueError."""
        input_text = "This should fail."
        unsupported_lang = "Elvish"

        with self.assertRaises(ValueError) as cm:
            self.client.translate(input_text, unsupported_lang)
        self.assertIn("Unsupported target language", str(cm.exception))
        print(f"Tested unsupported language '{unsupported_lang}': caught expected ValueError.")

    # Note: For actual API calls, testing API errors would involve
    # temporarily invalidating the key or exceeding limits, which isn't
    # practical for automated tests. Mocking is better for that specific scenario.

# --- How to run the tests ---
if __name__ == '__main__':
    print("--- Running Live DeepL Client Tests ---")
    print("WARNING: This will make actual calls to the DeepL API and consume your quota.")
    print("Ensure you have set the DEEPL_API_KEY environment variable (e.g., in a .env file).")
    print("Execute from your terminal using: python -m unittest your_test_file_name.py")
    print("-" * 35)
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
