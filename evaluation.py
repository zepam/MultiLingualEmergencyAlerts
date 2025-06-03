# have this at the top to supress warnings from the imports
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from evaluate import load
import pandas as pd
import argparse
import json
from tqdm import tqdm
import time
import re


def evaluate_generated_texts(generated_path, reference_path, output_csv=None, rouge=None, bleu=None, bertscore=None, comet=None):
    with open(reference_path, "r", encoding="utf-8") as f:
        reference_data = json.load(f)

    with open(generated_path, "r", encoding="utf-8") as f:
        prediction_data = json.load(f)
    
    results = []

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
                if language == "chinese_traditional":
                    selected_tokenizer = "zh"
                else:
                    selected_tokenizer = "13a"
                for disaster, gold_standards in values.items():
                    if (
                        service in prediction_data
                        and language in prediction_data[service]
                        and disaster in prediction_data[service][language]
                    ):
                        relevant_prompts = prediction_data[service][language][disaster]
                        if isinstance(relevant_prompts, dict):
                            for prompt, predictions in relevant_prompts.items():
                                if not predictions:
                                    continue
                                total_predictions = len(predictions)
                                duplicated_gold_standards = [gold_standards["reference"]] * total_predictions

                                try:
                                    if language == "english":
                                        comet_score = "N/A"
                                    else:
                                        comet_score = comet.compute(predictions=predictions, references=duplicated_gold_standards, sources=[gold_standards["source"]] * total_predictions)["mean_score"]
                                
                                    id_response = f"{language}:{service}:{disaster}:{prompt}"
                                    result = {
                                        "SERVICE": service,
                                        "LANGUAGE": language,
                                        "DISASTER": disaster,
                                        "PROMPT": prompt,
                                        "ROUGE-1": rouge.compute(predictions=predictions, references=duplicated_gold_standards)["rouge1"],
                                        "ROUGE-2": rouge.compute(predictions=predictions, references=duplicated_gold_standards)["rouge2"],
                                        "ROUGE-L": rouge.compute(predictions=predictions, references=duplicated_gold_standards)["rougeL"],
                                        "BLEU": bleu.compute(predictions=predictions, references=duplicated_gold_standards, tokenize=selected_tokenizer)["score"],
                                        "BERTScore_P": bertscore.compute(predictions=predictions, references=duplicated_gold_standards, lang="en")["precision"][0],
                                        "BERTScore_R": bertscore.compute(predictions=predictions, references=duplicated_gold_standards, lang="en")["recall"][0],
                                        "BERTScore_F1": bertscore.compute(predictions=predictions, references=duplicated_gold_standards, lang="en")["f1"][0],
                                        "COMET": comet_score
                                    }
                                    results.append(result)
                                except Exception as e:
                                    print(f"[Error on line {id_response}] {e}")
                                    continue
                                pbar.update(1)
                        # google translate
                        elif isinstance(relevant_prompts, list):
                            # If relevant_prompts is a list, we assume it's a single prediction
                            predictions = relevant_prompts
                            if predictions:

                                # google translate tranlates everything directly, even our standard variables. Let's parse out everything within square brackets
                                # to not penalize for that
                                formatted_predictions = []
                                for prediction in predictions:
                                    formatted_predictions.append(re.sub(r'\[.*?\]', '', prediction))

                                total_predictions = len(predictions)
                                duplicated_gold_standards = [re.sub(r'\[.*?\]', '', gold_standards["reference"])] * len(predictions)

                                try:
                                    if language == "english":
                                        comet_score = "N/A"
                                    else:
                                        comet_score = comet.compute(predictions=formatted_predictions, references=duplicated_gold_standards, sources=[gold_standards["source"]] * total_predictions)["mean_score"]
                                
                                    id_response = f"{language}:{service}:{disaster}"
                                    result = {
                                        "SERVICE": service,
                                        "LANGUAGE": language,
                                        "DISASTER": disaster,
                                        "PROMPT": "N/A",  # No specific prompt in this case
                                        "ROUGE-1": rouge.compute(predictions=formatted_predictions, references=duplicated_gold_standards)["rouge1"],
                                        "ROUGE-2": rouge.compute(predictions=formatted_predictions, references=duplicated_gold_standards)["rouge2"],
                                        "ROUGE-L": rouge.compute(predictions=formatted_predictions, references=duplicated_gold_standards)["rougeL"],
                                        "BLEU": bleu.compute(predictions=formatted_predictions, references=duplicated_gold_standards, tokenize=selected_tokenizer)["score"],
                                        "BERTScore_P": bertscore.compute(predictions=formatted_predictions, references=duplicated_gold_standards, lang="en")["precision"][0],
                                        "BERTScore_R": bertscore.compute(predictions=formatted_predictions, references=duplicated_gold_standards, lang="en")["recall"][0],
                                        "BERTScore_F1": bertscore.compute(predictions=formatted_predictions, references=duplicated_gold_standards, lang="en")["f1"][0],
                                        "COMET": comet_score
                                    }
                                    results.append(result)
                                except Exception as e:
                                    print(f"[Error on line {id_response}] {e}")
                                    continue
                                pbar.update(1)
    
    df = pd.DataFrame(results)

    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Results saved to: {output_csv}")

    return df

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description="Evaluate generated texts against reference texts")
    parser.add_argument("generated_path", help="Path generated text file")
    parser.add_argument("reference_path", help="Path reference text file")
    parser.add_argument("--output_csv", help="Path to output CSV file", default=None)
    args = parser.parse_args()

    # Load metrics
    rouge = load("rouge")
    bleu = load("sacrebleu")
    bertscore = load("bertscore")
    comet = load("comet")

    df = evaluate_generated_texts(
        args.generated_path,
        args.reference_path,
        args.output_csv,
        rouge,
        bleu,
        bertscore,
        comet
    )

    # Print the DataFrame
    print(df)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Evaluation completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()


    """
    python evaluation.py output_file.json evaluation_gold_standards.json --output_csv results.csv

    """