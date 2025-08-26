"""
evaluation.py

This script evaluates generated text outputs against reference texts using a variety of metrics,
including ROUGE, BLEU, BERTScore, and COMET. It supports multilingual evaluation and can output
results to a CSV file for further analysis.

Usage:
    python evaluation.py <generated_file.json> <reference_file.json> --output_csv <results.csv>

Arguments:
    generated_file.json   Path to the JSON file containing generated texts.
    reference_file.json   Path to the JSON file containing reference (gold standard) texts.
    --output_csv          (Optional) Path to save the evaluation results as a CSV file.
    --service_name        (Optional) Evaluate only this one service - deepseek, google_translate, chatgpt, gemini

Dependencies: evaluate, pandas, tqdm, argparse, json, re, time, sacrebleu

Example:
    python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results.csv
    python evaluation.py output_file.json data/evaluation_gold_standards.json --output_csv results_google_translate.csv --service_name google_translate

"""

# have this at the top to supress warnings from the imports because it's annoying
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ruff: noqa: E402
import pandas as pd
import argparse
import json
from tqdm import tqdm
import time
import re
import logging
import os
import torch
#from comet import download_model, load_from_checkpoint

from evaluate import load
from sacrebleu.tokenizers.tokenizer_spm import Flores101Tokenizer
from sacrebleu.tokenizers.tokenizer_zh import TokenizerZh
from clients.translation_map import TRANSLATION_MAP

torch.set_float32_matmul_precision('medium')
torch.cuda.empty_cache()

# Optional: psutil for more accurate memory logging
try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="evaluation.log",
    filemode="a",
    force=True
)

logger = logging.getLogger(__name__)

def log_memory_usage(note=""):
    """Log the current memory usage of the process."""
    if _HAS_PSUTIL:
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / 1024 ** 2  # in MB
        logger.info(f"MEMORY USAGE{f' ({note})' if note else ''}: {mem:.2f} MB")
    else:
        # Fallback: use resource module (less accurate, Unix only)
        try:
            import resource
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            logger.info(f"MEMORY USAGE{f' ({note})' if note else ''}: {mem} KB (resource module)")
        except ImportError:
            logger.info("psutil not installed and resource module unavailable; cannot log memory usage.")


class EvaluationTokenizer:
    def set_tokenizer_function(self, language):
        tokenizer = None
        match language:
            case "chinese_traditional":
                tokenizer = TokenizerZh()
            case _:
                tokenizer = Flores101Tokenizer()
        return tokenizer

    def __init__(self, language):
        self.tokenizer_function = self.set_tokenizer_function(language)    
    
    def tokenize(self, text):
        return self.tokenizer_function(text)

# used for ROUGE
def tokenizer_lambda(language):
    return lambda x: EvaluationTokenizer(language).tokenize(x)

def get_results_count(generated_path, service_name=None):
    """
    Collects results for a specific service or all services.
    - If service_name is provided, returns a list of results for that service.
    - If service_name is None, returns a dictionary of all results, grouped by service.
    """
    # If data is a path, load it
    if isinstance(generated_path, str):
        with open(generated_path, 'r') as f:
            json_data = json.load(f)
    else:
        json_data = generated_path

    if service_name:
        # Case 1: Get results for a single service
        if service_name in json_data:
            return get_results_count(json_data[service_name])
        print(f"Service '{service_name}' not found.") # only get here when if statement is false
        return 0
    elif isinstance(json_data, dict):
        return sum(get_results_count(v) for v in json_data.values())
    elif isinstance(json_data, list):
        return 1 if len(json_data) > 0 else 0
    else:
        return 0

