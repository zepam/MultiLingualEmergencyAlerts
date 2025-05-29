# have this at the top to supress warnings from the imports
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import textstat
from evaluate import load
import pandas as pd
import argparse
import json
from tqdm import tqdm


def evaluate_generated_texts(generated_path, reference_path, output_csv=None, rouge=None, bleu=None, bertscore=None, meteor=None):
    with open(reference_path, "r", encoding="utf-8") as f:
        reference_data = json.load(f)

    with open(generated_path, "r", encoding="utf-8") as f:
        prediction_data = json.load(f)
    
    # insert any preprocessing of prediction_data here

    results = []

    # Count total number of iterations for progress bar
    total = 0
    for service in prediction_data:
        for key, values in reference_data.items():
            for disaster, gold_standard in values.items():
                if (
                    service in prediction_data
                    and key in prediction_data[service]
                    and disaster in prediction_data[service][key]
                ):
                    relevant_prompts = prediction_data[service][key][disaster]
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
            for key, values in reference_data.items():
                for disaster, gold_standard in values.items():
                    if (
                        service in prediction_data
                        and key in prediction_data[service]
                        and disaster in prediction_data[service][key]
                    ):
                        relevant_prompts = prediction_data[service][key][disaster]
                        if isinstance(relevant_prompts, dict):
                            for prompt, predictions in relevant_prompts.items():
                                if not predictions:
                                    continue
                                total_predictions = len(predictions)
                                duplicated_gold_standards = [gold_standard] * total_predictions
                                try:
                                    id = f"{key}:{service}:{disaster}:{prompt}"
                                    result = {
                                        "SERVICE": service,
                                        "LANGUAGE": key,
                                        "DISASTER": disaster,
                                        "PROMPT": prompt,
                                        "ROUGE-1": rouge.compute(predictions=predictions, references=duplicated_gold_standards)["rouge1"],
                                        "ROUGE-2": rouge.compute(predictions=predictions, references=duplicated_gold_standards)["rouge2"],
                                        "ROUGE-L": rouge.compute(predictions=predictions, references=duplicated_gold_standards)["rougeL"],
                                        "BLEU": bleu.compute(predictions=predictions, references=duplicated_gold_standards)["score"],
                                        "BERTScore_P": bertscore.compute(predictions=predictions, references=duplicated_gold_standards, lang="en")["precision"][0],
                                        "BERTScore_R": bertscore.compute(predictions=predictions, references=duplicated_gold_standards, lang="en")["recall"][0],
                                        "BERTScore_F1": bertscore.compute(predictions=predictions, references=duplicated_gold_standards, lang="en")["f1"][0],
                                        "METEOR": meteor.compute(predictions=predictions, references=duplicated_gold_standards)["meteor"],
                                        #"FKGL": textstat.flesch_kincaid_grade(predictions),
                                        #"DCRS": textstat.dale_chall_readability_score(predictions),
                                        #"CLI": textstat.coleman_liau_index(predictions)
                                    }
                                    results.append(result)
                                except Exception as e:
                                    print(f"[Error on line {id}] {e}")
                                    continue
                                pbar.update(1)
    
    df = pd.DataFrame(results)

    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Results saved to: {output_csv}")

    return df

def main():
    parser = argparse.ArgumentParser(description="Evaluate generated texts against reference texts")
    parser.add_argument("generated_path", help="Path generated text file")
    parser.add_argument("reference_path", help="Path reference text file")
    parser.add_argument("--output_csv", help="Path to output CSV file", default=None)
    args = parser.parse_args()

    # Load metrics
    rouge = load("rouge")
    bleu = load("sacrebleu")
    bertscore = load("bertscore")
    meteor = load("meteor")

    df = evaluate_generated_texts(
        args.generated_path,
        args.reference_path,
        args.output_csv,
        rouge,
        bleu,
        bertscore,
        meteor
    )

    # Print the DataFrame
    print(df)

if __name__ == "__main__":
    main()


    """
    python evaluation.py output_file.json test_reference_text.txt --output_csv results.csv

    """