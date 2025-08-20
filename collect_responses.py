"""
collect_responses.py

This script iterates over API endpoints to Google Translate, Deepseek, ChatGPT, and Gemini in order to
request generation of multilingual emergency alerts.

Example:
    python collect_responses.py --preserve_output --skip_chatgpt --skip_deepseek --skip_gemini --skip_google_translate --skip_deepL

Functions:
    - parse_args: Parses arguments passed into the script
    - loop_responses: For a given language - disaster - prompt pairing, query all the APIs
    - collect_multilingual_responses: loop over every language, disaster, and prompt to call loop_responses
    - main: Does the thing. Outputs data to a JSON file

Flags:
    --preserve_output: If a matching output file exists, read in the existing data and append to it.
    --skip_gemini: Forcibly skip any calls to Gemini
    --skip_chatgpt: Forcibly skip any calls to ChatGPT
    --skip_deepseek: Forcibly skip any calls to DeepSeek
    --skip_google_translate: Forcibly skip any calls to Google Translate
    --skip_deepL: Forcibly skip any calls to DeepL Translator
"""

import json
import logging
import argparse
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import date

from dotenv import load_dotenv
from source.helpers import chat_with_service

logging.getLogger("deepL").setLevel(logging.WARNING)

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
  "Haitian Creole",
  "Russian",
  "Ukrainian"
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

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_file", type=str, default="./output_file.json",
                      help="Filename for where JSON output of responses will be stored")
    parser.add_argument("--total_responses", type=int, default=5,
                        help="The number of responses to collect per service")
    
    parser.add_argument("--preserve_output", action='store_true',
                        help="If a matching output file exists, read in the existing data and append to it. Useful when combatting rate limits")
    
    parser.add_argument("--skip_gemini", action="store_true", default=False,
                        help="Forcibly skip any calls to Gemini")
    parser.add_argument("--skip_chatgpt", action='store_true',
                        help="Forcibly skip any calls to ChatGPT")
    parser.add_argument("--skip_deepseek", action='store_true', default=False,
                    help="Forcibly skip any calls to DeepSeek")
    parser.add_argument("--skip_google_translate", action='store_true', default=False,
                    help="Forcibly skip any calls to Google Translate")
    parser.add_argument("--skip_deepL", action='store_true', default=False,
                help="Forcibly skip any calls to DeepL Translator")
  
    return parser.parse_args()

