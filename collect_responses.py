"""
collect_responses.py

This script iterates over API endpoints to Google Translate, Deepseek, ChatGPT, and Gemini in order to
request generation of multilingual emergency alerts.

Usage:
    python collect_responses.py

Example:
    python collect_responses.py --preserve_output=True --skip_chatgpt=True --skip_google_translate=True --skip_gemini=True

Functions:
    - parse_args: Parses arguments passed into the script
    - loop_responses: For a given language - disaster - prompt pairing, query all the APIs
    - collect_multilingual_responses: loop over every language, disaster, and prompt to call loop_responses
    - main: Does the thing. Outputs data to a JSON file
"""

import json
import logging
import argparse
import arabic_reshaper
from bidi.algorithm import get_display

from dotenv import load_dotenv
from helpers import generate_output_schema, chat_with_service

# prompts for multilingual responses to test prompt engineering. They are run for every service - language - disaster
ITERATIVE_PROMPT_FILES = [
  "prompts/prompt_simple.txt",
  "prompts/prompt_chain_of_translation.txt",
  "prompts/prompt_one_shot.txt",
  "prompts/prompt_cross_lingual_alignment.txt",
  "prompts/prompt_persona.txt"
]

# languages to evaluate
LANGUAGES = [
  "Spanish",
  "Arabic",
  "Chinese (Traditional)",
  "Vietnamese",
  "Haitian Creole"
]

STANDARD_DISASTERS = [
  "a flood",
  "extreme wind",
  "a fire",
  "a boil water notice",
  "a 911 outage",
]

# Configure logging
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    filename="output.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# TODO: --skip commands aren't parsing correctly, they are always True if there is any value passed
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

def loop_responses(skip_bool, service_name, language, disaster, prompt, logger, output_json, total_responses):
    language_name = language.replace(" ", "_").replace("(", "").replace(")", "").lower()
    disaster_name = disaster.replace("a ", "").replace(" ", "_")
    prompt_name = prompt.replace("prompts/", "")

    # google doesn't require a prompt to function
    if service_name == "google_translate":
        existing_response_list = output_json[service_name][language_name][disaster_name]
    else:
        existing_response_list = output_json[service_name][language_name][disaster_name][prompt_name]

    """
    While
        1) total_responses hasn't yet been reached
        2) the service should be run (not forcibly skipped by commandline argument or not skipped by a sequence of invalid API calls)
    keep querying service_name for the language - prompt - disaster combo
    """
    while not skip_bool and (len(existing_response_list) < total_responses):
        logger.info(f"Running {language_name}: {disaster_name}: {prompt_name}: {service_name}")
        output = chat_with_service(service_name, language=language, disaster=disaster, prompt=prompt, logger=logger)
        if output is None:
            skip_bool = True
        else:
            if language_name == "arabic":
                # make sure Arabic output is not broken and is left to right
                output = get_display(arabic_reshaper.reshape(output), base_dir = "R")
            existing_response_list.append(output)
    
    return skip_bool

def collect_multilingual_responses(logger, output_json, skip_gemini, skip_chatgpt, skip_deepseek, skip_google_translate, total_responses):
    for language in LANGUAGES:
        for disaster in STANDARD_DISASTERS:
            for prompt in ITERATIVE_PROMPT_FILES:
                skip_gemini = loop_responses(skip_gemini, "gemini", language, disaster, prompt, logger, output_json, total_responses)
                skip_chatgpt = loop_responses(skip_chatgpt, "chatgpt", language, disaster, prompt, logger, output_json, total_responses)
                skip_deepseek = loop_responses(skip_deepseek, "deepseek", language, disaster, prompt, logger, output_json, total_responses)

            # Google Translate needs to take an original template and translate directly
            disaster_name = disaster.replace("a ", "").replace(" ", "_")
            prompt = f"prompts/{disaster_name}.txt"
            skip_google_translate = loop_responses(skip_google_translate, "google_translate", language, disaster, prompt, logger, output_json, total_responses)

            # Direct translations also need a short description and the original template
            prompt = f"prompts/translate_{disaster_name}.txt"
            skip_gemini = loop_responses(skip_gemini, "gemini", language, disaster, prompt, logger, output_json, total_responses)
            skip_chatgpt = loop_responses(skip_chatgpt, "chatgpt", language, disaster, prompt, logger, output_json, total_responses)
            skip_deepseek = loop_responses(skip_deepseek, "deepseek", language, disaster, prompt, logger, output_json, total_responses)


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

    collect_multilingual_responses(logger, output_json, skip_gemini, skip_chatgpt, skip_deepseek, skip_google_translate, total_responses)

    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)