def evaluate_generated_texts(generated_path, reference_path, output_csv=None, rouge=None, bleu=None, bertscore=None, comet=None, only_service=None):
    logger.info(f"Loading reference data from {reference_path}")
    with open(reference_path, "r", encoding="utf-8") as f:
        reference_data = json.load(f)

    logger.info(f"Loading prediction data from {generated_path}")
    with open(generated_path, "r", encoding="utf-8") as f:
        prediction_data = json.load(f)
    
    results = []

    # count iterations for progress bar
    if only_service:
        total = get_results_count(generated_path, service_name=only_service)
    else:
        total = get_results_count(generated_path)

    """
    we want to collect fine-tuned results that tell us:
    1) if prompt A better than prompt B
    2) if disaster A did better than disaster B
    3) if service A did better than service B
    4) if language A did better than language B

    so let's evaluate on a per-prompt level. We can then take the average to broaden the evaluation to larger categories like disaster, language
    iterate over every language - {disaster: reference_text} pair
    """
    with tqdm(total=total, desc="Evaluating prompts") as pbar:
        for service in prediction_data:
            if only_service and service != only_service:
                continue
            for language, values in reference_data.items():
                # Bleu doesn't take a tokenizer directly but rather a string matching a tokenizer
                if language == "chinese_traditional":
                    tokenizer_string = "zh"
                else:
                    tokenizer_string = "flores101"

                #evaluation_tokenizer = tokenizer_lambda(language)
                evaluation_tokenizer = (lambda tok: (lambda x: tok.tokenize(x)))(EvaluationTokenizer(language))

                # bertscore takes a language code indicating the language being passed in
                language_code = TRANSLATION_MAP.get(language, language)

                for disaster, gold_standards in values.items():
                    if (
                        service in prediction_data
                        and language in prediction_data[service]
                        and disaster in prediction_data[service][language]
                    ):
                        relevant_prompts = prediction_data[service][language][disaster]
                        
                        # chatgpt, deepseek, gemini
                        if isinstance(relevant_prompts, dict):
                            for prompt, predictions in relevant_prompts.items():
                                if not predictions:
                                    logger.warning(f"No predictions for {language}:{service}:{disaster}:{prompt}")
                                    continue
                                # Extract the "text" field from each prediction dict, if exists. Otherwise take entire response.
                                predictions_text = [pred["text"] if isinstance(pred, dict) and "text" in pred else pred for pred in predictions]
                                total_predictions = len(predictions)

                                # we have 5 predictions and one gold standard. Just make an array of the same gold standard 5 times
                                duplicated_gold_standards = [gold_standards["reference"]] * total_predictions

                                # try:
                                id_response = f"{service}:{language}:{disaster}:{prompt}"
                                logger.info(f"Evaluating {id_response} with {total_predictions} predictions")
                                rouge_result = rouge.compute(predictions=predictions_text, references=duplicated_gold_standards, tokenizer=evaluation_tokenizer)
                                bertscore_result = bertscore.compute(predictions=predictions_text, references=duplicated_gold_standards, lang=language_code)
                                bleu_result = bleu.compute(predictions=predictions_text, references=duplicated_gold_standards, tokenize=tokenizer_string)
                                comet_result = comet.compute(predictions=predictions_text, references=duplicated_gold_standards, sources=[gold_standards["source"]] * total_predictions)
                                #comet_result = calculate_comet(comet, gold_standards, predictions_text, duplicated_gold_standards)

                                result = gather_results(service, language, disaster, prompt, rouge_result, bertscore_result, bleu_result, comet_result)
                                results.append(result)
                                    
                                # except Exception as e:
                                #     logger.error(f"[Error on line {id_response}] {e}", exc_info=True)
                                #     print(f"[Error on line {id_response}] {e}")
                                #     continue
                                pbar.update(1)
                                # Log memory usage every XX prompts
                                if pbar.n % 5 == 0:
                                    log_memory_usage(f"After {pbar.n} prompts")

                        # google translate
                        elif isinstance(relevant_prompts, list):
                            # If relevant_prompts is a list, we assume it's a single prediction
                            predictions = relevant_prompts
                            if predictions:
                                # Extract the "text" field from each prediction dict
                                predictions_text = [pred["text"] if isinstance(pred, dict) and "text" in pred else pred for pred in predictions]

                                # google translate tranlates everything directly, even our standard variables. Let's parse out everything within square brackets to not penalize for that
                                formatted_predictions = []
                                for prediction in predictions_text:
                                    formatted_predictions.append(re.sub(r'\[.*?\]', '', prediction))

                                total_predictions = len(formatted_predictions)
                                # apply the same treatment to the gold standards
                                duplicated_gold_standards = [re.sub(r'\[.*?\]', '', gold_standards["reference"])] * total_predictions

                                # try:        
                                id_response = f"{service}:{language}:{disaster}"
                                logger.info(f"Evaluating {id_response} with {total_predictions} predictions")
                                rouge_result = rouge.compute(predictions=formatted_predictions, references=duplicated_gold_standards, tokenizer=evaluation_tokenizer)
                                bertscore_result = bertscore.compute(predictions=formatted_predictions, references=duplicated_gold_standards, lang=language_code)
                                bleu_result = bleu.compute(predictions=formatted_predictions, references=duplicated_gold_standards, tokenize=tokenizer_string)
                                comet_result = calculate_comet(comet, gold_standards, predictions_text, duplicated_gold_standards)
                                #result = gather_results(service, language, disaster, "N/A", rouge_result, bertscore_result, bleu_result, comet_result)
                                result = gather_results(service, language, disaster, "N/A", rouge_result, bertscore_result, bleu_result, comet_result)
                                results.append(result)
                                # except Exception as e:
                                #     logger.error(f"[Error on line {id_response}] {e}", exc_info=True)
                                #     print(f"[Error on line {id_response}] {e}")
                                #     continue
                                pbar.update(1)
                                # Log memory usage every 5 prompts
                                if pbar.n % 5 == 0:
                                    log_memory_usage(f"After {pbar.n} prompts")
                #TODO  save results until now instead of at the end

    
    df = pd.DataFrame(results)

    if output_csv:
        df.to_csv(output_csv, index=False)
        logger.info(f"Results saved to: {output_csv}")
        print(f"Results saved to: {output_csv}")
    # Log memory usage at the end
    log_memory_usage("At end of evaluation")

    return df

