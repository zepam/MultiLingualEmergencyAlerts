"""
Evaluation script for multilingual emergency alert translations

This script evaluates machine-generated translations against reference texts using 
various NLP metrics. It processes JSON files containing translations from different
services (like ChatGPT, DeepSeek, Gemini, Google Translate) and evaluates them using:

    - ROUGE (1, 2, L): Measures overlap of n-grams between generated and reference texts
    - BLEU: Measures precision of n-grams in generated text compared to references
    - BERTScore: Computes token similarity using contextual embeddings
    - COMET: Neural-based MT evaluation metric
    - CHRF: Character-level n-gram F-score

The script handles different translation service output formats and supports
language-specific tokenization. Results are saved to a CSV file for further analysis.

Usage:
    python evaluation.py <generated_path> <reference_path> [--output_csv OUTPUT_CSV] [--service_name SERVICE]

Arguments:
    generated_path    Path to the JSON file containing generated translations
    reference_path    Path to the JSON file containing reference translations
    --output_csv      Path to save the evaluation results as CSV (optional)
    --service_name    Only evaluate translations from this service (optional)
Returns:
    DataFrame containing evaluation results for each translation

The script produces detailed logs in logs/evaluation.log and can evaluate
on a per-prompt level to enable analysis by prompt, disaster type, service, or language.

NOTE: This script requires significant resources. Consider using the run_all_evaluations.sh script. This 
will run each evaluation sequentially then concatenate the results.
"""

# have this at the top to supress warnings from the imports because they're annoying
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import logging
logging.getLogger("pytorch_lightning").setLevel(logging.WARNING)

# ruff: noqa: E402
import pandas as pd
import argparse
import json
from tqdm import tqdm
import time
import re
import os
# import torch

from evaluate import load
from sacrebleu.tokenizers.tokenizer_spm import Flores101Tokenizer
from sacrebleu.tokenizers.tokenizer_zh import TokenizerZh
from clients.translation_map import TRANSLATION_MAP

# torch.set_float32_matmul_precision('medium')
# torch.cuda.empty_cache()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/evaluation.log",
    filemode="a",
    force=True
)

logger = logging.getLogger(__name__)

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
        logger.warning(f"Service '{service_name}' not found.") # only get here when if statement is false
        return 0
    elif isinstance(json_data, dict):
        return sum(get_results_count(v) for v in json_data.values())
    elif isinstance(json_data, list):
        return 1 if len(json_data) > 0 else 0
    else:
        return 0

def evaluate_generated_texts(generated_path,reference_path, output_csv=None, rouge=None,
                             bleu=None, bertscore=None, comet=None, chrf=None, only_service=None):
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

                                # Extract date field if present
                                dates = [pred.get("date") if isinstance(pred, dict) and "date" in pred else None for pred in predictions]
                                # If all dates are the same, use that date, else None
                                date = dates[0] if dates and all(d == dates[0] for d in dates) else None

                                # try:
                                id_response = f"{service}:{language}:{disaster}:{prompt}"
                                logger.info(f"Evaluating {id_response} with {total_predictions} predictions")
                                rouge_result = rouge.compute(predictions=predictions_text, references=duplicated_gold_standards, tokenizer=evaluation_tokenizer)
                                bertscore_result = bertscore.compute(predictions=predictions_text, references=duplicated_gold_standards, lang=language_code)
                                bleu_result = bleu.compute(predictions=predictions_text, references=duplicated_gold_standards, tokenize=tokenizer_string)
                                comet_result = comet.compute(predictions=predictions_text, references=duplicated_gold_standards, sources=[gold_standards["source"]] * total_predictions)
                                chrf_result = chrf.compute(predictions=predictions_text, references=duplicated_gold_standards, word_order=2, lowercase=True)
                                result = gather_results(service, language, disaster, prompt, rouge_result, bertscore_result, bleu_result, comet_result, chrf_result, date=date)
                                results.append(result)
                                    
                                pbar.update(1)

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

                                # Extract date field if present
                                dates = [pred.get("date") if isinstance(pred, dict) and "date" in pred else None for pred in predictions]
                                # If all dates are the same, use that date, else None
                                date = dates[0] if dates and all(d == dates[0] for d in dates) else None

                                # try:        
                                id_response = f"{service}:{language}:{disaster}"
                                logger.info(f"Evaluating {id_response} with {total_predictions} predictions")
                                rouge_result = rouge.compute(predictions=formatted_predictions, references=duplicated_gold_standards, tokenizer=evaluation_tokenizer)
                                bertscore_result = bertscore.compute(predictions=formatted_predictions, references=duplicated_gold_standards, lang=language_code)
                                bleu_result = bleu.compute(predictions=formatted_predictions, references=duplicated_gold_standards, tokenize=tokenizer_string)
                                comet_result = comet.compute(predictions=predictions_text, references=duplicated_gold_standards, sources=[gold_standards["source"]] * total_predictions)
                                chrf_result = chrf.compute(predictions=predictions_text, references=duplicated_gold_standards, word_order=2, lowercase=True)
                                result = gather_results(service, language, disaster, "N/A", rouge_result, bertscore_result, bleu_result, comet_result, chrf_result, date=date)
                                results.append(result)

                                pbar.update(1)
    df = pd.DataFrame(results)

    if output_csv:
        df.to_csv(output_csv, index=False)
        logger.info(f"Results saved to: {output_csv}")
        print(f"Results saved to: {output_csv}")
    return df


def gather_results(service, language, disaster, prompt, rouge_result, bertscore_result, bleu_result, comet_result, chrf_result, date=None):
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
        "COMET": comet_result["mean_score"],
        "CHRF": chrf_result["score"],
        "DATE": date
    }


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

    logger.info("Starting evaluation script")
    logger.info(f"Generated file: {args.generated_path}")
    logger.info(f"Reference file: {args.reference_path}")
    logger.info(f"Output CSV: {args.output_csv}")

    # Load metrics
    logger.info("Loading metrics")
    rouge = load("rouge")
    bleu = load("sacrebleu")
    bertscore = load("bertscore")
    comet = load("comet")
    chrf = load("chrf")

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
        chrf,
        only_service=args.service_name
    )

    logger.info("Evaluation complete.")
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Evaluation completed in {elapsed_time:.2f} seconds.")
    print(f"Evaluation completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()