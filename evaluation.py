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

Dependencies: evaluate, pandas, tqdm, argparse, json, re, time, sacrebleu

Example:
    python evaluation.py output_file.json evaluation_gold_standards.json --output_csv results.csv

Functions:
    - evaluate_generated_texts: Evaluates generated texts against references using multiple metrics.
    - main: Parses arguments, loads metrics, runs evaluation, and prints/saves results.
    - tokenizer_lambda: defines a lambda that can return and call a tokenizer for a given text
"""

# have this at the top to supress warnings from the imports
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from evaluate import load
from sacrebleu.tokenizers.tokenizer_spm import Flores101Tokenizer
from sacrebleu.tokenizers.tokenizer_intl import TokenizerV14International
from sacrebleu.tokenizers.tokenizer_zh import TokenizerZh

import pandas as pd
import argparse
import json
from tqdm import tqdm
import time
import re

BATCH_SIZE = 100  # Set batch size to 1 to mostly avoid memory issues

class EvaluationTokenizer:
    def set_tokenizer_function(self, language):
        tokenizer = None
        match language:
            case "chinese_traditional":
                tokenizer = TokenizerZh()
            case "arabic", "vietnamese":
                tokenizer = Flores101Tokenizer()
            case _: # spanish, haitian creole
                tokenizer = TokenizerV14International()
        return tokenizer

    def __init__(self, language):
        self.tokenizer_function = self.set_tokenizer_function(language)    
    
    def tokenize(self, text):
        return self.tokenizer_function(text)

# used for ROUGE
def tokenizer_lambda(language):
    return lambda x: EvaluationTokenizer(language).tokenize(x)

def evaluate_generated_texts(
    generated_path,
    reference_path,
    output_csv=None,
    rouge=None,
    bleu=None,
    bertscore=None,
    comet=None,
    use_bertscore=True,
    use_comet=True
):
    with open(reference_path, "r", encoding="utf-8") as f:
        reference_data = json.load(f)

    with open(generated_path, "r", encoding="utf-8") as f:
        prediction_data = json.load(f)
    
    # Write results to disk incrementally to avoid memory issues
    import csv
    import os
    results = []
    temp_csv_path = None
    if output_csv:
        temp_csv_path = output_csv + ".tmp"
        # Write header if file does not exist
        if not os.path.exists(temp_csv_path):
            with open(temp_csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "SERVICE", "LANGUAGE", "DISASTER", "PROMPT",
                    "ROUGE-1", "ROUGE-2", "ROUGE-L", "BLEU",
                    "BERTScore_P", "BERTScore_R", "BERTScore_F1", "COMET"
                ])

    # Count total number of iterations for progress bar
    total = 0
    for service in prediction_data:
        for language, values in reference_data.items():
            for disaster, gold_standard in values.items():
                if (
                    service in prediction_data
                    and language in prediction_data[service]
                    and disaster in prediction_data[service][language]
                ):
                    relevant_prompts = prediction_data[service][language][disaster]
                    if isinstance(relevant_prompts, dict):
                        total += len(relevant_prompts)

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
            for language, values in reference_data.items():
                # Bleu doesn't take a tokenizer directly but rather a string matching a tokenizer
                if language == "chinese_traditional":
                    tokenizer_string = "zh"
                elif language == "arabic" or language == "vietnamese":
                    tokenizer_string = "flores101"
                else: # spanish, haitian creole
                    tokenizer_string = "intl"

                evaluation_tokenizer = tokenizer_lambda(language)

                # bertscore takes a language code indicating the language being passed in
                language_code = None
                match language:
                    case "chinese_traditional":
                        language_code = "zh"
                    case "arabic":
                        language_code = "ar"
                    case "vietnamese":
                        language_code = "vi"
                    case "haitian_creole":
                        language_code = "ht"
                    case "spanish":
                        language_code = "es"

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
                                    continue
                                total_predictions = len(predictions)

                                # we have 5 predictions and one gold standard. Just make an array of the same gold standard 5 times
                                duplicated_gold_standards = [gold_standards["reference"]] * total_predictions

                                try:
                                    id_response = f"{language}:{service}:{disaster}:{prompt}"
                                    # Batch process predictions in chunks of 100
                                    batch_size = BATCH_SIZE
                                    for batch_start in range(0, len(predictions), batch_size):
                                        batch_end = min(batch_start + batch_size, len(predictions))
                                        batch_predictions = predictions[batch_start:batch_end]
                                        batch_references = duplicated_gold_standards[batch_start:batch_end]
                                        batch_sources = [gold_standards["source"]] * len(batch_predictions)
                                        # Compute metrics for the batch
                                        rouge_result = rouge.compute(predictions=batch_predictions, references=batch_references, tokenizer=evaluation_tokenizer)
                                        import gc; gc.collect()
                                        bertscore_result = None
                                        comet_result = None
                                        if use_bertscore:
                                            bertscore_result = bertscore.compute(predictions=batch_predictions, references=batch_references, lang=language_code)
                                            gc.collect()
                                        bleu_result = bleu.compute(predictions=batch_predictions, references=batch_references, tokenize=tokenizer_string)
                                        gc.collect()
                                        if use_comet:
                                            comet_result = comet.compute(predictions=batch_predictions, references=batch_references, sources=batch_sources)
                                            gc.collect()
                                        for i in range(len(batch_predictions)):
                                            result = {
                                                "SERVICE": service,
                                                "LANGUAGE": language,
                                                "DISASTER": disaster,
                                                "PROMPT": prompt,
                                                "ROUGE-1": rouge_result["rouge1"][i] if isinstance(rouge_result["rouge1"], list) else rouge_result["rouge1"],
                                                "ROUGE-2": rouge_result["rouge2"][i] if isinstance(rouge_result["rouge2"], list) else rouge_result["rouge2"],
                                                "ROUGE-L": rouge_result["rougeL"][i] if isinstance(rouge_result["rougeL"], list) else rouge_result["rougeL"],
                                                "BLEU": bleu_result["score"][i] if isinstance(bleu_result["score"], list) else bleu_result["score"],
                                            }
                                            if use_bertscore and bertscore_result is not None:
                                                result["BERTScore_P"] = bertscore_result["precision"][i]
                                                result["BERTScore_R"] = bertscore_result["recall"][i]
                                                result["BERTScore_F1"] = bertscore_result["f1"][i]
                                            else:
                                                result["BERTScore_P"] = None
                                                result["BERTScore_R"] = None
                                                result["BERTScore_F1"] = None
                                            if use_comet and comet_result is not None:
                                                result["COMET"] = comet_result["mean_score"][i] if isinstance(comet_result["mean_score"], list) else comet_result["mean_score"]
                                            else:
                                                result["COMET"] = None
                                            if output_csv:
                                                # Write result immediately to disk
                                                with open(temp_csv_path, "a", encoding="utf-8", newline="") as f:
                                                    writer = csv.writer(f)
                                                    writer.writerow([
                                                        result["SERVICE"], result["LANGUAGE"], result["DISASTER"], result["PROMPT"],
                                                        result["ROUGE-1"], result["ROUGE-2"], result["ROUGE-L"], result["BLEU"],
                                                        result["BERTScore_P"], result["BERTScore_R"], result["BERTScore_F1"], result["COMET"]
                                                    ])
                                            else:
                                                results.append(result)
                                            pbar.update(1)
                                        # Explicitly free memory after each batch
                                        del rouge_result, bertscore_result, bleu_result, comet_result, batch_predictions, batch_references, batch_sources
                                        gc.collect()
                                except Exception as e:
                                    print(f"[Error on line {id_response}] {e}")
                                    continue
                        # google translate
                        elif isinstance(relevant_prompts, list):
                            # If relevant_prompts is a list, we assume it's a single prediction
                            predictions = relevant_prompts
                            if predictions:

                                # google translate tranlates everything directly, even our standard variables. Let's parse out everything within square brackets to not penalize for that
                                formatted_predictions = []
                                for prediction in predictions:
                                    formatted_predictions.append(re.sub(r'\[.*?\]', '', prediction))

                                total_predictions = len(predictions)
                                # apply the same treatment to the gold standards
                                duplicated_gold_standards = [re.sub(r'\[.*?\]', '', gold_standards["reference"])] * len(predictions)

                                try:        
                                    id_response = f"{language}:{service}:{disaster}"
                                    # Batch process predictions in chunks of 100
                                    batch_size = BATCH_SIZE
                                    for batch_start in range(0, len(predictions), batch_size):
                                        batch_end = min(batch_start + batch_size, len(predictions))
                                        batch_predictions = predictions[batch_start:batch_end]
                                        batch_references = duplicated_gold_standards[batch_start:batch_end]
                                        batch_sources = [gold_standards["source"]] * len(batch_predictions)
                                        # Compute metrics for the batch
                                        rouge_result = rouge.compute(predictions=batch_predictions, references=batch_references, tokenizer=evaluation_tokenizer)
                                        import gc; gc.collect()
                                        bertscore_result = None
                                        comet_result = None
                                        if use_bertscore:
                                            bertscore_result = bertscore.compute(predictions=batch_predictions, references=batch_references, lang=language_code)
                                            gc.collect()
                                        bleu_result = bleu.compute(predictions=batch_predictions, references=batch_references, tokenize=tokenizer_string)
                                        gc.collect()
                                        if use_comet:
                                            comet_result = comet.compute(predictions=batch_predictions, references=batch_references, sources=batch_sources)
                                            gc.collect()
                                        for i in range(len(batch_predictions)):
                                            result = {
                                                "SERVICE": service,
                                                "LANGUAGE": language,
                                                "DISASTER": disaster,
                                                "PROMPT": "N/A",  # No specific prompt in this case
                                                "ROUGE-1": rouge_result["rouge1"][i] if isinstance(rouge_result["rouge1"], list) else rouge_result["rouge1"],
                                                "ROUGE-2": rouge_result["rouge2"][i] if isinstance(rouge_result["rouge2"], list) else rouge_result["rouge2"],
                                                "ROUGE-L": rouge_result["rougeL"][i] if isinstance(rouge_result["rougeL"], list) else rouge_result["rougeL"],
                                                "BLEU": bleu_result["score"][i] if isinstance(bleu_result["score"], list) else bleu_result["score"],
                                            }
                                            if use_bertscore and bertscore_result is not None:
                                                result["BERTScore_P"] = bertscore_result["precision"][i]
                                                result["BERTScore_R"] = bertscore_result["recall"][i]
                                                result["BERTScore_F1"] = bertscore_result["f1"][i]
                                            else:
                                                result["BERTScore_P"] = None
                                                result["BERTScore_R"] = None
                                                result["BERTScore_F1"] = None
                                            if use_comet and comet_result is not None:
                                                result["COMET"] = comet_result["mean_score"][i] if isinstance(comet_result["mean_score"], list) else comet_result["mean_score"]
                                            else:
                                                result["COMET"] = None
                                            if output_csv:
                                                # Write result immediately to disk
                                                with open(temp_csv_path, "a", encoding="utf-8", newline="") as f:
                                                    writer = csv.writer(f)
                                                    writer.writerow([
                                                        result["SERVICE"], result["LANGUAGE"], result["DISASTER"], result["PROMPT"],
                                                        result["ROUGE-1"], result["ROUGE-2"], result["ROUGE-L"], result["BLEU"],
                                                        result["BERTScore_P"], result["BERTScore_R"], result["BERTScore_F1"], result["COMET"]
                                                    ])
                                            else:
                                                results.append(result)
                                            pbar.update(1)
                                        # Explicitly free memory after each batch
                                        del rouge_result, bertscore_result, bleu_result, comet_result, batch_predictions, batch_references, batch_sources
                                        gc.collect()
                                except Exception as e:
                                    print(f"[Error on line {id_response}] {e}")
                                    continue
    
    if output_csv:
        # If results were written incrementally, read them back in for return
        df = pd.read_csv(temp_csv_path)
        # Move temp file to final output
        import shutil
        shutil.move(temp_csv_path, output_csv)
        print(f"Results saved to: {output_csv}")
    else:
        df = pd.DataFrame(results)

    return df

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description="Evaluate generated texts against reference texts")
    parser.add_argument("generated_path", help="Path generated text file")
    parser.add_argument("reference_path", help="Path reference text file")
    parser.add_argument("--output_csv", help="Path to output CSV file", default=None)
    parser.add_argument("--no_bertscore", action="store_true", help="Disable BERTScore metric")
    parser.add_argument("--no_comet", action="store_true", help="Disable COMET metric")
    args = parser.parse_args()

    # Load metrics
    rouge = load("rouge")
    bleu = load("sacrebleu")
    bertscore = None
    comet = None
    use_bertscore = not args.no_bertscore
    use_comet = not args.no_comet
    if use_bertscore:
        bertscore = load("bertscore")
    if use_comet:
        comet = load("comet")

    df = evaluate_generated_texts(
        args.generated_path,
        args.reference_path,
        args.output_csv,
        rouge,
        bleu,
        bertscore,
        comet,
        use_bertscore=use_bertscore,
        use_comet=use_comet
    )

    # Print the DataFrame
    print(df)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Evaluation completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()