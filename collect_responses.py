import os
import json
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

TEMPLATE_FILES = [
  "prompts/fire.txt",
  "prompts/extreme_wind.txt",
  "prompts/flood.txt",
  "prompts/boil_water_notice.txt",
  "prompts/911_outage.txt"
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
  "a flood",
  "extreme wind",
  "a fire",
  "a boil water notice",
  "a 911 outage",

  # new disasters
  #"an alien invasion",
  #"a meteor strike",
  #"a nuclear power plant meltdown",
  #"a solar flare",
  #"a contagious disease called SARD-26",
]

def chat_gemini(language, disaster, prompt):
  gemini_client = GeminiClient(key=os.getenv("GEMINI_API_KEY"))
  return gemini_client.chat(
    prompt_file=prompt,
    language=language,
    disaster=disaster
  )

def chat_deepseek(language, disaster, prompt):
  deepseek_client = DeepSeekClient(key=os.getenv("OPENROUTER_API_KEY"))
  return deepseek_client.chat(
    prompt_file=prompt,
    language=language,
    disaster=disaster
  )

def chat_chatgpt(language, disaster, prompt):
  chatgpt_client = ChatGPTClient(key=os.getenv("AZURE_OPENAI_API_KEY"), base_url=os.getenv("AZURE_OPENAI_ENDPOINT"), deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"))
  return chatgpt_client.chat(
    prompt_file=prompt,
    language=language,
    disaster=disaster
  )

def chat_google_translate(language, disaster, prompt):
  google_translate_client = GoogleCloudTranslationClient()
  return google_translate_client.chat(
    prompt_file=prompt,
    language=language,
    disaster=disaster
  )

if __name__ == "__main__":
  load_dotenv()

  prompt_breakdown_json = {
    "prompt_simple.txt": [],
    "prompt_persona.txt": [],
    "prompt_one_shot.txt": [],
    "prompt_cross_lingual_alignment.txt": [],
    "prompt_chain_of_translation.txt": []
  }

  breakdown_json = {
    "spanish": {
      "flood": { **prompt_breakdown_json },
      "extreme_wind": { **prompt_breakdown_json },
      "fire": { **prompt_breakdown_json },
      "boil_water_notice": { **prompt_breakdown_json },
      "911 outage": { **prompt_breakdown_json }
    },
    "haitian_creole": {
      "flood": { **prompt_breakdown_json },
      "extreme_wind": { **prompt_breakdown_json },
      "fire": { **prompt_breakdown_json },
      "boil_water_notice": { **prompt_breakdown_json },
      "911_outage": { **prompt_breakdown_json }
    },
    "vietnamese": {
      "flood": { **prompt_breakdown_json },
      "extreme_wind": { **prompt_breakdown_json },
      "fire": { **prompt_breakdown_json },
      "boil_water_notice": { **prompt_breakdown_json },
      "911_outage": { **prompt_breakdown_json }
    },
    "arabic": {
      "flood": { **prompt_breakdown_json },
      "extreme_wind": { **prompt_breakdown_json },
      "fire": { **prompt_breakdown_json },
      "boil_water_notice": { **prompt_breakdown_json },
      "911_outage": { **prompt_breakdown_json }
    },
    "mandarin": {
      "flood": { **prompt_breakdown_json },
      "extreme_wind": { **prompt_breakdown_json },
      "fire": { **prompt_breakdown_json },
      "boil_water_notice": { **prompt_breakdown_json },
      "911_outage": { **prompt_breakdown_json }
    }
  }

  output_json = {
    "chatgpt": { **breakdown_json },
    "gemini": { **breakdown_json },
    "deepseek": { **breakdown_json },
    "google_translate": {
      "spanish": { 
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      },
      "arabic": {
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      },
      "mandarin": {
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      },
      "vietnamese": {
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      },
      "haitian_creole": {
        "flood": [],
        "extreme_wind": [],
        "fire": [],
        "boil_water_notice": [],
        "911_outage": []
      }
    }
  }

  for language in ["Haitian Creole"]: # LANGUAGES
    if language == "Haitian Creole":
      language_name = "haitian_creole"
    else:
      language_name = language.lower()

    for disaster in ["a fire"]: # DISASTERS
      disaster_name = disaster.replace("a ", "").replace(" ", "_")
      for prompt in ["prompts/prompt_simple.txt"]: # PROMPT_FILES
        prompt_name = prompt.replace("prompts/", "")
        
        gemini_output = chat_gemini(language=language, disaster=disaster, prompt=prompt)
        output_json["gemini"][language_name][disaster_name][prompt_name].append(gemini_output)

        chatgpt_output = chat_chatgpt(language=language, disaster=disaster, prompt=prompt)
        output_json["chatgpt"][language_name][disaster_name][prompt_name].append(chatgpt_output)

        deepseek_output = chat_deepseek(language=language, disaster=disaster, prompt=prompt)
        output_json["deepseek"][language_name][disaster_name][prompt_name].append(deepseek_output)

      prompt_file = f"prompts/{disaster_name}.txt"

      google_translate_output = chat_google_translate(language=language, disaster=disaster, prompt=prompt_file)
      output_json["google_translate"][language_name][disaster_name].append(google_translate_output)

  with open('responses.json', 'w', encoding='utf-8') as f:
    json.dump(output_json, f, ensure_ascii=False, indent=4)
