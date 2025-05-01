from google import genai
import pdb
import datasets


# Client to interact with the Gemini API
class GeminiClient:
    def __init__(self, key):
        self.key = key
        self.model = "gemini-2.0-flash"

    def chat(self, prompt_file):
        with open(prompt_file, "r") as file:
            breakpoint()

            prompt_text = file.read()
            prompt_text = prompt_text.replace("{DISASTER}", "tornado")