def save_output_json(output_json, output_file, logger):
    
    """Saves the output JSON data to a specified file.

    This function writes the current state of the output JSON to disk and logs the result. If saving fails, an error is logged.

    Args:
        output_json (dict): The output data to be saved.
        output_file (str): The filename where the JSON will be stored.
        logger (logging.Logger): Logger for logging progress and errors.

    Returns:
        None
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_json, f, ensure_ascii=False, indent=4, default=str)
            #logger.info(f"Progress saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save progress: {e}")

def loop_responses(skip_bool, service_name, language, disaster, prompt_file_path, logger, output_json, output_filename, total_responses):
    """Queries a language model or translation service for a multilingual emergency alert response.

    This function checks if a response for the current month already exists, and if not,
    requests a new response from the specified service.
    The response is then appended to the output JSON with the current date.

    Args:
        skip_bool (bool): Whether to skip querying the service.
        service_name (str): The name of the service to query.
        language (str): The target language for the alert.
        disaster (str): The disaster scenario for the alert.
        prompt_file_path (str): The prompt file to use for generation.
        logger (logging.Logger): Logger for logging progress and errors.
        output_json (dict): The output data structure to store responses.
        total_responses (int): The number of responses to collect per service.

    Returns:
        bool: The updated skip status for the service.
    """
    if skip_bool:
        return skip_bool
    
    language_name = language.replace(" ", "_").replace("(", "").replace(")", "").lower()
    disaster_name = disaster.replace("a ", "").replace(" ", "_")
    prompt_name = prompt_file_path.replace("prompts/", "")

    # update json schema if needed
    prepare_response_schema(service_name, logger, output_json, language_name, disaster_name)

    if service_name in ["google_translate", "deepL"]:
        existing_response_list = output_json[service_name][language_name][disaster_name]
    else:
        if prompt_name not in output_json[service_name][language_name][disaster_name]:
            output_json[service_name][language_name][disaster_name][prompt_name] = []
        existing_response_list = output_json[service_name][language_name][disaster_name][prompt_name]

    # save all that work
    save_output_json(output_json, output_filename, logger)

    # Check if we already have a response for this week
    timely_response_exists = check_for_weeks_response(existing_response_list)
    
    """
    Only get a new response if:
    1) We don't have one for this week yet
    2) the service should be run (not forcibly skipped by commandline argument)
    """
    if not timely_response_exists:
        #logger.info(f"Running {service_name}: {language_name}: {disaster_name}: {prompt_name}")

        #try:
        output = chat_with_service(service_name, language=language, disaster=disaster, prompt_file_path=prompt_file_path, logger=logger)

        # TODO You must also ensure that chat_with_service is updated to return None (not an empty string) on failure, and only return an empty string if that is a valid response. If chat_with_service is in another file, update its error handling accordingly.
        if not output:      # the deepL client returns an empty string if it fails, need to exclude it
            logger.warning(f"{service_name} returned None for {language_name}:{disaster_name}:{prompt_name}")
            return True  # Skip this service going forward
        
        if language_name == "arabic":
            # make sure Arabic output is not broken and is left to right
            output = get_display(arabic_reshaper.reshape(output), base_dir = "R")
            
        # Store response with today's date
        response_with_date = {
            "text": output,
            "date": date.today().isoformat()
        }
        existing_response_list.append(response_with_date)
        return False  # Return false if a new response was added
        
    else:
        logger.info(f"Skipping {service_name} : {language_name} : {disaster_name} : {prompt_name}  - already have response for this week")
    
    return False 

def check_for_weeks_response(existing_response_list):
    today = date.today()
    timely_response_exists = False
    
    # check if there is already a response for this week (same year and same ISO week number)
    for response in existing_response_list:
        if isinstance(response, dict):
            response_date = response.get('date', '')
        else:
            response_date = ''
        if response_date:
            response_date_obj = date.fromisoformat(response_date)
            if (response_date_obj.year == today.year and 
                response_date_obj.isocalendar()[1] == today.isocalendar()[1]):
                timely_response_exists = True
                break
    return timely_response_exists

def prepare_response_schema(service_name, logger, output_json, language_name, disaster_name):
    if service_name not in output_json:
        output_json[service_name] = {}
        logger.info(f"Adding {service_name} to output JSON")

    if language_name not in output_json[service_name]:
        output_json[service_name][language_name] = {}
        logger.info(f"Adding {service_name} - {language_name} in output JSON")

    if disaster_name not in output_json[service_name][language_name]:
        if service_name in ["google_translate", "deepL"]:
            output_json[service_name][language_name][disaster_name] = []
            logger.info(f"Adding {service_name} - {language_name} - {disaster_name} in output JSON")
        else:
            output_json[service_name][language_name][disaster_name] = {}
            logger.info(f"Adding {service_name} - {language_name} - {disaster_name} in output JSON with prompts")# return true (skipped) if a response already exists


#TODO: skip the service if it cannot connect
def collect_multilingual_responses(logger, output_json, skip_gemini, skip_chatgpt, skip_deepseek, skip_google_translate, skip_deepL, total_responses, output_filename):
    for language in LANGUAGES:
        for disaster in STANDARD_DISASTERS:
            for prompt in ITERATIVE_PROMPT_FILES:
                if not skip_gemini:  # yes, this looks redundant, but we want to skip Gemini even checking (logging) if the flag is set
                    new_skip_gemini = loop_responses(skip_gemini, "gemini", language, disaster, prompt, logger, output_json, output_filename, total_responses)
                    if not new_skip_gemini:  # If we successfully made an API call
                        save_output_json(output_json, output_filename, logger)
                if not skip_chatgpt:
                    new_skip_chatgpt = loop_responses(skip_chatgpt, "chatgpt", language, disaster, prompt, logger, output_json, output_filename, total_responses)
                    if not new_skip_chatgpt:  # If we successfully made an API call
                        save_output_json(output_json, output_filename, logger)
                if not skip_deepseek:
                    new_skip_deepseek = loop_responses(skip_deepseek, "deepseek", language, disaster, prompt, logger, output_json, output_filename, total_responses)
                    if not new_skip_deepseek:  # If we successfully made an API call
                        save_output_json(output_json, output_filename, logger)

            # Google Translate needs to take an original template and translate directly
            disaster_name = disaster.replace("a ", "").replace(" ", "_")
            prompt = f"prompts/{disaster_name}.txt"
            if not skip_google_translate:
                new_skip_google_translate = loop_responses(skip_google_translate, "google_translate", language, disaster, prompt, logger, output_json, output_filename, total_responses)
                if not new_skip_google_translate:
                    save_output_json(output_json, output_filename, logger)
            if not skip_deepL:
                new_skip_deepL = loop_responses(skip_deepL, "deepL", language, disaster, prompt, logger, output_json, output_filename, total_responses)
                if not new_skip_deepL:
                    save_output_json(output_json, output_filename, logger)

            # Direct translations also need a short description and the original template
            prompt = f"prompts/translate_{disaster_name}.txt"
            skip_gemini = loop_responses(skip_gemini, "gemini", language, disaster, prompt, logger, output_json, output_filename, total_responses)
            skip_chatgpt = loop_responses(skip_chatgpt, "chatgpt", language, disaster, prompt, logger, output_json, output_filename, total_responses)
            skip_deepseek = loop_responses(skip_deepseek, "deepseek", language, disaster, prompt, logger, output_json, output_filename, total_responses)


if __name__ == "__main__":
    load_dotenv()
    args = parse_args()

    output_json = None

    try:
        with open(args.output_file, "r", encoding="utf-8") as file:
            output_json = json.load(file)
        logger.info(f"Preserved existing output from {args.output_file}")
    except FileNotFoundError:
        logger.error(f"Output file {args.output_file} not found. Please create the file or specify the correct path.")
        exit(1)

    if output_json is None:
        exit()

    skip_gemini = args.skip_gemini
    skip_chatgpt = args.skip_chatgpt
    skip_deepseek = args.skip_deepseek
    skip_google_translate = args.skip_google_translate
    skip_deepL = args.skip_deepL
    total_responses = args.total_responses

    logger.info("**************************************************")
    logger.info("**************************************************")

    collect_multilingual_responses(logger, output_json, skip_gemini, skip_chatgpt, skip_deepseek, skip_google_translate, skip_deepL, total_responses, args.output_file)

    # with open(args.output_file, 'w', encoding='utf-8') as f:
    #     json.dump(output_json, f, ensure_ascii=False, indent=4)

    # just in case there is anything left
    save_output_json(output_json, args.output_file, logger)