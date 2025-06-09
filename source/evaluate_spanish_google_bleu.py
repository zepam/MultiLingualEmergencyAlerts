import json
from evaluate import load

# List of all available sacrebleu tokenizers
bleu_tokenizers = [
    "none",         # No tokenization
    "intl",         # International
    "zh",           # Chinese, same results as 13a
    "flores101",    # Flores101
    "char",         # Character
]

def get_spanish_google_translate_preds_refs(generated_path, reference_path):
    with open(generated_path, "r", encoding="utf-8") as f:
        prediction_data = json.load(f)
    with open(reference_path, "r", encoding="utf-8") as f:
        reference_data = json.load(f)

    # Dict: disaster -> (predictions, references)
    disaster_data = {}
    for disaster, gold in reference_data["spanish"].items():
        if (
            "google_translate" in prediction_data
            and "spanish" in prediction_data["google_translate"]
            and disaster in prediction_data["google_translate"]["spanish"]
        ):
            preds = prediction_data["google_translate"]["spanish"][disaster]
            preds = [remove_brackets(p) for p in preds]
            gold_ref = remove_brackets(gold["reference"])
            disaster_data[disaster] = (
                preds,
                [[gold_ref]] * len(preds)  # sacrebleu expects list of references per prediction
            )
    return disaster_data

def remove_brackets(text):
    import re
    return re.sub(r'\[.*?\]', '', text)

def main():
    generated_path = "output_file.json"
    reference_path = "evaluation_gold_standards.json"

    disaster_data = get_spanish_google_translate_preds_refs(generated_path, reference_path)
    bleu = load("sacrebleu")
    print("Evaluating spanish Google Translate results for all available BLEU tokenizers:")

    for tokenizer in bleu_tokenizers:
        print(f"\nTokenizer: {tokenizer}")
        # Overall BLEU
        all_predictions = []
        all_references = []
        for preds, refs in disaster_data.values():
            all_predictions.extend(preds)
            all_references.extend(refs)
        try:
            bleu_result = bleu.compute(predictions=all_predictions, references=all_references, tokenize=tokenizer)
            print(f"  Overall BLEU: {bleu_result['score']:.2f}")
        except Exception as e:
            print(f"  Overall BLEU: Error: {e}")

        # Per-disaster BLEU
        for disaster, (preds, refs) in disaster_data.items():
            try:
                bleu_result = bleu.compute(predictions=preds, references=refs, tokenize=tokenizer)
                print(f"    {disaster:20} BLEU: {bleu_result['score']:.2f}")
            except Exception as e:
                print(f"    {disaster:20} BLEU: Error: {e}")

if __name__ == "__main__":
    main()