import json
import logging
import argparse

from dotenv import load_dotenv
from helpers import generate_output_schema, chat_gemini, chat_chatgpt, chat_google_translate, chat_deepseek

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

# Configure logging
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    filename="responses.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--predictions_dir', type=str, default='./predictions',
                      help='Directory containing prediction CSV files')


if __name__ == "__main__":
  load_dotenv()

  output_json = generate_output_schema()

  for language in LANGUAGES:
    language_name = language.replace(" ", "_").lower()

    for disaster in DISASTERS:
      disaster_name = disaster.replace("a ", "").replace(" ", "_")
      for prompt in PROMPT_FILES:
        prompt_name = prompt.replace("prompts/", "")
        
        logger.info(f"Running {language_name}: {disaster_name}: {prompt_name}: Gemini")
        gemini_output = chat_gemini(language=language, disaster=disaster, prompt=prompt)
        output_json["gemini"][language_name][disaster_name][prompt_name].append(gemini_output)

        logger.info(f"Running {language_name}: {disaster_name}: {prompt_name}: ChatGPT")
        chatgpt_output = chat_chatgpt(language=language, disaster=disaster, prompt=prompt)
        output_json["chatgpt"][language_name][disaster_name][prompt_name].append(chatgpt_output)
        
        logger.info(f"Running {language_name}: {disaster_name}: {prompt_name}: DeepSeek")
        deepseek_output = chat_deepseek(language=language, disaster=disaster, prompt=prompt)
        output_json["deepseek"][language_name][disaster_name][prompt_name].append(deepseek_output)

      logger.info(f"Running {language_name}: {disaster_name}: Google Translate")
      prompt_file = f"prompts/{disaster_name}.txt"
      google_translate_output = chat_google_translate(language=language, disaster=disaster, prompt=prompt_file)
      output_json["google_translate"][language_name][disaster_name].append(google_translate_output)

  with open('responses.json', 'w', encoding='utf-8') as f:
    json.dump(output_json, f, ensure_ascii=False, indent=4)
