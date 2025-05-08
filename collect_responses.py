import os
from dotenv import load_dotenv
from clients.gemini import GeminiClient
from clients.deepseek import DeepSeekClient
from clients.chatgpt import ChatGPTClient
from clients.cloud_translation import GoogleCloudTranslationClient

PROMPT_FILES = [
  "prompts/prompt_simple.txt",
  "prompts/prompt_chain_of_translation.txt",
  "prompts/prompt_one_shot.txt",
  "prompts/prompt_cross_lingual_alignment.txt",
  "prompts/prompt_persona.txt"
]

LANGUAGES = [
  "Spanish",
  "Arabic",
  "Mandarin",
  "Vietnamese",
  "Haitian Creole"
]

DISASTERS = [
  # standard disasters
  "a tornado",
  "a flood",
  "extreme wind",
  "a wildfire or fire",
  "a boil water notice",
  "a 911 outage",

  # new disasters
  "an alien invasion",
  "a meteor strike",
  "a nuclear power plant warning",
  "a volcanic eruption",
  "a contagious disease called SARD-26",
  "a dam break"
]

def chat_gemini():
  gemini_client = GeminiClient(key=os.getenv("GEMINI_API_KEY"))
  gemini_client.chat(
    prompt_files=["prompts/prompt_simple.txt"],
    language="Spanish",
    disaster="tornado"
  )

def chat_deepseek():
  deepseek_client = DeepSeekClient(key=os.getenv("OPENROUTER_API_KEY"))
  deepseek_client.chat(
    prompt_files=["prompts/prompt_simple.txt"],
    language="Spanish",
    disaster="tornado"
  )

def chat_chatgpt():
  chatgpt_client = ChatGPTClient(key=os.getenv("AZURE_OPENAI_API_KEY"), base_url=os.getenv("AZURE_OPENAI_ENDPOINT"), deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"))
  chatgpt_client.chat(
    prompt_files=["prompts/prompt_simple.txt"],
    language="Spanish",
    disaster="tornado"
  )

def chat_google_translate():
  # Note: this needs text and not a prompt because it's a literal translation
  google_translate_client = GoogleCloudTranslationClient()
  google_translate_client.chat(
    prompt_files=["prompts/prompt_simple.txt"],
    language="es", # Language needs to be ISO code
    disaster="tornado"
  )

if __name__ == "__main__":
  load_dotenv()

  # chat_gemini()
  # chat_deepseek()
  # chat_chatgpt()
  # chat_google_translate()
