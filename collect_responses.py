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
    filename="output.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_file", type=str, default="./output_file.json",
                      help="Filename for where JSON output of responses will be stored")
    parser.add_argument("--total_responses", type=int, default=5,
                        help="The number of responses to collect per service")
    
    parser.add_argument("--preserve_output", type=bool, default=False,
                        help="If a matching output file exists, read in the existing data and append to it. Useful when combatting rate limits")
    
    parser.add_argument("--skip_gemini", type=bool, default=False,
                        help="Forcibly skip any calls to Gemini")
    parser.add_argument("--skip_chatgpt", type=bool, default=False,
                    help="Forcibly skip any calls to ChatGPT")
    parser.add_argument("--skip_deepseek", type=bool, default=False,
                    help="Forcibly skip any calls to DeepSeek")
    parser.add_argument("--skip_google_translate", type=bool, default=False,
                    help="Forcibly skip any calls to Google Translate")
  
    return parser.parse_args()

if __name__ == "__main__":
    load_dotenv()
    args = parse_args()

    output_json = None
    if args.preserve_output:
        try:
            with open(args.output_file, "r", encoding="utf-8") as file:
                output_json = json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found: {args.output_file}")
    else:
        output_json = generate_output_schema()

    if output_json is None:
        exit()

    skip_gemini = args.skip_gemini
    skip_chatgpt = args.skip_chatgpt
    skip_deepseek = args.skip_deepseek
    skip_google_translate = args.skip_google_translate
    total_responses = args.total_responses

    for language in LANGUAGES:
        language_name = language.replace(" ", "_").lower()

        for disaster in DISASTERS:
            disaster_name = disaster.replace("a ", "").replace(" ", "_")
            for prompt in PROMPT_FILES:
                prompt_name = prompt.replace("prompts/", "")
                
                while not skip_gemini and (len(output_json["gemini"][language_name][disaster_name][prompt_name]) < total_responses):
                    logger.info(f"Running {language_name}: {disaster_name}: {prompt_name}: Gemini")
                    gemini_output = chat_gemini(language=language, disaster=disaster, prompt=prompt, logger=logger)
                    if gemini_output is None:
                        skip_gemini = True
                    else:
                        output_json["gemini"][language_name][disaster_name][prompt_name].append(gemini_output)

                while not skip_chatgpt and (len(output_json["chatgpt"][language_name][disaster_name][prompt_name]) < total_responses):
                    logger.info(f"Running {language_name}: {disaster_name}: {prompt_name}: ChatGPT")
                    chatgpt_output = chat_chatgpt(language=language, disaster=disaster, prompt=prompt, logger=logger)
                    if chat_chatgpt is None:
                        skip_chatgpt = True
                    else:
                        output_json["chatgpt"][language_name][disaster_name][prompt_name].append(chatgpt_output)
                
                while not skip_deepseek and (len(output_json["deepseek"][language_name][disaster_name][prompt_name]) < total_responses):
                    logger.info(f"Running {language_name}: {disaster_name}: {prompt_name}: DeepSeek")
                    deepseek_output = chat_deepseek(language=language, disaster=disaster, prompt=prompt, logger=logger)
                    if deepseek_output is None:
                        skip_deepseek = True
                    else:
                        output_json["deepseek"][language_name][disaster_name][prompt_name].append(deepseek_output)

            while not skip_google_translate and (len(output_json["google_translate"][language_name][disaster_name]) < total_responses):
                logger.info(f"Running {language_name}: {disaster_name}: Google Translate")
                prompt_file = f"prompts/{disaster_name}.txt"
                google_translate_output = chat_google_translate(language=language, disaster=disaster, prompt=prompt_file, logger=logger)
                if google_translate_output is None:
                    skip_google_translate = True
                else:
                    output_json["google_translate"][language_name][disaster_name].append(google_translate_output)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)