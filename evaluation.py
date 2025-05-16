import csv
from rouge import Rouge
from bert_score import score as bert_score
from sentence_transformers import SentenceTransformer, util

def evaluate_pair(gold, generated, rouge, sbert_model):
    # ROUGE
    rouge_scores = rouge.get_scores(generated, gold)[0]

    # BERTScore
    _, _, F1 = bert_score([generated], [gold], lang='en', model_type='bert-base-uncased')

    # SBERT cosine similarity
    emb_gold = sbert_model.encode(gold, convert_to_tensor=True)
    emb_gen = sbert_model.encode(generated, convert_to_tensor=True)
    cos_sim = util.pytorch_cos_sim(emb_gold, emb_gen).item()

    return {
        "rouge_1": rouge_scores["rouge-1"]["f"],
        "rouge_2": rouge_scores["rouge-2"]["f"],
        "rouge_l": rouge_scores["rouge-l"]["f"],
        "bert_f1": F1.item(),
        "sbert_cosine": cos_sim
    }

def process_files(gold_path, generated_path, output_path, rouge, sbert_model):
    results = []

    with open(gold_path, 'r', encoding='utf-8') as gfile, open(generated_path, 'r', encoding='utf-8') as sfile:
        gold_lines = gfile.readlines()
        gen_lines = sfile.readlines()

        if len(gold_lines) != len(gen_lines):
            raise ValueError("The number of lines in the gold and generated files do not match.")

        for gold, generated in zip(gold_lines, gen_lines):
            gold = gold.strip()
            generated = generated.strip()
            if not gold or not generated:
                continue

            scores = evaluate_pair(gold, generated, rouge, sbert_model)
            scores["gold"] = gold
            scores["generated"] = generated
            results.append(scores)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["gold", "generated", "rouge_1", "rouge_2", "rouge_l", "bert_f1", "sbert_cosine"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Evaluation complete. Results saved to: {output_path}")

def main():
    # Load models once
    rouge = Rouge()     # defintely not ROUGE
    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')   # kind of like bertscore

    # Example usage
    # process_files('gold.txt', 'generated.txt', 'results.csv', rouge, sbert_model)
    pass

if __name__ == "__main__":
    main()