def calculate_comet(comet, gold_standards, predictions_text, duplicated_gold_standards):
    comet_data = [
        {"src": src, "mt": pred, "ref": ref}
        for src, pred, ref in zip(gold_standards["source"], predictions_text, duplicated_gold_standards)
    ]
    return comet.predict(comet_data, batch_size=1, gpus=1)

# def find_language_code(language):
#     language_code = None
#     match language:
#         case "chinese_traditional":
#             language_code = "zh"
#         case "arabic":
#             language_code = "ar"
#         case "vietnamese":
#             language_code = "vi"
#         case "haitian_creole":
#             language_code = "ht"
#         case "spanish":
#             language_code = "es"
#     return language_code

def gather_results(service, language, disaster, prompt, rouge_result, bertscore_result, bleu_result, comet_result):
    return {
        "SERVICE": service,
        "LANGUAGE": language,
        "DISASTER": disaster,
        "PROMPT": prompt, 
        "ROUGE-1": rouge_result["rouge1"],
        "ROUGE-2": rouge_result["rouge2"],
        "ROUGE-L": rouge_result["rougeL"],
        "BLEU": bleu_result["score"],
        "BERTScore_P": bertscore_result["precision"][0],
        "BERTScore_R": bertscore_result["recall"][0],
        "BERTScore_F1": bertscore_result["f1"][0],
        #"COMET": 0
        "COMET": comet_result["mean_score"]
       #"COMET": comet_result.system_score
    }

# def load_comet_model(model_name="eamt22-prune-comet-da"):
#     cache_dir = os.path.expanduser("~/.cache/torch/unbabel_comet")
#     model_dir = os.path.join(cache_dir, model_name, "checkpoints")
#     model_path = os.path.join(model_dir, "model.ckpt")

#     # Download if missing
#     if not os.path.exists(model_path):
#         print(f"Downloading {model_name}...")
#         model_path = download_model(model_name)

#     # Load from checkpoint
#     return load_from_checkpoint(model_path).to("cuda").half()

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description="Evaluate generated texts against reference texts")
    parser.add_argument("generated_path", help="Path generated text file")
    parser.add_argument("reference_path", help="Path reference text file")
    parser.add_argument("--output_csv", help="Path to output CSV file", default=None)
    parser.add_argument("--service_name", help="Only evaluate this service (chatgpt, deepseek, gemini, google_translate)")
    args = parser.parse_args()

    logger.info("**************************************************")
    logger.info("**************************************************")
    # logger.info(torch.cuda.is_available())
    # logger.info(torch.cuda.get_device_name(0))
    # print(torch.cuda.is_available())      # should be True
    # print(torch.cuda.get_device_name(0))  # your GPU name

    logger.info("Starting evaluation script")
    logger.info(f"Generated file: {args.generated_path}")
    logger.info(f"Reference file: {args.reference_path}")
    logger.info(f"Output CSV: {args.output_csv}")

    # Log memory usage at the start
    log_memory_usage("At start of script")

    # Load metrics
    logger.info("Loading metrics")
    rouge = load("rouge")
    bleu = load("sacrebleu")
    bertscore = load("bertscore")
    comet = load("comet")
    #comet = load_comet_model("wmt21-comet-qe-mqm")

    # load native comet
    # model_path = download_model("wmt21-comet-qe-mqm")
    # comet = load_from_checkpoint(model_path).to("cuda")

    # If output_csv is specified, put it in the results folder
    output_path = None
    if args.output_csv:
        output_path = os.path.join("results/", os.path.basename(args.output_csv))
    
    df = evaluate_generated_texts(
        args.generated_path,
        args.reference_path,
        output_path,
        rouge,
        bleu,
        bertscore,
        comet,
        only_service=args.service_name
    )

    # Print the DataFrame
    logger.info("Evaluation complete.")

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Evaluation completed in {elapsed_time:.2f} seconds.")
    print(f"Evaluation completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()